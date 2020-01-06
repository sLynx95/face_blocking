import tkinter
import cv2
import PIL.Image, PIL.ImageTk
import traceback
from api import Api
from face_blocking import FaceBlocking

class App:
    def __init__(self, detection_type, recognition_type, server_url = None, token = None, video_source = 0, debug=False):
        self.video_source = video_source
        self.server_url = server_url
        self.token = token
        self.debug = debug

        self.personal_banned_labels = []
        self.system_banned_labels = []
        self.banned_labels = []

        self.vid = FaceBlocking(detection_type, recognition_type, video_source)
        self.load_labels()
        
        self.init_gui()

        if server_url: self.pool(callback=lambda: self.update_system_banned_labels_async(redraw=True), delay=3000)
        self.pool(callback=lambda: self.draw_frame(), delay=15)

        self.window.mainloop()


    def init_gui(self):
        self.window = tkinter.Tk()
        self.window.title('Face blocking AR')

        self.canvas = tkinter.Canvas(self.window, width=self.vid.width, height=self.vid.height)
        self.canvas.grid(row=0, columnspan=2)

        tkinter.Label(text="Select banned").grid(row=1, column=0)
        personal_banned_labels_listbox = tkinter.Listbox(selectmode=tkinter.MULTIPLE, activestyle=tkinter.NONE)
        personal_banned_labels_listbox.grid(row=2, column=0)
        personal_banned_labels_listbox.insert(tkinter.END, *self.labels)
        personal_banned_labels_listbox.bind('<<ListboxSelect>>', self.update_personal_banned_labels)

        tkinter.Label(text="System banned list").grid(row=1, column=1)
        self.system_banned_labels_listbox = tkinter.Listbox()
        self.system_banned_labels_listbox.grid(row=2, column=1)
        self.system_banned_labels_listbox.insert(tkinter.END, *self.system_banned_labels)
        self.system_banned_labels_listbox.config(state=tkinter.DISABLED)

    def load_labels(self):
        if self.server_url: 
            self.api = Api(server_url=self.server_url)
            self.update_labels()
            self.update_system_banned_labels()
        else:
            self.labels = self.vid.labels

    def update_personal_banned_labels(self, _evt):
        self.personal_banned_labels = [_evt.widget.get(int(i)) for i in _evt.widget.curselection()]
        self.update_banned_labels()

    def draw_system_banned_list(self):
        try:
            self.system_banned_labels_listbox.config(state=tkinter.NORMAL)
            self.system_banned_labels_listbox.delete(0, tkinter.END)
            self.system_banned_labels_listbox.insert(tkinter.END, *self.system_banned_labels)
            self.system_banned_labels_listbox.config(state=tkinter.DISABLED)
            self.window.update()
        except:
            return

    def update_system_banned_labels_async(self, redraw=False):
        def callback(response):
            self.system_banned_labels = response.json()
            self.update_banned_labels()
            if redraw: self.draw_system_banned_list()

        self.api.run_async(
            lambda: self.api.get_user_ban_list(self.token),
            callback=callback
        )
    
    def update_system_banned_labels(self):
        self.system_banned_labels = self.api.get_user_ban_list(self.token).json()
        self.update_banned_labels()
    
    def update_banned_labels(self):
        self.banned_labels = list(set(self.personal_banned_labels + self.system_banned_labels))

    def update_labels(self):
        self.labels = self.api.get_labels(self.token).json()

    def draw_frame(self):
        try:
            frame = self.vid.get_processed_frame(_block_list=self.banned_labels, _debug=self.debug)

            self.photo = PIL.ImageTk.PhotoImage(image=PIL.Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)))
            self.canvas.create_image(0, 0, image = self.photo, anchor = tkinter.NW)
        except Exception as e:
            print(traceback.format_exc())

    def pool(self, callback, delay):
        callback()
        self.window.after(delay, lambda: self.pool(callback, delay))
 