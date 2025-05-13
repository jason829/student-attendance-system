"""
This is needed to extract the face embeddings from images in the dataset.
More varied images of the same person will improve accuracy.

"""

from imutils import paths
import face_recognition
import pickle
import cv2
import os

# Image path
imagePaths = list(paths.list_images('people'))
knownEncodings = []
knownNames = []

# loop over all images
for (i, imagePath) in enumerate(imagePaths):
    name = imagePath.split(os.path.sep)[-2]
    
    image = cv2.imread(imagePath)
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Get face location 
    boxes = face_recognition.face_locations(rgb,model='hog')
    
    # Face encoding
    encodings = face_recognition.face_encodings(rgb, boxes)
    for encoding in encodings:
        knownEncodings.append(encoding)
        knownNames.append(name)

data = {"encodings": knownEncodings, "names": knownNames}
f = open("face_enc", "wb")
f.write(pickle.dumps(data))
f.close()