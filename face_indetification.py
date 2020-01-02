import sys
import cv2
import pickle
import numpy as np
from PIL import Image

SIZE = (550, 550)
CASCADE_CLF = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_default.xml')
FACE_RECOGNIZER = cv2.face.LBPHFaceRecognizer_create()
FACE_RECOGNIZER.read('recognize_trained.yml')


def get_labels():
    with open("labels.pickle", 'rb') as file:
        labels = pickle.load(file)
        labels = {id_: label for label, id_ in labels.items()}
        return labels


def get_detection_mode():
    try:
        detection_type = sys.argv[1].lower()
    except IndexError:
        detection_type = "base"
    return detection_type


def face_detection(frame_):
    detection_type = get_detection_mode()
    if detection_type == 'base':
        return base_face_detection(frame_)
    elif detection_type == 'caffe':
        return caffe_face_detection(frame_)


def base_face_detection(frame_):
    gray_frame_ = cv2.cvtColor(frame_, cv2.COLOR_BGR2GRAY)
    faces = CASCADE_CLF.detectMultiScale(gray_frame_, scaleFactor=1.5, minNeighbors=5)
    for (x1, y1, x2, y2) in faces:
        start_x_, end_x_ = x1, x1 + x2
        start_y_, end_y_ = y1, y1 + y2
        roi_ = frame_[start_y_:end_y_, start_x_:end_x_]
        print(roi_.shape)
        return start_x_, start_y_, end_x_, end_y_


def caffe_face_detection(frame_):
    (h, w) = frame_.shape[:2]
    net = cv2.dnn.readNetFromCaffe('deploy.prototxt', 'res10_300x300_ssd_iter_140000.caffemodel')
    blob = cv2.dnn.blobFromImage(cv2.resize(frame_, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
    # pass the blob through the network and obtain the detections and predictions
    net.setInput(blob)
    detections = net.forward()
    for i in range(0, detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        if confidence < 0.7:
            continue
        box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
        (start_x_, start_y_, end_x_, end_y_) = box.astype("int")
        roi_ = frame_[start_y_:end_y_, start_x_:end_x_]
        print(roi_.shape)
        return start_x_, start_y_, end_x_, end_y_


LABELS = get_labels()
if __name__ == '__main__':
    print(LABELS)
    capture = cv2.VideoCapture(0)
    while True:
        # Capture frame-by-frame
        val, frame = capture.read()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        try:
            start_x, start_y, end_x, end_y = face_detection(frame)
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

            # cv2.imwrite('roi_item.png', interest_region_gray_resized_arr)
            # cv2.imwrite('images/sebastian/8.png', interest_region_color)

        # Display the resulting frame
        cv2.imshow('video', frame)
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    capture.release()
    cv2.destroyAllWindows()
