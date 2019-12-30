import cv2
import pickle
import numpy as np
from PIL import Image

SIZE = (550, 550)

with open("labels.pickle", 'rb') as file:
    LABELS = pickle.load(file)
    LABELS = {id_: label for label, id_ in LABELS.items()}

CASCADE_CLF = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_default.xml')
FACE_RECOGNIZER = cv2.face.LBPHFaceRecognizer_create()
FACE_RECOGNIZER.read('recognize_trained.yml')

if __name__ == '__main__':
    print(LABELS)
    capture = cv2.VideoCapture(0)
    while True:
        # Capture frame-by-frame
        val, frame = capture.read()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = CASCADE_CLF.detectMultiScale(gray_frame, scaleFactor=1.5, minNeighbors=5)
        for (x1, y1, x2, y2) in faces:
            # print(x1, y1, x2, y2)
            # interest_region_gray = gray_frame[y1:y1+y2, x1:x1+x2]
            interest_region_color = frame[y1:y1+y2, x1:x1+x2]
            interest_region_gray = Image.fromarray(gray_frame[y1:y1 + y2, x1:x1 + x2], mode="L")
            interest_region_gray_resized = interest_region_gray.resize(SIZE, Image.ANTIALIAS)
            interest_region_gray_resized_arr = np.array(interest_region_gray_resized, dtype="uint8")

            id_, conf = FACE_RECOGNIZER.predict(interest_region_gray_resized_arr)
            if (conf >= 45) and (conf <= 85):
                print(LABELS[id_])
                font = cv2.FONT_HERSHEY_SIMPLEX
                name = LABELS[id_]
                color = (255, 255, 255)
                stroke = 2
                cv2.putText(frame, name, (x1, y1), font, 1, color, stroke, cv2.LINE_AA)
                fill_color = (139, 216, 198)  # BGR 0-255
                cv2.rectangle(frame, (x1, y1), (x1 + x2, y1 + y2), fill_color, -1)
            cv2.rectangle(frame, (x1, y1), (x1 + x2, y1 + y2), (255, 255, 255), 2)

            # cv2.imwrite('roi_item.png', interest_region_gray_resized_arr)
            # cv2.imwrite('images/sebastian/8.png', interest_region_color)

        # Display the resulting frame
        cv2.imshow('video', frame)
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

    # When everything done, release the capture
    capture.release()
    cv2.destroyAllWindows()
