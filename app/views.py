from tkinter import *
from .costumelements import *

class ViewManager:

    def __init__(self, root, controller):
        self.root = root
        self.controller = controller

        self.views = []
        self.viewsIndex = []

        self.root.title("P2P Chat by Nico Müller & Philippe Hugo")
        self.root.iconbitmap('favicon.ico')
        self.root.geometry("920x720")
        self.root["bg"] = "#fff"

    def show(self, name):
        view = self.getView(name)
        view.frame.tkraise()

    def getView(self, name):
        if name+"View" not in self.viewsIndex:
            view = globals()[name+"View"](self.root, self.controller, self.newFrame(name))
            self.views.append(view)
            self.viewsIndex.append(name+"View")
            return self.views[len(self.views)-1]
        else:
            view = self.views[self.viewsIndex.index(name+"View")]
            view.frame.tkraise()
            return view

    def newFrame(self, name):
        frame = Frame(self.root, bg="#fff", height=720, width=920)
        frame.grid(row=0, column=0, sticky=N+W+S+E)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)
        return frame


class BaseView:

    def __init__(self, root, controller, frame):
        self.root = root
        self.controller = controller
        self.frame = frame
        self.var = {}

    def set(self, name, value):
        self.var[name] = value

    def get(self, name):
        if name in self.var:
            return self.var[name]
        else:
            return '['+name+']'


class MainView(BaseView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create()

    def create(self):
        self.sider = Frame(self.frame, bg="#eee", height=720, width=250)
        self.sider.pack()
        self.sider.place(relx=0, rely=0, relh=1, relw=0.25)
        self.sider.columnconfigure(0, weight=1)

        self.content = Frame(self.frame, bg="#fff", height=720, width=670)
        self.content.place(relx=0.25, rely=0, relh=1, relw=0.75)

        l = Label(self.content, text="Max Muster", bg="#fff", anchor="w", pady=10, padx=20, font=("Segoe UI",24,"bold"))
        l.place(relx=0, rely=0, relw=1)

        e = Entry(self.content, bg="#ddd", fg="#333", borderwidth=20, relief=FLAT, font=("Segoe UI",12))
        e.place(relx=1, rely=1, relw=1, anchor=SE)

        self.siderbutton = MenuButton(self.sider, text="⚪ "+self.controller.client.ip, command=lambda controller=self.controller: controller.view("Settings"))
        self.siderbutton.grid(row=0, column=0, columnspan=1, sticky=W+E)

        self.siderbutton2 = MenuButton(self.sider, text="▢ Max Müller")
        self.siderbutton2.grid(row=1, column=0, columnspan=1, sticky=W+E)

        self.siderbutton2 = MenuButton(self.sider, text="▢ Hans Muster")
        self.siderbutton2.grid(row=2, column=0, columnspan=1, sticky=W+E)

        self.siderbutton2 = MenuButton(self.sider, text="▢ Thomas Dach")
        self.siderbutton2.grid(row=3, column=0, columnspan=1, sticky=W+E)



class SettingsView(BaseView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create()

    def create(self):
        self.sider = Frame(self.frame, bg="#eee", height=720, width=250)
        self.sider.pack()
        self.sider.place(relx=0, rely=0, relh=1, relw=0.25)
        self.sider.columnconfigure(0, weight=1)

        self.content = Frame(self.frame, bg="#fff", height=720, width=670)
        self.content.place(relx=0.25, rely=0, relh=1, relw=0.75)

        btn1 = MenuButton(self.sider,  text="❮ Chats", command=lambda controller=self.controller: controller.view("Main"))
        btn1.grid(row=0, column=0, columnspan=1, sticky=W+E)

