import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import time
import traceback
import argparse
from face_blocking import FaceBlocking

class App:
    def __init__(self, window, window_title, detection_type, recognition_type, video_source=0):
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source

        self.vid = FaceBlocking(detection_type, recognition_type, video_source)
        
        self.init_gui()

        self.delay = 15
        self.update()

        self.window.mainloop()

    def init_gui(self):
        self.canvas = tkinter.Canvas(self.window, width = self.vid.width, height = self.vid.height)
        # self.canvas = tkinter.Canvas(self.window, width = 300, height = 300)
        self.canvas.pack()

        self.demo_mode = tkinter.BooleanVar(value=True)
        demo_checkbox = tkinter.Checkbutton(self.window, text="Demo mode", variable=self.demo_mode)
        demo_checkbox.pack(anchor=tkinter.CENTER, expand=True)

    def snapshot(self):
        print('snapshot')
    
    def update(self):
        try:
            frame = self.vid.get_processed_frame(_demo=self.demo_mode.get())

            self.photo = PIL.ImageTk.PhotoImage(image = PIL.Image.fromarray(frame))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
        except Exception as e:
            print(traceback.format_exc())


        self.window.after(self.delay, self.update)
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--detection_type', choices=['base', 'caffe'], default='caffe')
    parser.add_argument('-r', '--recognition_type', choices=['base', 'svm'], default='svm')
    args = parser.parse_args()

    detection_type = args.detection_type
    recognition_type = args.recognition_type
    App(tkinter.Tk(), "BLOCKING FACES LETS GOO", detection_type, recognition_type)
