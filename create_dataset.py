import os
import pickle
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from skimage import io, color
from skimage.transform import resize
from PIL import Image

from face_indetification import CASCADE_CLF, FACE_RECOGNIZER, SIZE

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(PROJECT_DIR, 'images')
y_ids, current_id = {}, 0
X, y = [], []


def base_face_detection(img_array, label_id):
    # find faces on image
    faces = CASCADE_CLF.detectMultiScale(img_array, scaleFactor=1.5, minNeighbors=5)
    for (x1, y1, x2, y2) in faces:
        interest_region_gray = Image.fromarray(img_array[y1:y1 + y2, x1:x1 + x2], mode="L")
        interest_region_gray_resized = interest_region_gray.resize(SIZE, Image.ANTIALIAS)
        # interest_region_gray_resized.show()
        current_roi = np.array(interest_region_gray_resized, dtype="uint8")
        if current_roi:
            return current_roi, label_id


def base_create_face_recognizer(data, labels, path):
    FACE_RECOGNIZER.train(data, np.array(labels))
    FACE_RECOGNIZER.save(path)


for root, dirs, files in os.walk(IMG_DIR):
    for file in files:
        if file.endswith("jpg") or file.endswith('png'):
            file_path = os.path.join(root, file)
            label = os.path.basename(root).replace("_", " ").lower()
            print(file_path)

            # add new labels as int
            if label not in y_ids:
                y_ids[label] = current_id
                current_id += 1
            y_id = y_ids[label]

            # mono_img = color.rgb2gray(io.imread(file_path))
            # small_img = resize(mono_img, SIZE, anti_aliasing=False)
            # plt.imshow(small_img, cmap='gray')
            # plt.show()
            # print(small_img.shape)

            # open image from path in black/white mode
            gray_img = Image.open(file_path).convert(mode="L")
            gray_img_array = np.array(gray_img, dtype="uint8")
            curr_roi, curr_y = base_face_detection(img_array=gray_img_array, label_id=y_id)
            X.append(curr_roi)
            y.append(curr_y)

with open("labels.pickle", 'wb') as f:
    pickle.dump(y_ids, f)

base_create_face_recognizer(data=X, labels=y, path="recognize_trained.yml")

training_data = pd.DataFrame(zip(y, X), columns=['label', 'data'])
print(training_data)
training_data.to_json('data_from_images.json')

# TODO: face recognize based on DL
