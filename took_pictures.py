import os
import cv2
import argparse
import subprocess

from face_detection import FaceDetector


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--name')
    parser.add_argument('-t', '--detection_type', choices=['base', 'caffe'], default='caffe')
    parser.add_argument('-f', '--only_face', choices=['no', 'yes'], default="no")
    args = parser.parse_args()
    dir_name = args.name
    detection_type = args.detection_type
    only_face = True if args.only_face == 'yes' else False

    capture = cv2.VideoCapture(0)
    num = 1
    while True:
        if dir_name is None:
            print('You must pass your name as argument!')
            subprocess.run(["python", "took_pictures.py", "-h"])
            break

        img_dir = f'images/{dir_name}/'
        os.makedirs(img_dir, exist_ok=True)
        detector = FaceDetector(detection_type)
        # Capture frame-by-frame
        val, frame = capture.read()
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        try:
            start_x, start_y, end_x, end_y = detector.get_coordinates(frame)[0]
            roi_ = frame[start_y:end_y, start_x:end_x]
            cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), (255, 255, 255), 2)
            if only_face:
                cv2.imwrite(f'{img_dir}/{num}.png', roi_)
            else:
                cv2.imwrite(f'{img_dir}/{num}.png', frame)
            print(f'face no. {num}')
            num += 1

        except TypeError:
            pass

        # Display the resulting frame
        cv2.imshow('video', frame)
        if (cv2.waitKey(20) & 0xFF == ord('q')) or num == 1000:
            break
    # When everything done, release the capture
    capture.release()
    cv2.destroyAllWindows()
