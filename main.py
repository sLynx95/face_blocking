import argparse
from app_gui import App
from login_gui import Login

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-dt', '--detection_type', choices=['base', 'caffe'], default='caffe')
    parser.add_argument('-rt', '--recognition_type', choices=['base', 'svm'], default='svm')
    parser.add_argument('-s', '--server')
    parser.add_argument('-d', '--debug', action='store_true')
    args = parser.parse_args()

    detection_type = args.detection_type
    recognition_type = args.recognition_type
    server_url = args.server
    debug = args.debug

    if not server_url:
        App(
            detection_type=detection_type,
            recognition_type=recognition_type,
            debug=debug
        )
    else:
        main_window_callback = lambda token: App(
            detection_type=detection_type,
            recognition_type=recognition_type,
            server_url=server_url,
            token=token,
            debug=debug
        )
        Login(main_window_callback)
