import tkinter
from api import Api

class Login:
    def  __init__(self, callback):
        self.callback = callback
        self.api = Api('http://localhost:5000')

        self.init_gui()

        self.window.mainloop()
    
    def init_gui(self):
        self.window = tkinter.Tk()
        self.window.title('Login to system')

        tkinter.Label(text="Username").grid(row=0, column=0)
        tkinter.Label(text="Pasword").grid(row=1, column=0)
        self.info_label = tkinter.Label()
        self.info_label.grid(row=2, columnspan=2)

        self.username_entry = tkinter.Entry()
        self.username_entry.grid(row=0, column=1)
        self.password_entry = tkinter.Entry(show="*")
        self.password_entry.grid(row=1, column=1)

        tkinter.Button(text="Login", command=self.login).grid(row=3, columnspan=2)
    
    def login(self):
        self.info_label.config(text="Authenticating...")
        self.window.update()

        response = self.api.login(self.username_entry.get(), self.password_entry.get())
        
        if response.status_code is not 200:
            self.info_label.config(text="Login failed, try again")
            return

        self.window.destroy()
        self.callback(response.text)