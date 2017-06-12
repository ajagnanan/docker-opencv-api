from openalpr import Alpr

import os
import json
import tornado.ioloop
import tornado.web

country_code = os.getenv('ALPR_COUNTRY_CODE', "us")
top_n = os.getenv('ALPR_TOP_N', "5")

print('Initialization params:')
print('country_code: ' + country_code)
print('top_n: ' + top_n)

alpr = Alpr(country_code, "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
alpr.set_top_n(int(top_n))

class MainHandler(tornado.web.RequestHandler):
    def post(self):
        print('Printing request files')
        print(self.request.files)
        if 'image' not in self.request.files:
            self.finish('Image parameter not provided')

        fileinfo = self.request.files['image'][0]
        jpeg_bytes = fileinfo['body']

        if len(jpeg_bytes) <= 0:
            return False

        results = alpr.recognize_array(jpeg_bytes)

        self.finish(json.dumps(results))

application = tornado.web.Application([
    (r"/alpr", MainHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()
