import os
import sys
import pickle
import argparse
import subprocess
import cv2
import numpy as np
import pandas as pd
from PIL import Image

from face_indetification import FACE_RECOGNIZER
from face_detection import FaceDetector

parser = argparse.ArgumentParser()
parser.add_argument('-t', '--detection_type', default='base', choices=['base', 'caffe'])
args = parser.parse_args()
detection_type = args.detection_type
detector = FaceDetector(detection_type)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(PROJECT_DIR, 'images')
y_ids, current_id = {}, 0
X, y = [], []


def base_create_face_recognizer(data, labels, path):
    FACE_RECOGNIZER.train(data, np.array(labels))
    FACE_RECOGNIZER.save(path)


for root, dirs, files in os.walk(IMG_DIR):
    for file in files:
        if file.endswith("jpg") or file.endswith('png'):
            file_path = os.path.join(root, file)
            label = os.path.basename(root).replace("_", " ").lower()
            # print(file_path)

            # add new labels as int
            if label not in y_ids:
                y_ids[label] = current_id
                current_id += 1
            y_id = y_ids[label]

            # open image from path in black/white mode
            img_array = np.array(Image.open(file_path).convert(mode="L"), dtype="uint8")
            try:
                curr_roi, curr_y = detector.face_detection(img_array, file_path, y_id)
                X.append(curr_roi)
                y.append(curr_y)
            except TypeError:
                print(f"Can't find any face on path: {file_path}")

with open("labels.pickle", 'wb') as f:
    pickle.dump(y_ids, f)

base_create_face_recognizer(data=X, labels=y, path="recognize_trained.yml")

training_data = pd.DataFrame(zip(y, X), columns=['label', 'data'])
print(training_data)
training_data.to_json('data_from_images.json')

# TODO: face recognize based on DL
