import os
import cv2
import argparse
import subprocess
# import numpy as np
# from PIL import Image

from keras.models import load_model

from face_detection import FaceDetector
from face_recognition import FaceRecognizer

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(PROJECT_DIR, 'models')
FILES_DIR = os.path.join(PROJECT_DIR, 'files')


def block_face(_frame, _name, _start_x, _start_y, _end_x, _end_y):
    font = cv2.FONT_HERSHEY_SIMPLEX
    color_text = (255, 255, 255)
    fill_color = (139, 216, 198)  # BGR 0-255
    stroke = 2
    cv2.putText(_frame, _name, (_start_x, _start_y), font, 1, color_text, stroke, cv2.LINE_AA)
    cv2.rectangle(_frame, (_start_x, _start_y), (_end_x, _end_y), fill_color, -1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--detection_type', choices=['base', 'caffe'], default='caffe')
    parser.add_argument('-r', '--recognition_type', choices=['base', 'svm'], default='svm')
    args = parser.parse_args()

    detection_type = args.detection_type
    recognition_type = args.recognition_type
    face_recognizer = FaceRecognizer(recognition_type)
    embedding_model = load_model(os.path.join(MODELS_DIR, "facenet_keras.h5"))

    capture = cv2.VideoCapture(0)
    while True:
        # Capture frame-by-frame
        val, frame = capture.read()
        if (detection_type is None) and (recognition_type is None):
            print('Missing argument')
            subprocess.run(["python", "face_indetification.py", "-h"])
            break
        detector = FaceDetector(detection_type)
        try:
            start_x, start_y, end_x, end_y = detector.get_coordinates(frame, _multi_face=True)
            roi_color = frame[start_y:end_y, start_x:end_x]
            who_face, conf = face_recognizer.face_classification(roi_color, embedding_model)
            if conf >= 40:  # and (conf <= 85):
                block_face(frame, who_face, start_x, start_y, end_x, end_y)
            cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (255, 255, 255), 2)

        except ValueError:
            try:
                faces = detector.get_caffe_coordinates(frame, _multi_face=True)
                for i in range(len(faces)):
                    start_x, start_y, end_x, end_y = faces[i]
                    roi_color = frame[start_y:end_y, start_x:end_x]
                    who_face, conf = face_recognizer.face_classification(roi_color, embedding_model)
                    if conf >= 40:  # and (conf <= 85):
                        block_face(frame, who_face, start_x, start_y, end_x, end_y)
                    cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (255, 255, 255), 2)
            except TypeError:
                # cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 0), -1)
                # cv2.putText(frame, "Can't detect any face", (int(frame.shape[1] / 3), int(frame.shape[0] / 2)),
                #             cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
                continue

        except TypeError:
            # cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 0), -1)
            # cv2.putText(frame, "Can't detect any face", (int(frame.shape[1]/3), int(frame.shape[0]/2)),
            #             cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)
            continue

        # Display the resulting frame
        cv2.imshow('video', frame)
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    capture.release()
    cv2.destroyAllWindows()
