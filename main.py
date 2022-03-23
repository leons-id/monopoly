from model import Model
from controller import Controller
from util import Stylesheet_1
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import rsrc


def main():
    app = QApplication(sys.argv)
#   app.setStyleSheet(stylesheet)
    model = Model()
    controller = Controller(model)
    app.setStyleSheet(Stylesheet_1)
    app.exec_()


if __name__ == '__main__':
    sys.exit(main())
    
    
    
