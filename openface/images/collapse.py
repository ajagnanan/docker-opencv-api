# Use this script to collapse a multi-level folder of images into one folder.

import fnmatch
import os
import shutil

folderName = 'unknown'
matches = []
for root, dirnames, filenames in os.walk(folderName):
    for filename in fnmatch.filter(filenames, '*.jpg'):
        matches.append(os.path.join(root, filename))

idx = 0        
for match in matches:
    print match
    shutil.move('./' + match, './' + folderName + '/' + str(idx) + '.jpg')
    idx = idx + 1