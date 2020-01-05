import os
import pickle
import joblib
import argparse
import subprocess
import cv2
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

from keras.models import load_model

from face_detection import FaceDetector
from face_recognition import SuppVecMachinesRecognizer, BaseRecognizer
from face_embedding import get_faces_embedding

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(PROJECT_DIR, 'models')
FILES_DIR = os.path.join(PROJECT_DIR, 'files')
IMG_DIR = os.path.join(PROJECT_DIR, 'images')


def show_num_detect_faces(detector, directory=IMG_DIR):
    for subdir in os.listdir(directory):
        path = os.path.join(directory, subdir)
        if not os.path.isdir(path):
            continue
        faces = get_base_faces(detector, path)
        print(f'>loaded {len(faces)} examples for person: {subdir.replace("_", " ").title()}')


def get_base_faces(detector, directory=IMG_DIR):
    faces = []
    for file_name in os.listdir(directory):
        path = os.path.join(directory, file_name)
        img_array_ = np.array(Image.open(path).convert(mode="L"), dtype="uint8")
        try:
            face_black, _, face = detector.face_detection(img_array_, path, _label=file_name)
            faces.append(face)
        except TypeError:
            print(f"Can't find any face on path: {path}")
            continue
    return faces


def prepare_data_base_recognizer(detector):
    show_num_detect_faces(detector)

    current_id, label_ids, data, labels = 0, {}, [], []
    for root, dirs, files in os.walk(IMG_DIR):
        for file in files:
            if file.endswith("jpg") or file.endswith('png'):
                file_path = os.path.join(root, file)
                label = os.path.basename(root).replace("_", " ").title()
                # add new labels as int
                if label not in label_ids:
                    label_ids[label] = current_id
                    current_id += 1
                label_id = label_ids[label]
                # open image from path in black/white mode
                img_array = np.array(Image.open(file_path).convert(mode="L"), dtype="uint8")
                try:
                    curr_roi, curr_y, _ = detector.face_detection(img_array, file_path, label_id)
                    data.append(curr_roi)
                    labels.append(curr_y)
                except TypeError:
                    continue
                    # print(f"Can't find any face on path: {file_path}")
    with open(os.path.join(FILES_DIR, "labels.pickle"), 'wb') as f:
        pickle.dump(label_ids, f)
    return data, labels


def prepare_data_svm_recognizer(detector, recognizer):

    X, y = get_svm_dataset(detector)
    model = load_model(os.path.join(MODELS_DIR, "facenet_keras.h5"))
    X_embedding = get_faces_embedding(X, model)
    X_embedding_encode = recognizer.data_encoder.transform(X_embedding)
    y_encode = recognizer.label_encoder.fit_transform(y)
    joblib.dump(recognizer.label_encoder, os.path.join(MODELS_DIR, "label_encoder.pkl"))
    return X_embedding_encode, y_encode


def get_faces(detector, directory=IMG_DIR, size=(160, 160)):
    faces = []
    for file_name in os.listdir(directory):
        path = os.path.join(directory, file_name)
        img_array_ = np.array(Image.open(path).convert(mode="L"), dtype="uint8")
        try:
            face_black, _, face = detector.face_detection(img_array_, path, _label=file_name)
            face = cv2.resize(face, size)
            faces.append(face)
        except TypeError:
            print(f"Can't find any face on path: {path}")
            continue
        # print(face.shape)
        # cv2.imshow("Output", face)
        # cv2.waitKey(0)
    return faces


def get_svm_dataset(detector, directory=IMG_DIR):
    X_, y_ = [], []
    for subdir in os.listdir(directory):
        path = os.path.join(directory, subdir)
        # skip any files that might be in the dir
        if not os.path.isdir(path):
            continue
        # load all faces in the subdirectory
        faces = get_faces(detector, path)
        labels = [subdir.replace("_", " ").title() for _ in range(len(faces))]
        print(f'>loaded {len(faces)} examples for person: {subdir.replace("_", " ").title()}')
        X_.extend(faces)
        y_.extend(labels)
    return np.asarray(X_), np.asarray(y_)


if __name__ == '__main__':
    detector_base = FaceDetector(detection_type='base')
    detector_caffe = FaceDetector(detection_type='caffe')

    recognizer_base = BaseRecognizer()
    data_base, labels_base = prepare_data_base_recognizer(detector_caffe)
    print('Prepared data for base recognizer')
    recognizer_base.train_clf(data_base, labels_base)
    print('Trained base recognizer')

    recognizer_svm = SuppVecMachinesRecognizer()
    data_svm, labels_svm = prepare_data_svm_recognizer(detector_caffe, recognizer_svm)
    print('Prepared data for svm recognizer')
    recognizer_svm.train_clf(data_svm, labels_svm, show_stats=True)
    print('Trained svm recognizer')

    # for root, dirs, files in os.walk(IMG_DIR):
    #     # i = 1
    #     for file in files:
    #         if file.endswith("jpg") or file.endswith('png'):
    #             file_path = os.path.join(root, file)
    #             label = os.path.basename(root).replace("_", " ").title()
    #
    #             # add new labels as int
    #             if label not in y_ids:
    #                 y_ids[label] = current_id
    #                 current_id += 1
    #             y_id = y_ids[label]
    #
    #             # open image from path in black/white mode
    #             img_array = np.array(Image.open(file_path).convert(mode="L"), dtype="uint8")
    #             try:
    #                 curr_roi, curr_y, color_roi = detector.face_detection(img_array, file_path, y_id)
    #                 X.append(curr_roi)
    #                 curr_roi_svm = cv2.resize(color_roi, (160, 160))
    #                 print(curr_roi_svm.shape)
    #                 # b, g, r = cv2.split(curr_roi_svm)
    #                 # curr_roi_svm = cv2.merge([r, g, b])
    #                 # plt.subplot(20, 10, i)
    #                 # plt.axis('off')
    #                 # plt.imshow(curr_roi_svm)
    #                 # i += 1
    #                 # print(curr_roi_svm)
    #                 X_svm.append(curr_roi_svm)
    #                 # cv2.imshow("Output", curr_roi)
    #                 # cv2.waitKey(0)
    #                 y.append(curr_y)
    #                 # labels.append(curr_y)
    #             # except ValueError:
    #             #     continue
    #             except TypeError:
    #                 print(f"Can't find any face on path: {file_path}")
    #     # plt.show()
    #
    # with open("labels.pickle", 'wb') as f:
    #     pickle.dump(y_ids, f)
