from openalpr import Alpr
from imagenet import ImagenetModel

import zbar
import os
import logging

logger = logging.getLogger(__name__)

country_code = os.getenv('OCV_COUNTRY_CODE', "us")
top_n = os.getenv('OCV_TOP_N', "5")
mxnet_model = os.getenv('OCV_MXNET_MODEL', "squeezenet_v1.1")

logger.info('Initialization params:')
logger.info('country_code: ' + country_code)
logger.info('top_n: ' + top_n)
logger.info('mxnet_model: ' + mxnet_model)

# openface vars
pickleLocation = '/root/data/data.pickle'
dataLocation = '/root/data/data.json'

# create an alpr
alpr = Alpr(country_code, "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
alpr.set_top_n(int(top_n))

# create a reader
scanner = zbar.ImageScanner()
scanner.parse_config('enable')

# create the imagenet instance
mxnet = ImagenetModel(synset_path='synset.txt', network_prefix=mxnet_model, label_names=['prob_label'])