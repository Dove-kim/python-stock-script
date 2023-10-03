from kiwoom.kiwoom import Kiwoom

import sys
from PyQt5.QtWidgets import *

class Ui_class():
    def __init__(self):
        print("ui class")

        self.app = QApplication(sys.argv)

        window = Kiwoom()
        window.show()

        self.app.exec_()