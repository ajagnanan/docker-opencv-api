from openalpr import Alpr
from imagenet import ImagenetModel

import zbar
import dlib
import os
import logging

logger = logging.getLogger(__name__)

country_code = os.getenv('OCV_COUNTRY_CODE', "us")
top_n = os.getenv('OCV_TOP_N', "5")

logger.info('Initialization params:')
logger.info('country_code: ' + country_code)
logger.info('top_n: ' + top_n)

# Initialization of variables to be treated as singletons 

# create an alpr
alpr = Alpr(country_code, "/etc/openalpr/openalpr.conf", "/usr/share/openalpr/runtime_data")
alpr.set_top_n(int(top_n))

# create a reader
scanner = zbar.ImageScanner()
scanner.parse_config('enable')

# create the imagenet instance
squeezenet = ImagenetModel(synset_path='synset.txt', network_prefix='squeezenet_v1.1', label_names=['prob_label'])
vgg19 = ImagenetModel(synset_path='synset.txt', network_prefix='vgg19', label_names=['prob_label'])

# create dlib detector
# http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2 shape_predictor_68_face_landmarks.dat
# http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2 dlib_face_recognition_resnet_model_v1.dat

predictor_path = "./shape_predictor_68_face_landmarks.dat"
face_rec_model_path = "./dlib_face_recognition_resnet_model_v1.dat"

dlibFaceDetector = dlib.get_frontal_face_detector()
dlibShapePredictor = dlib.shape_predictor(predictor_path)
dlibFaceRecognitionModel = dlib.face_recognition_model_v1(face_rec_model_path)