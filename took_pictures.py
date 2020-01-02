import sys
import os
import cv2
import argparse
import subprocess

from face_indetification import CASCADE_CLF, SIZE
from face_detection import FaceDetector

parser_pic = argparse.ArgumentParser()
parser_pic.add_argument('-n', '--name')
parser_pic.add_argument('-t', '--detection_type', choices=['base', 'caffe'], default='base')
parser_pic.add_argument('-f', '--only_face', choices=['False', 'True'], default='False')
args = parser_pic.parse_args()

dir_name = args.name
detection_type = args.detection_type
only_face = args.only_face

if __name__ == '__main__':
    capture = cv2.VideoCapture(0)
    num = 0
    while True:
        if dir_name is None:
            print('You must pass your name as argument!')
            # subprocess.run(["python", "took_pictures.py", "-h"])
            break

        img_dir = f'images/{dir_name}/'
        os.makedirs(img_dir, exist_ok=True)
        detector = FaceDetector(detection_type)
        num += 1
        # Capture frame-by-frame
        val, frame = capture.read()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        print(f'face num {num}')

        try:
            start_x, start_y, end_x, end_y = detector.get_coordinates(frame)
            roi_ = frame[start_y:end_y, start_x:end_x]
        except TypeError:
            continue
        cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (255, 255, 255), 2)
        if only_face:
            cv2.imwrite(f'{img_dir}/{num}.png', roi_)
        else:
            cv2.imwrite(f'{img_dir}/{num}.png', frame)

        # Display the resulting frame
        cv2.imshow('video', frame)
        if (cv2.waitKey(20) & 0xFF == ord('q')) or num == 1000:
            break
    # When everything done, release the capture
    capture.release()
    cv2.destroyAllWindows()
