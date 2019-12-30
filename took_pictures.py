import sys
import os
import cv2

SIZE = (550, 550)
CASCADE_CLF = cv2.CascadeClassifier('cascades/data/haarcascade_frontalface_default.xml')


if __name__ == '__main__':
    capture = cv2.VideoCapture(0)
    num = 0
    while True:
        try:
            img_dir = f'images/{sys.argv[1]}/'
            os.makedirs(img_dir, exist_ok=True)
        except IndexError:
            print('You must pass your name as argument!')
            break

        num += 1
        # Capture frame-by-frame
        val, frame = capture.read()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = CASCADE_CLF.detectMultiScale(gray_frame, scaleFactor=1.5, minNeighbors=5)
        for (x1, y1, x2, y2) in faces:
            roi = frame[y1:y1+y2, x1:x1+x2]
            # cv2.rectangle(frame, (x1, y1), (x1 + x2, y1 + y2), (255, 255, 255), 2)
            print(f'face num {num}')
            cv2.imwrite(f'{img_dir}/{num}.png', roi)

        # Display the resulting frame
        cv2.imshow('video', frame)
        if num == 1000:
            break
    # When everything done, release the capture
    capture.release()
    cv2.destroyAllWindows()
