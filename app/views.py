from tkinter import *
from PIL import Image, ImageTk

class ViewManager:

    def __init__(self, core, root):
        self.core = core
        self.root = root
        self.top = Toplevel(root)

        self.root.title("COMET P2P")
        self.root.iconbitmap('app/img/favicon.ico')
        self.root.geometry("920x720")
        self.root.overrideredirect(True)
        self.root["bg"] = "#000"

        self.top.title(self.root.title())
        self.top.iconbitmap('app/img/favicon.ico')
        self.top.geometry(self.root.geometry())
        self.top.attributes("-alpha",0.0)

        self.top.img = ImageTk.PhotoImage(Image.open('app/img/logo.png'))
        self.top.label = Label(self.top, image=self.top.img)
        self.top.label.place(relx=0,rely=0, relw=1, relh=1)
        self.top.label = self.top.img

        self.header = Header(self.core,self.root)
        self.switch = Switch(self.core, self.root)

        self.top.bind("<FocusIn>",lambda e: self.normalize())

    def open(self):
        self.switch.add("SearchView")
        self.switch.add("SettingsView")
        self.switch.add("MainView")
        self.switch.get("MainView").show()

    def minimize(self):
        self.root.attributes("-alpha",0.0)
        self.root.overrideredirect(False)
        self.root.iconify()
        self.root.overrideredirect(True)
    
    def normalize(self):
        self.top.iconify()
        self.root.overrideredirect(False)
        self.root.deiconify()
        self.root.overrideredirect(True)
        self.root.attributes("-alpha",1)

    def close(self):
        self.root.destroy()

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
        self.viewsIndex.append(viewname)
        self.views.append(layer)
        return self.views[-1]

    def createLayer(self):
        frame = Frame(self.root, bg="#fff")
        frame.place(relx=0, rely=0.03, relw=1, relh=0.97)
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
        self.sider.navBack = NavigationBack("", "", self.core, self.sider.frame)
        self.sider.contactList = ContactList(self.core.contacts.contacts, self.core, self.sider.frame)

        self.content = Content(self.core, self.root)
        self.content.title = ContentTitle("Chat", self.core, self.content.frame)
        self.content.chat = Chat(self.content.title, self.core,self.content.frame)

        #INPUT

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


class Header(BaseElement):

    color = "#006FAE"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frame = Frame(self.root, bg=Header.color)
        self.frame.place(relx=0, rely=0, relh=0.03, relw=1)

        self.action = HeaderActions(self.core,self.frame)

        self.frame.bind("<ButtonPress-1>", self.StartMove)
        self.frame.bind("<ButtonRelease-1>", self.StopMove)
        self.frame.bind("<B1-Motion>", self.OnMotion)
    
    def StartMove(self, event):
        self.x = event.x
        self.y = event.y

    def StopMove(self, event):
        self.x = None
        self.y = None

    def OnMotion(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry("+%s+%s" % (x, y))


class HeaderActions(BaseElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frame = Frame(self.root, bg=Header.color)
        self.frame.place(relx=1, rely=0, relh=1, anchor=NE)

        self.close = HeaderClose(self.core, self.frame)
        self.minimize = HeaderMinimize(self.core, self.frame)


class HeaderClose(BaseElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        size = 18
        self.img = ImageTk.PhotoImage(Image.open('app/img/close.png').resize((size,size), Image.ANTIALIAS))
        self.frame = Label(self.root, bg=Header.color, width="20px", image=self.img)
        self.frame.image = self.img
        self.frame.pack(side=RIGHT, fill=Y)

        self.frame.bind("<Enter>",self.enter)
        self.frame.bind("<Leave>",self.leave)
        self.frame.bind("<Button-1>",self.click)

    def click(self,e):
        self.core.view.close()

    def enter(self,e):
        self.frame.config(bg="#f00")

    def leave(self,e):
        self.frame.config(bg=Header.color)


class HeaderMinimize(BaseElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        size = 18
        self.img = ImageTk.PhotoImage(Image.open('app/img/minimize.png').resize((size,size), Image.ANTIALIAS))
        self.frame = Label(self.root, bg=Header.color, width="20px", image=self.img)
        self.frame.image = self.img
        self.frame.pack(side=RIGHT, fill=Y)

        self.frame.bind("<Enter>",self.enter)
        self.frame.bind("<Leave>",self.leave)
        self.frame.bind("<Button-1>",self.click)

    def click(self,e):
        self.core.view.minimize()

    def enter(self,e):
        self.frame.config(bg="#0080c9")

    def leave(self,e):
        self.frame.config(bg=Header.color)


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
        self.frame.config(text="❮  "+self.title, font=("Segoe UI",12))
        self.frame.bind("<Button-1>", self.click)
        self.setColor("#ddd", "#ccc")
        if self.back == "":
            self.frame.config(text="   COMET P2P", font=("Segoe UI",12, "bold"))
            self.frame.unbind("<Button-1>")
            self.setColor("#ddd", "#ddd")

        self.frame.config(pady=23)
        self.frame.pack(fill=X)

    def click(self, e):
        self.core.view.show(self.back)


class NavigationSettings(HoverButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frame.config(text="⚪ "+self.core.profile.username, )
        self.frame.bind("<Button-1>", self.click)
        self.frame.place(relx=0, rely=0.92, relh=0.08, relw=1)
        self.setColor("#ddd", "#ccc")

    def click(self, e):
        self.core.view.show("SettingsView")


class MenuButton(Button):

    def __init__(self, master, **kw):
        Button.__init__(self, master=master, **kw)
        self["background"] = "#eee"
        self.defaultBackground = self["background"]
        self["activebackground"] = "#ddd"
        self['borderwidth'] = 0
        self['font'] = ("Segoe UI",12)
        self['anchor'] = "w"
        self['padx'] = 20
        self['pady'] = 10
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self['activebackground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground


class Content(BaseElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.frame = Frame(self.root, bg="#fff", height=720, width=670)
        self.frame.place(relx=0.25, rely=0, relh=1, relw=0.75)


class ContentLogo(BaseElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.img = ImageTk.PhotoImage(Image.open('app/img/logo.png').resize((40,40), Image.ANTIALIAS))
        self.frame = Label(self.root, bg="#fff", image=self.img)
        self.frame.image = self.img
        self.frame.place(relx=1, rely=0, w="58px", h="58px", anchor=NE)
        self.frame.bind("<Button-1>",self.click)

    def click(self,e):
        self.core.view.show("MainView")


class ContentTitle(BaseElement):

    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.title = title
        self.frame = Label(self.root, text=self.title, bg="#fff", fg="#000", anchor="w", pady=15, padx=20, font=("Segoe UI",24,"bold"))
        self.frame.place(relx=0, rely=0, relw=1)
        self.logo = ContentLogo(self.core, self.root)

    def text(self,text):
        self.frame.config(text=text)


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
        self.frame.bind("<Button-1>",self.click)

    def click(self,e):
        self.core.view.switch.get("MainView").content.chat.load(self.contact.token)


class Chat(BaseElement):

    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.active = False
        self.title = title
        self.frame = Frame(self.root, bg="#fff")
        self.frame.place(relx=0, rely=1, relh=0.892, relw=1, anchor=SW)
        
        self.window = ChatWindow(self,self.core,self.frame)
        self.input = Input(self.core,self.frame)
        self.load("000000")

    def load(self, token):
        self.active = self.core.contacts.get(token)
        self.title.text(self.active.username)
        self.window.clear()
        for message in self.active.messages:
            self.window.addMessage(message)
        self.window.showNew()


class ChatWindow(BaseElement):

    def __init__(self, chat, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.chat = chat
        self.frame = VerticalScrolledFrame(self.root, bg="#fff")
        self.messages = []
        self.frame.place(relx=0, rely=0, relw=1, relh=0.91)
    
    def clear(self):
        for message in self.messages:
            message.frame.destroy()
            del message
        self.messages = []

    def addMessage(self, message):
        self.messages.append(ChatMessage(message, self.core, self.frame.interior))

    def showNew(self):
        self.frame.scroll(1)


class ChatMessage(BaseElement):

    def __init__(self, message, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.message = message
        self.frame = Label(self.root, wraplength=400, text=self.message.text, bg="#fff", fg="#000", anchor=NW, justify=LEFT, pady=5, padx=20, font=("Segoe UI",14,"italic"))
        if self.message.self:
            self.frame.config(anchor=NE, fg="#00A3FF",justify=RIGHT)
        self.frame.pack(fill=X)


class Input(BaseElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.onsend = lambda value: print("Message: "+value)

        self.frame = Frame(self.root, bg="#fff")
        self.frame.place(relx=0, rely=1, relw=1, relh=0.09, anchor=SW)

        self.entry = Entry(self.frame, bg="#eee", fg="#333", borderwidth=20, relief=FLAT, font=("Segoe UI",12))
        self.entry.place(relx=0, rely=0, relw=1, relh=1)
        self.entry.bind("<Return>", self.click)

        self.button = InputButton(self.core, self.frame)
        self.button.frame.place(relx=1, rely=0, relw=0.08, relh=1, anchor=NE)
        self.button.frame.bind("<Button-1>", self.click)

    def click(self, e):
        value = self.entry.get()
        if value == "":
            return
        self.onsend(value)
        self.entry.delete(0,END)
        self.entry.insert(0,"")


class InputButton(BaseElement):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        size = 35
        self.img = ImageTk.PhotoImage(Image.open('app/img/send.png').resize((size,size), Image.ANTIALIAS))
        self.imghover = ImageTk.PhotoImage(Image.open('app/img/sendhover.png').resize((size,size), Image.ANTIALIAS))
        self.frame = Label(self.root, image=self.img)
        self.frame.image = self.img
        self.frame.bind("<Enter>",self.enter)
        self.frame.bind("<Leave>",self.leave)

    def enter(self,e):
        self.frame.config(image=self.imghover)

    def leave(self,e):
        self.frame.config(image=self.img)


# by https://gist.github.com/bakineugene/76c8f9bcec5b390e45df

class VerticalScrolledFrame(Frame):
    """A pure Tkinter scrollable frame that actually works!
    * Use the 'interior' attribute to place widgets inside the scrollable frame
    * Construct and pack/place/grid normally
    * This frame only allows vertical scrolling
    """
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)            

        # create a canvas object and a vertical scrollbar for scrolling it
        self.vscrollbar = Scrollbar(self, orient=VERTICAL)
        self.vscrollbar.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = Canvas(self, bd=0, highlightthickness=0, yscrollcommand=self.vscrollbar.set, bg="#fff")
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        self.vscrollbar.config(command=self.canvas.yview)

        # reset the view
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # create a frame inside the canvas which will be scrolled with it
        self.interior = Frame(self.canvas)
        self.interior_id = self.canvas.create_window(0, 0, window=self.interior,anchor=NW)
        self.interior.bind('<Configure>', self._configure_interior)
        self.canvas.bind('<Configure>', self._configure_canvas)
        self.canvas.bind_all("<MouseWheel>", self.onMouseWheel)

    def _configure_interior(self,event=""):
        size = (self.interior.winfo_reqwidth(), self.interior.winfo_reqheight())
        self.canvas.config(scrollregion="0 0 %s %s" % size)
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.config(width=self.interior.winfo_reqwidth())

    def _configure_canvas(self,event=""):
        if self.interior.winfo_reqwidth() != self.canvas.winfo_width():
            self.canvas.itemconfigure(self.interior_id, width=self.canvas.winfo_width())

    def onMouseWheel(self,e):
        delta = int(-1*(int(e.delta)/120))
        self.canvas.yview_scroll(delta, "units")

    def scroll(self,s):
        self.update()
        self._configure_canvas()
        self._configure_interior()
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(s)

