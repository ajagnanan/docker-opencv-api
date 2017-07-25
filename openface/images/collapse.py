import fnmatch
import os
import shutil

matches = []
for root, dirnames, filenames in os.walk('unknown'):
    for filename in fnmatch.filter(filenames, '*.jpg'):
        matches.append(os.path.join(root, filename))

idx = 0        
for match in matches:
    print match
    shutil.move('./' + match, './unknown/' + str(idx) + '.jpg')
    idx = idx + 1