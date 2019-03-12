from tkinter import *

class MenuButton(Button):

    def __init__(self, master, **kw):
        Button.__init__(self, master=master, **kw)
        self["background"] = "#eee"
        self.defaultBackground = self["background"]
        self["activebackground"] = "#ddd"
        self['borderwidth'] = 0
        self['font'] = font=("Segoe UI",12)
        self['anchor'] = "w"
        self['padx'] = 20
        self['pady'] = 10,
        self.bind("<Enter>", self.on_enter)
        self.bind("<Leave>", self.on_leave)

    def on_enter(self, e):
        self['background'] = self['activebackground']

    def on_leave(self, e):
        self['background'] = self.defaultBackground
