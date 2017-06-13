from openalpr import Alpr
from PIL import Image

import zbar
import tornado.ioloop
import tornado.web
import tornado.options
tornado.options.parse_command_line()

import sys
from sys import argv
sys.path.append('/usr/local/lib/python2.7/site-packages')

import os
import io
import json
import logging

country_code = os.getenv('OCV_COUNTRY_CODE', "us")
top_n = os.getenv('OCV_TOP_N', "5")

print('Initialization params:')
print('country_code: ' + country_code)
print('top_n: ' + top_n)

# create an alpr
alpr = Alpr(country_code, "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
alpr.set_top_n(int(top_n))

# create a reader
scanner = zbar.ImageScanner()
scanner.parse_config('enable')

class AlprHandler(tornado.web.RequestHandler):
    def post(self):
        logging.info('Executing POST')
        
        #print(self.request.files)
        if 'image' not in self.request.files:
            self.finish('Image parameter not provided')

        fileinfo = self.request.files['image'][0]
        image_bytes = fileinfo['body']

        if len(image_bytes) <= 0:
            return False

        results = alpr.recognize_array(image_bytes)

        self.finish(json.dumps(results))

class QrHandler(tornado.web.RequestHandler):
    def post(self):
        logging.info('Executing POST')
        
        #print(self.request.files)
        if 'image' not in self.request.files:
            self.finish('Image parameter not provided')

        fileinfo = self.request.files['image'][0]
        image_bytes = fileinfo['body']

        if len(image_bytes) <= 0:
            return False

        pil = Image.open(io.BytesIO(image_bytes)).convert('L')
        width, height = pil.size

        # wrap image data
        raw = pil.tobytes()
        image = zbar.Image(width, height, 'Y800', raw)

        # scan the image for barcodes
        scanner.scan(image)

        results = {}
        
        for symbol in image:
            #print dir(symbol)
            
            results['type'] = symbol.type
            results['data'] = symbol.data
            results['location'] = symbol.location
            results['quality'] = symbol.quality
            results['count'] = symbol.count
            #results['components'] = symbol.components

        self.finish(json.dumps(results))

application = tornado.web.Application([
    (r"/alpr", AlprHandler),
    (r"/qr", QrHandler)
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
