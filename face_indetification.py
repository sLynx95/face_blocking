import sys
import cv2
import pickle
import argparse
import subprocess
import numpy as np
from PIL import Image

from face_detection import FaceDetector

SIZE = (550, 550)
CASCADE_CLF = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_default.xml')
FACE_RECOGNIZER = cv2.face.LBPHFaceRecognizer_create()
FACE_RECOGNIZER.read('recognize_trained.yml')

parser = argparse.ArgumentParser()
parser.add_argument('--detection_type', choices=['base', 'caffe'])
args = parser.parse_args()
detection_type = args.detection_type


def get_labels():
    with open("labels.pickle", 'rb') as file:
        labels = pickle.load(file)
        labels = {id_: label for label, id_ in labels.items()}
        return labels


LABELS = get_labels()
if __name__ == '__main__':
    # print(LABELS)
    capture = cv2.VideoCapture(0)
    while True:
        # Capture frame-by-frame
        val, frame = capture.read()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        if detection_type is None:
            print('Missing argument')
            subprocess.run(["python", "face_indetification.py", "-h"])
            break
        detector = FaceDetector(detection_type)
        try:
            start_x, start_y, end_x, end_y = detector.get_coordinates(frame)
        except TypeError:
            continue
        roi = gray_frame[start_y:end_y, start_x:end_x]
        id_, conf = FACE_RECOGNIZER.predict(roi)
        if conf >= 60:    # and (conf <= 85):
            print(LABELS[id_])
            font = cv2.FONT_HERSHEY_SIMPLEX
            name = LABELS[id_]
            color = (255, 255, 255)
            stroke = 2
            cv2.putText(frame, name, (start_x, start_y), font, 1, color, stroke, cv2.LINE_AA)
            fill_color = (139, 216, 198)  # BGR 0-255
            cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), fill_color, -1)
        cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (255, 255, 255), 2)

        # Display the resulting frame
        cv2.imshow('video', frame)
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    capture.release()
    cv2.destroyAllWindows()
