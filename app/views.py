from tkinter import *
from .costumelements import *

class ViewManager:

    def __init__(self, core, root):
        self.core = core
        self.root = root

        self.root.title("P2P Chat by Nico Müller & Philippe Hugo")
        self.root.iconbitmap('favicon.ico')
        self.root.geometry("920x720")
        self.root["bg"] = "#fff"

        self.switch = Switch(self.core, self.root)

    def open(self):
        self.switch.add("SearchView")
        self.switch.add("SettingsView")
        self.switch.add("MainView")

        self.switch.get("MainView").show()

    def show(self, name):
        self.switch.show(name)


class Switch:

    def __init__(self, core, root):
        self.core = core
        self.root = root

        self.views = []
        self.viewsIndex = []

    def get(self, name):
        return self.views[self.viewsIndex.index(name)]

    def show(self, name):
        self.get(name).show()

    def add(self, viewname):
        layer = globals()[viewname](self.core, self.createLayer())
        print(layer)
        self.viewsIndex.append(viewname)
        self.views.append(layer)
        return self.views[-1]

    def createLayer(self):
        frame = Frame(self.root, bg="#fff")
        frame.place(relx=0, rely=0, relw=1, relh=1)
        return frame


class BaseView:

    def __init__(self, core, root):
        self.core = core
        self.root = root

    def show(self):
        self.root.tkraise()


class MainView(BaseView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create()

    def create(self):
        self.sider = Sider(self.core, self.root)
        self.sider.navBack = NavigationBack("✉ P2P Chat", "", self.core, self.sider.frame)
        self.sider.contactList = ContactList(self.core.contacts.contacts, self.core, self.sider.frame)

        self.content = Content(self.core, self.root)
        self.content.title = ContentTitle("Chats", self.core, self.content.frame)

        #INPUT

        e = Entry(self.content.frame, bg="#eee", fg="#333", borderwidth=20, relief=FLAT, font=("Segoe UI",12))
        e.place(relx=1, rely=1, relw=1, relh=0.08, anchor=SE)

        s = Button(self.content.frame, text="➞", bd=0, highlightthickness=0, activeforeground="#fff", activebackground="#06d", bg="#09f", fg="#fff", font=("Segoe UI",24,"bold"))
        s.place(relx=0.92, rely=0.92, relw=0.08, relh=0.08)

        ctn = MenuButton(self.sider.frame, fg="#999", text="+ Freunde finden", command=lambda controller=self.core: controller.view.show("SearchView"))
        ctn.pack(fill=X)


class SettingsView(BaseView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create()

    def create(self):
        self.sider = Sider(self.core, self.root)
        self.sider.navBack = NavigationBack("Chats", "MainView", self.core, self.sider.frame)

        self.content = Content(self.core, self.root)
        self.content.title = ContentTitle("Einstellungen", self.core, self.content.frame)


class SearchView(BaseView):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.create()

    def create(self):
        self.sider = Sider(self.core, self.root)
        self.sider.navBack = NavigationBack("Chats", "MainView", self.core, self.sider.frame)
        self.sider.contactList = ContactList([], self.core, self.sider.frame)
        ctn = MenuButton(self.sider.frame, fg="#999", text="    Suchen ...", command=lambda controller=self.core: controller.view.show("SearchView"))
        ctn.pack(fill=X)

        self.content = Content(self.core, self.root)
        self.content.title = ContentTitle("Freunde finden", self.core, self.content.frame)

        img = PhotoImage(file="app/img/network.png")
        panel = Label(self.content.frame, bg="#fff", image=img)
        panel.image = img
        panel.place(relx=0, rely=0.11, relw=1, relh=0.89)


class BaseElement:

    def __init__(self, core, root):
        self.core = core
        self.root = root


class HoverButton(BaseElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bg = "#eee"
        self.bghover = "#ddd"

        self.frame = Button(self.root, bg=self.bg, anchor="w", padx=20, pady=10, bd=0, activebackground=self.bghover, font=("Segoe UI",12))
        self.frame.bind("<Enter>", self.on_enter)
        self.frame.bind("<Leave>", self.on_leave)

    def setColor(self,bg,bghover):
        self.bg = bg
        self.bghover = bghover
        self.frame.config(bg=self.bg, activebackground=self.bghover)

    def on_enter(self, e):
        self.frame.config(bg=self.bghover)

    def on_leave(self, e):
        self.frame.config(bg=self.bg)


class Sider(BaseElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frame = Frame(self.root, bg="#eee")
        self.frame.place(relx=0, rely=0, relh=1, relw=0.25)

        self.navSettings = NavigationSettings(self.core, self.frame)


class NavigationBack(HoverButton):

    def __init__(self, title, back, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = title
        self.back = back
        self.frame.config(text="✉  P2P Chat", fg="#fff", activeforeground="#fff")
        self.setColor("#0096d2", "#0096d2")
        if self.back != "":
            self.frame.config(text="❮  P2P Chat")
            self.frame.bind("<Button-1>", self.click)

        self.frame.config(font=("Segoe UI",22,"bold"), pady=7)
        self.frame.pack(fill=X)

    def click(self, e):
        self.core.view.show(self.back)


class NavigationSettings(HoverButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frame.config(text="⚪ "+self.core.client.ip, )
        self.frame.bind("<Button-1>", self.click)
        self.frame.place(relx=0, rely=0.92, relh=0.08, relw=1)
        self.setColor("#ddd", "#ccc")

    def click(self, e):
        self.core.view.show("SettingsView")


class Content(BaseElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frame = Frame(self.root, bg="#fff", height=720, width=670)
        self.frame.place(relx=0.25, rely=0, relh=1, relw=0.75)


class ContentTitle(BaseElement):

    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = title
        self.placeHolder = Label(self.root, text=self.title, bg="#fff", fg="#fff", anchor="w", pady=15, padx=20, font=("Segoe UI",24,"bold"))
        self.placeHolder.pack()
        self.frame = Label(self.root, text=self.title, bg="#fff", fg="#000", anchor="w", pady=15, padx=20, font=("Segoe UI",24,"bold"))
        self.frame.place(relx=0, rely=0, relw=1)


class ContactList(BaseElement):

    def __init__(self, contacts, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frame = Frame(self.root, bg="#eee")
        self.frame.place(relx=0, rely=0, relw=1)
        self.list = []

        for contact in self.core.contacts.contacts:
            self.list.append(ContactListElement(contact, self.core, self.root))


class ContactListElement(HoverButton):

    def __init__(self, contact, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.contact = contact
        self.frame.config(text="▢ "+contact.username)
        self.frame.pack(fill=X)

