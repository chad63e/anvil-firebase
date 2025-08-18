import anvil.server  # noqa: F401
from anvil import *  # noqa: F403
from anvil.js import window

from ._anvil_designer import Form1Template


class Form1(Form1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.

    def link_1_click(self, **event_args):
        """This method is called when the link is clicked"""
        window.open("https://github.com/chad63e/anvil-firebase/wiki")
