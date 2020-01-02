import os
import sys
import pickle
import cv2
import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# from skimage import io, color
# from skimage.transform import resize
from PIL import Image

from face_indetification import CASCADE_CLF, FACE_RECOGNIZER, SIZE


class FaceDetector:
    def __init__(self, detection_type):
        self._roi = None
        self._label = None
        self._detection_type = detection_type.lower()
        print(self._detection_type)

    def get_coordinates(self, _img_array):
        if self._detection_type == "base":
            return self.get_base_coordinates(_img_array)
        elif self._detection_type == "caffe":
            return

    def face_detection(self, _img_array, _img_path, _label):
        if self._detection_type == "base":
            self._roi, self._label = self.base_detection(_img_array, _label)
        elif self._detection_type == "caffe":
            self._roi, self._label = self.caffe_detection(_img_path, _img_array, _label)
        return self._roi, self._label

    @staticmethod
    def get_base_coordinates(_img_array):
        # find faces on image
        faces = CASCADE_CLF.detectMultiScale(_img_array, scaleFactor=1.5, minNeighbors=5)
        # if False:
        # # if isinstance(faces, tuple):
        #     return
        # else:
        for (x1_, y1_, x2_, y2_) in faces:
            start_x_, end_x_ = x1_, x1_ + x2_
            start_y_, end_y_ = y1_, y1_ + y2_
            return start_x_, start_y_, end_x_, end_y_

    def base_detection(self, _img_array, _label):

        start_x, start_y, end_x, end_y = self.get_base_coordinates(_img_array)
        _roi = self.get_roi(_img_array, start_x, start_y, end_x, end_y)
        return _roi, _label

    def caffe_detection(self, img_path, _img_array, _label, prototxt="deploy.prototxt",
                        model="res10_300x300_ssd_iter_140000.caffemodel"):

        def get_best_face():
            confidences = []
            for j in range(0, detections.shape[2]):
                conf = detections[0, 0, j, 2]
                if conf > 0.9:
                    confidences.append(conf)
            if confidences:
                return max(confidences)

        # load model
        net = cv2.dnn.readNetFromCaffe(prototxt, model)
        # load image and construct an input blob for the image by resizing to a fixed 300x300 pixels and then normalizing it
        img = cv2.imread(img_path)
        (h, w) = img.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
        # pass the blob through the network and obtain the detections and predictions
        net.setInput(blob)
        detections = net.forward()

        best_conf = get_best_face()
        for i in range(0, detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence == best_conf:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (start_x, start_y, end_x, end_y) = box.astype("int")

                _roi = self.get_roi(_img_array, start_x, start_y, end_x, end_y)
                return _roi, _label

    @staticmethod
    def get_roi(_img_array, _start_x, _start_y, _end_x, _end_y):
        interest_region_gray = Image.fromarray(_img_array[_start_y:_end_y, _start_x:_end_x], mode="L")
        current_roi = np.array(interest_region_gray, dtype="uint8")
        # interest_region_gray.show()
        return current_roi
