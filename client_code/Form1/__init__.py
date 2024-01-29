import anvil.server
from anvil import *

from ._anvil_designer import Form1Template


class Form1(Form1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        doc_url = f"{anvil.server.get_app_origin()}/_/theme/Docs/QuickStart.md"
        with open(doc_url, "r") as file:
            self.rich_text_1.content = file.read()
