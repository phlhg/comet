from .views import *
from .models import *


class BaseController:

    def __init__(self, root):
        BaseController.ViewManager = ViewManager(root, self)

    def view(self, name):
        return BaseController.ViewManager.show(name)

    def getView(self,name):
        return BaseController.ViewManager.get(name)


class Core(BaseController):

    def __init__(self, *args):
        super().__init__(*args)
        self.client = Client(self)
        self.storage = Storage(self)
        self.view("Main")

