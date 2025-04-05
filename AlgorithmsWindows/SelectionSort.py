from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QPushButton, QLabel, QLineEdit, QFrame,
                           QGraphicsView, QGraphicsScene, QGraphicsItem, QSpinBox)
from PyQt5.QtCore import Qt, QTimer, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QBrush, QPalette
import random, sys



class BarItem(QGraphicsItem):
    pass


class SelectionSort(QMainWindow):
    pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = SelectionSort()
    window.show()
    sys.exit(app.exec_())