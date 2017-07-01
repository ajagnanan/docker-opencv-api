# ImageNet model 

import mxnet as mx
import numpy as np

import cv2, os, urllib2, argparse, time
from collections import namedtuple

import logging

logger = logging.getLogger(__name__)

Batch = namedtuple('Batch', ['data'])

class ImagenetModel(object):

    """
    Loads a pre-trained model locally or from an external URL and returns an MXNet graph that is ready for prediction
    """
    def __init__(self, synset_path, network_prefix, params_url=None, symbol_url=None, synset_url=None, context=mx.cpu(), label_names=['prob_label'], input_shapes=[('data', (1,3,224,224))]):

        # Download the symbol set and network if URLs are provided
        if params_url is not None:
            print "fetching params from "+params_url
            fetched_file = urllib2.urlopen(params_url)
            with open(network_prefix+"-0000.params",'wb') as output:
                output.write(fetched_file.read())

        if symbol_url is not None:
            print "fetching symbols from "+symbol_url
            fetched_file = urllib2.urlopen(symbol_url)
            with open(network_prefix+"-symbol.json",'wb') as output:
                output.write(fetched_file.read())

        if synset_url is not None:
            print "fetching synset from "+synset_url
            fetched_file = urllib2.urlopen(synset_url)
            with open(synset_path,'wb') as output:
                output.write(fetched_file.read())

        # Load the symbols for the networks
        with open(synset_path, 'r') as f:
            self.synsets = [l.rstrip() for l in f]

        # Load the network parameters from default epoch 0
        sym, arg_params, aux_params = mx.model.load_checkpoint(network_prefix, 0)

        # Load the network into an MXNet module and bind the corresponding parameters
        self.mod = mx.mod.Module(symbol=sym, label_names=label_names, context=context)
        self.mod.bind(for_training=False, data_shapes= input_shapes)
        self.mod.set_params(arg_params, aux_params)
        self.camera = None

    """
    Takes in an image, reshapes it, and runs it through the loaded MXNet graph for inference returning the N top labels from the softmax
    """
    def predict_from_file(self, filename, reshape=(224, 224), N=5):

        response = {}

        # Switch RGB to BGR format (which ImageNet networks take)
        image_bytes = filename #cv2.imread(filename)
        if len(image_bytes) <= 0:
            error = {}
            error['error'] = 'Unable to decode posted image!'
            return error

        img = cv2.cvtColor(image_bytes, cv2.COLOR_BGR2RGB)
        if img is None:
            return response

        # Resize image to fit network input
        img = cv2.resize(img, reshape)
        img = np.swapaxes(img, 0, 2)
        img = np.swapaxes(img, 1, 2)
        img = img[np.newaxis, :]

        # Run forward on the image
        self.mod.forward(Batch([mx.nd.array(img)]))
        prob = self.mod.get_outputs()[0].asnumpy()
        prob = np.squeeze(prob)

        # Extract the top N predictions from the softmax output
        results = []
        a = np.argsort(prob)[::-1]
        for i in a[0:N]:
            #print('probability=%f, class=%s' %(prob[i], self.synsets[i]))
            item = {}
            item['probability'] = str(prob[i])
            item['class'] = str(self.synsets[i])
            results.append(item)

        response['results'] = results
        return response

    """
    Captures an image from the PiCamera, then sends it for prediction
    """
    def predict_from_cam(self, capfile='cap.jpg', reshape=(224, 224), N=5):
        if self.camera is None:
            self.camera = picamera.PiCamera()

        # Show quick preview of what's being captured
        self.camera.start_preview()
        time.sleep(3)
        self.camera.capture(capfile)
        self.camera.stop_preview()

        return self.predict_from_file(capfile)


#if __name__ == "__main__":
    #parser = argparse.ArgumentParser(description="pull and load pre-trained resnet model to classify one image")
    #parser.add_argument('--img', type=str, default='cam', help='input image for classification, if this is cam it captures from the PiCamera')
    #parser.add_argument('--prefix', type=str, default='squeezenet_v1.1', help='the prefix of the pre-trained model')
    #parser.add_argument('--label-name', type=str, default='prob_label', help='the name of the last layer in the loaded network (usually softmax_label)')
    #parser.add_argument('--synset', type=str, default='synset.txt', help='the path of the synset for the model')
    #parser.add_argument('--params-url', type=str, default=None, help='the (optional) url to pull the network parameter file from')
    #parser.add_argument('--symbol-url', type=str, default=None, help='the (optional) url to pull the network symbol JSON from')
    #parser.add_argument('--synset-url', type=str, default=None, help='the (optional) url to pull the synset file from')
    #args = parser.parse_args()

    

    #python example.py --img 'people.jpg' --prefix 'squeezenet_v1.1' --synset 'synset.txt'
    
    #print "predicting on "+args.img
    #if args.img == "cam":
    #    print mod.predict_from_cam()
    #else:
    #    print mod.predict_from_file(args.img)