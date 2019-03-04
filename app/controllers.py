from .views import *

class BaseController:

    def __init__(self, root):
        BaseController.ViewManager = ViewManager(root, self)

    def view(self, name):
        return BaseController.ViewManager.addView(name)


class Core(BaseController):

    def __init__(self, *args):
        super().__init__(*args)
        self.view("Main")
        self.view("Settings")
        self.view("Main")
