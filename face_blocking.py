import os
import cv2
from keras.models import load_model
from face_detection import FaceDetector
from face_recognition import FaceRecognizer

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(PROJECT_DIR, 'models')
FILES_DIR = os.path.join(PROJECT_DIR, 'files')

class FaceBlocking:
    def __init__(self, detection_type, recognition_type, video_source=0):
        self.COVER_COLOR = (255, 0, 0)
        self.MIN_CONF = 40

        self.detector = FaceDetector(detection_type)
        self.face_recognizer = FaceRecognizer(recognition_type)
        self.embedding_model = load_model(os.path.join(MODELS_DIR, "facenet_keras.h5"))
        self.labels = self.face_recognizer.labels

        self.capture = cv2.VideoCapture(video_source)
        if not self.capture.isOpened():
            raise ValueError("Unable to open video source", video_source)

        self.width = self.capture.get(cv2.CAP_PROP_FRAME_WIDTH)
        self.height = self.capture.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def __del__(self):
        if self.capture.isOpened():
            self.capture.release()

    def get_processed_frame(self, _block_list=[], _debug=False):
        val, frame = self.capture.read()

        faces = self.detector.get_coordinates(frame, _multi_face=True)
        for i in range(len(faces)):
            start_x, start_y, end_x, end_y = faces[i]
            roi_color = frame[start_y:end_y, start_x:end_x]
            who_face, conf = self.face_recognizer.face_classification(roi_color, self.embedding_model)
            if conf >= self.MIN_CONF and who_face in _block_list:
                self.block_face(frame, who_face, start_x, start_y, end_x, end_y)
            if _debug:
                self.draw_debug(frame, who_face, start_x, start_y, end_x, end_y)

        return frame

    def draw_debug(self, _frame, _name, _start_x, _start_y, _end_x, _end_y):
        font = cv2.FONT_HERSHEY_SIMPLEX
        color = (255, 255, 255)
        stroke = 2
        cv2.putText(_frame, _name, (_start_x, _start_y), font, 1, color, stroke, cv2.LINE_AA)
        cv2.rectangle(_frame, (_start_x, _start_y), (_end_x, _end_y), color, stroke)
    
    def block_face(self, _frame, _name, _start_x, _start_y, _end_x, _end_y):
        cv2.rectangle(_frame, (_start_x, _start_y), (_end_x, _end_y), self.COVER_COLOR, -1)
