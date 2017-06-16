from openalpr import Alpr

import zbar
import os
import logging

logger = logging.getLogger(__name__)

country_code = os.getenv('OCV_COUNTRY_CODE', "us")
top_n = os.getenv('OCV_TOP_N', "5")

logger.info('Initialization params:')
logger.info('country_code: ' + country_code)
logger.info('top_n: ' + top_n)

# create an alpr
alpr = Alpr(country_code, "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
alpr.set_top_n(int(top_n))

# create a reader
scanner = zbar.ImageScanner()
scanner.parse_config('enable')