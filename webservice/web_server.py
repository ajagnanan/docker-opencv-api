from PIL import Image

import cv2
import zbar
import numpy as np
import pickle
np.set_printoptions(precision=2)

from bottle import *
BaseRequest.MEMFILE_MAX = 1e8

import sys
from sys import argv
sys.path.append('/usr/local/lib/python2.7/site-packages')

import io
import json
import logging

import openfaceUtils
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

    if len(image_bytes) <= 0:
        return {'error': 'Unable to decode posted image!'}

    img_array = np.asarray(bytearray(image_bytes), dtype=np.uint8)
    print("recieved image of size {}".format(len(img_array)))
    image_data = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    detectors = config.dlibFaceDetector(image_data, 1)
    logger.info('Number of faces detected: {}'.format(len(detectors)))
    
    dataPickle = pickle.loads(open('/root/data/data.pickle', 'r').read())

    results = {
        'faces': {}
    }
    # Now process each face we found.
    for k, d in enumerate(detectors):
        logger.info('Detection {}: Left: {} Top: {} Right: {} Bottom: {}'.format(k, d.left(), d.top(), d.right(), d.bottom()))
        results['faces'][k] = {
            'position': {
                'top': d.top(),
                'left': d.left(),
                'bottom': d.bottom(),
                'right': d.right()
            },
            'matches': {}
        }

        # Get the landmarks/parts for the face in box d.
        shape = config.dlibShapePredictor(image_data, d)
        # Compute the 128D vector that describes the face in img identified by
        # shape.  In general, if two face descriptor vectors have a Euclidean
        # distance between them less than 0.6 then they are from the same
        # person, otherwise they are from different people.  He we just print
        # the vector to the screen.
        faceDescriptor = config.dlibFaceRecognitionModel.compute_face_descriptor(image_data, shape)

        for name in dataPickle:
            matches = str(openfaceUtils.compare_faces(dataPickle[name], faceDescriptor))
            matched = False

            print(matches)
            for match in matches:
                if match == True:
                    matched = True
                    break
            
            results['faces'][k]['matches'][name] = {
                'matched': matched
            }
    
    #serialized = pickle.dumps(faceDescriptor, protocol=0)
    #print type(deserialized_a).__name__
    #results['descriptors'].append(str(faceDescriptor))
    # print type(deserialized_a).__name__
    # print(deserialized_a['rihanna'][0])

    response.content_type = 'application/json'
    return json.dumps(results)

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

@post('/faces/generate')
def faces_generate():
    logger.info('Executing POST')

    openfaceUtils.generatePickle()

    results = {"status": "ok"}

    response.content_type = 'application/json'
    return json.dumps(results)

# start server

port = int(os.environ.get('PORT', 8888))

if __name__ == "__main__":
    run(host='0.0.0.0', port=port, debug=True, server='gunicorn', workers=4)

app = default_app()