from .views import *
from .models import *


class BaseController:

    def __init__(self, root):
        BaseController.view = ViewManager(self, root)


class Core(BaseController):

    def __init__(self, *args):
        super().__init__(*args)
        self.storage = Storage(self)
        self.profile = Profile(self)
        self.contacts = ContactManager(self)
        self.client = Client(self)

        BaseController.view.open()
