import anvil.server
from anvil import *

from ._anvil_designer import Form1Template


class Form1(Form1Template):
    def __init__(self, **properties):
        # Set Form properties and Data Bindings.
        self.init_components(**properties)

        # Any code you write here will run before the form opens.
        doc_content = anvil.server.call('get_file_content')
        self.rich_text_1.content = doc_content
