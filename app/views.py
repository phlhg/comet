from tkinter import *

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
        self.sider.grid(row=0, column=0, sticky=N+W+S)
        self.header = Frame(self.frame, bg="#ddd", height=80, width=920)
        self.header.grid(row=0, column=0, sticky=N+W+E)

        self.labelheader = Label(self.header, font='Helvetica 10 bold', bg="#ddd", padx=10, pady=10, text=self.controller.client.ip)
        self.labelheader.grid(row=0, column=0)

        self.labelheader2 = Label(self.header, text=self.get("name2"))
        self.labelheader2.grid(row=0, column=1)



class SettingsView(BaseView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create()

    def create(self):
        sider = Frame(self.frame, bg="#eee", height=720, width=250)
        sider.grid(row=0, column=0, sticky=N+W+S)
        header = Frame(self.frame, bg="#ddd", height=80, width=920)
        header.grid(row=0, column=0, sticky=N+W+E)

        btn1 = Button(header, bd=0, text="  ❮   ", command=lambda controller=self.controller: controller.view("Main"))
        btn1.grid(row=0, column=0)

