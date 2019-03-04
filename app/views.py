from tkinter import *


class ViewManager:

    def __init__(self, root):
        self.root = root
        self.pages = []

        self.root.geometry("920x720")
        self.root["bg"] = "#fff"

    def addPage(self, name):
        view = globals()[name+"View"](self.root, self.newFrame(name))
        self.pages.append(view)
        return self.pages[len(self.pages)-1]

    def newFrame(self, name):
        frame = Frame(self.root, bg="#fff", height=720, width=920)
        frame.grid(row=0, column=0, sticky=N+W+S+E)
        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

        return frame


class BaseView:

    def __init__(self, root, frame):
        self.root = root
        self.frame = frame


class MainView(BaseView):

    def __init__(self, root, frame):
        super().__init__(root, frame)
        self.create()

    def create(self):
        sider = Frame(self.frame, bg="#eee", height=720, width=250)
        sider.grid(row=0, column=0, sticky=N+W+S)
        header = Frame(self.frame, bg="#ddd", height=60, width=920)
        header.grid(row=0, column=0, sticky=N+W+E)

        btn1 = Button(header, text="LOL")
        btn1.grid(row=0, column=0)


class SettingsView(BaseView):

    def __init__(self, root, frame):
        super().__init__(root, frame)
        self.create()

    def create(self):
        self.root.title("Einstellungen")
