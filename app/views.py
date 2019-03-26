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
        self.sider = Frame(self.frame, bg="#eee")
        self.sider.pack()
        self.sider.place(relx=0, rely=0, relh=1, relw=0.25)

        self.content = Frame(self.frame, bg="#fff", height=720, width=670)
        self.content.place(relx=0.25, rely=0, relh=1, relw=0.75)



        e = Entry(self.content, bg="#ddd", fg="#333", borderwidth=20, relief=FLAT, font=("Segoe UI",12))
        e.place(relx=1, rely=1, relw=1, relh=0.08, anchor=SE)

        s = Button(self.content, text="➞", bd=0, highlightthickness=0, activeforeground="#fff", activebackground="#06d", bg="#09f", fg="#fff", font=("Segoe UI",24,"bold"))
        s.place(relx=0.92, rely=0.92, relw=0.08, relh=0.08)

        self.messages = Frame(self.content, bg="#f00")
        self.messages.place(relx=0, rely=0, relh=0.92, relw=1)

        self.canvas = Canvas(self.messages)
        self.canvas.pack()
        self.canvas.create_window((5,5), window=self.messages, anchor="nw")

        scrollbar = Scrollbar(self.content, command=self.canvas.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.canvas.config(yscrollcommand=scrollbar.set)

        l = Label(self.canvas, text="Max Muster", bg="#fff", anchor="w", pady=0, padx=20, font=("Segoe UI",24,"bold"))
        l.place(relx=0, rely=0, relw=1)

        for i in range(50):
            s = Button(self.messages, text=("Nachricht "+str(i)))
            s.pack()



        self.contactList = Frame(self.sider, bg="#eee")
        self.contactList.place(relx=0, rely=0, relh=0.92, relw=1)
        self.contactList.columnconfigure(0, weight=1)


        self.settings = Frame(self.sider, bg="#eee")
        self.settings.pack()
        self.settings.place(relx=0, rely=0.92, relh=0.08, relw=1)

        self.siderbutton = MenuButton(self.settings, text="⚪ "+self.controller.client.ip, command=lambda controller=self.controller: controller.view("Settings"))
        self.siderbutton.place(relx=0, rely=0, relh=1, relw=1)

        i = 0
        for contact in self.controller.contacts.contacts:
            ctn = MenuButton(self.contactList, text="▢ "+contact.username)
            ctn.grid(row=(i+1), column=0, columnspan=1, sticky=W+E)
            i += 1

        ctn = MenuButton(self.contactList, text="+ Kontakt hinzufügen")
        ctn.grid(row=(i+1), column=0, columnspan=1, sticky=W+E)


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

        btn1 = MenuButton(self.sider,  text="❮"+" "*3+"Einstellungen", command=lambda controller=self.controller: controller.view("Main"))
        btn1.grid(row=0, column=0, columnspan=1, sticky=W+E)

