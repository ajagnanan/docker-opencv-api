from PIL import Image

import cv2
import zbar
import numpy as np
np.set_printoptions(precision=2)

from bottle import *
BaseRequest.MEMFILE_MAX = 1e8

import sys
from sys import argv
sys.path.append('/usr/local/lib/python2.7/site-packages')

import io
import json
import logging

import utils
import config

logger = logging.getLogger(__name__)

# configure openface model
with open("/root/data/data.pickle") as f:
    start = time.time()
    reps = pickle.load(f)
    print("Loaded stored pickle, took {}".format(time.time() - start))

data_dict = {}

try:
    with open('/root/data/data.json') as f:
        data = json.load(f)

    if 'profiles' in data:
        for d in data['profiles']:
            if 'upi' in d:
                data_dict[d['upi']] = d
    else:
        data_dict = data
except Exception as e:
    print("Unable to load data.json: ", e)

# start endpoints

@get('/health')
def healthCheck():
    logger.info('Executing GET')
    
    results = {}
    results["status"] = "ok"

    response.content_type = 'application/json'
    return json.dumps(results)

@post('/lpr')
def lpr():
    logger.info('Executing POST')

    if request.files.get('image'):
        image_bytes = request.files.get('image').file.read()
    else:
        image_bytes = request.body.read()

    if len(image_bytes) <= 0:
        return {'error': 'Unable to decode posted image!'}

    results = config.alpr.recognize_array(image_bytes)
    
    response.content_type = 'application/json'
    return json.dumps(results)

@post('/qrr')
def qrr():
    logger.info('Executing POST')

    if request.files.get('image'):
        image_bytes = request.files.get('image').file.read()
    else:
        image_bytes = request.body.read()

    if len(image_bytes) <= 0:
        return {'error': 'Unable to decode posted image!'}

    pil = Image.open(io.BytesIO(image_bytes)).convert('L')
    width, height = pil.size

    # wrap image data
    raw = pil.tobytes()
    image = zbar.Image(width, height, 'Y800', raw)

    # scan the image for barcodes
    config.scanner.scan(image)

    results = {}
    
    for symbol in image:
        #print dir(symbol)
        
        results['type'] = str(symbol.type)
        results['data'] = symbol.data
        results['location'] = symbol.location
        results['quality'] = symbol.quality
        results['count'] = symbol.count
        #results['components'] = symbol.components

    response.content_type = 'application/json'
    return json.dumps(results)

@post('/ofr')
def ofr():
    logger.info('Executing POST')

    if request.files.get('image'):
        image_bytes = request.files.get('image').file.read()
    else:
        image_bytes = request.body.read()

    img_array = np.asarray(bytearray(image_bytes), dtype=np.uint8)
    print("recieved image of size {}".format(len(img_array)))
    image_data = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if image_data is None:
        print("Unable to decode posted image!")
        response.status = 500
        return {'error': 'Unable to decode posted image!'}

    try:
        start = time.time()
        rep = utils.getRep(image_data)
        print("Got face representation in {} seconds".format(time.time() - start))
    except Exception as e:
        print("Error: {}".format(e))
        response.status = 500
        return {'error': str(e)}
    ids_to_compare = request.params.get('ids_to_compare', reps.keys())
    best = 4
    bestUid = "unknown"
    for i in ids_to_compare:
        if type(reps[i]) is not list:
            reps[i] = [reps[i]]
        for r in reps[i]:
            d = rep - r
            dot = np.dot(d,d)
            if dot < best:
                best = dot
                bestUid = i

    response.content_type = 'application/json'
    return {"uid": bestUid, "confidence": 1 - best/4, "data": data_dict.get(bestUid)}

@post('/odr')
def odr():
    logger.info('Executing POST')

    if request.files.get('image'):
        image_bytes = request.files.get('image').file.read()
    else:
        image_bytes = request.body.read()

    if len(image_bytes) <= 0:
        return {'error': 'Unable to decode posted image!'}

    img_array = np.asarray(bytearray(image_bytes), dtype=np.uint8)
    print("recieved image of size {}".format(len(img_array)))
    image_data = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    if image_data is None:
        print("Unable to decode posted image!")
        response.status = 500
        return {'error': 'Unable to decode posted image!'}

    results = {}
    mxnetModel = request.forms.get('model', default='squeezenet_v1.1')
    if mxnetModel == 'vgg19':
        results = config.vgg19.predict_from_file(image_data)
    else:
        mxnetModel = 'squeezenet_v1.1'
        results = config.squeezenet.predict_from_file(image_data)

    results['model'] = mxnetModel
    response.content_type = 'application/json'
    return json.dumps(results)

@get('/faces')
def faces_site():
    logger.info('Executing GET')

    return static_file("site/faces.html", ".")

@post('/faces/generate')
def faces_compare():
    logger.info('Executing POST')

    utils.generatePickle()

    results = {"status": "ok"}

    response.content_type = 'application/json'
    return json.dumps(results)

@get('/faces/<uid>')
def faces_get(uid):
    logger.info('Executing GET')

    f = glob.glob("/root/data/images/{}/*".format(uid))
    return static_file(f[0], '/')

# start server

port = int(os.environ.get('PORT', 8888))

if __name__ == "__main__":
    run(host='0.0.0.0', port=port, debug=True, server='gunicorn', workers=4)

app = default_app()