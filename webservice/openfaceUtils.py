import cv2
import numpy as np
import os

import openface

import glob
import time
import pickle
import json

from multiprocessing import Pool, cpu_count
from threading import local

import logging

logger = logging.getLogger(__name__)

modelDir = os.path.join('/root/openface', 'models')
dlibModelDir = os.path.join(modelDir, 'dlib')
openfaceModelDir = os.path.join(modelDir, 'openface')

align = openface.AlignDlib(os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))
net = openface.TorchNeuralNet(os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'), 96)

def init():
    global align, net
    align = openface.AlignDlib(os.path.join(dlibModelDir, "shape_predictor_68_face_landmarks.dat"))
    net = openface.TorchNeuralNet(os.path.join(openfaceModelDir, 'nn4.small2.v1.t7'), 96)

def getRep(bgrImg, align=align, net=net):
    rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)
    bb = align.getLargestFaceBoundingBox(rgbImg)
    if bb is None:
        raise Exception("Unable to find a face")
    alignedFace = align.align(96, rgbImg, bb,
                              landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
    if alignedFace is None:
        raise Exception("Unable to align image")
    rep = net.forward(alignedFace)
    return rep 

def loadImageFromFile(imgPath):
    global align, net
    uid = os.path.split(os.path.split(imgPath)[0])[-1]
    bgrImg = cv2.imread(imgPath)
    if bgrImg is None:
        logger.info("Unable to load image: {}".format(imgPath))
        return
    try:
        rep = getRep(bgrImg, align, net)
    except Exception as e:
        logger.info('{} for {}'.format(e, uid))
        return
    return (uid, rep)

def generatePickle():
    PROCESSES = cpu_count() / 2 + 1
    p = Pool(processes=PROCESSES, initializer=init)
    g = glob.glob("/root/data/images/*/*")

    start = time.time()
    reps = p.imap_unordered(loadImageFromFile, g)

    rep_dict = {}

    count = 0
    successes = 0
    for r in reps:
        count += 1
        if count % 100 == 0:
            logger.info("{}s: {}/{} done".format(time.time() - start, count, len(g)))
        if r:
            successes += 1
            if r[0] in rep_dict:
                rep_dict[r[0]].append(r[1])
            else:
                rep_dict[r[0]] = [r[1]]

    logger.info("Loaded {}/{} refs, took {} seconds.".format(successes, len(g), time.time() - start))

    with open("/root/data/data.pickle", 'wb') as f:
        pickle.dump(rep_dict, f)

def face_distance(face_encodings, face_to_compare):
    """
    Given a list of face encodings, compare them to a known face encoding and get a euclidean distance
    for each comparison face. The distance tells you how similar the faces are.
    :param faces: List of face encodings to compare
    :param face_to_compare: A face encoding to compare against
    :return: A numpy ndarray with the distance for each face in the same order as the 'faces' array
    """
    if len(face_encodings) == 0:
        return np.empty((0))

    distance = np.linalg.norm(face_encodings - face_to_compare, axis=1)
    print distance
    return distance
    
def compare_faces(known_face_encodings, face_encoding_to_check, tolerance=0.6):
    """
    Compare a list of face encodings against a candidate encoding to see if they match.
    :param known_face_encodings: A list of known face encodings
    :param face_encoding_to_check: A single face encoding to compare against the list
    :param tolerance: How much distance between faces to consider it a match. Lower is more strict. 0.6 is typical best performance.
    :return: A list of True/False values indicating which known_face_encodings match the face encoding to check
    """
    return list(face_distance(known_face_encodings, face_encoding_to_check) <= tolerance)