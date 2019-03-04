from .views import *

class BaseController:

    def __init__(self, root):
        BaseController.MainView = MainView(root)

    def view(self, name):
        return BaseController.MainView.addPage(name)


class Core(BaseController):

    def __init__(self, *args):
        super().__init__(*args)
        self.view("Main")

        self.loop()
