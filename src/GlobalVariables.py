import os

class CONFIG():
    def __init__(self):
        self.NODE_DIAMETER = 10
        self.LINE_WIDTH = 8
        self.DILATION_FACTOR_DATE = 500
        self.DILATION_FACTOR_HEIGHT = 100
        self.SESSION_NAME = ""
        self.DATA_PATH = os.path.join(os.path.dirname(__file__), "..", "saves")
        self.BG_COLOR = 'lightgray'
        self.NODE_DEFAULT_COLOR = 'white'
        self.FONT_DEFAULT_COLOR = 'black'