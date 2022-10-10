import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPainter, QPixmap, QPen, QColor, QPolygon, QBrush, QPalette
from PyQt5.QtCore import Qt, QPoint, QRectF, QRect
from PyQt5.Qt import QSize, QImageReader
from PyQt5 import QtCore
from PyQt5 import QtWidgets, QtGui
from time import time
import math

# QLabel for displaying picture and painting
class MyLabel(QLabel):

    def __init__(self, parent=None):
        super(MyLabel, self).__init__(parent)
        self.isShow = False
        self.points = []

        self.move = False
        self.left_clicked = False
        self.right_clicked = False

        self.mode = '0'

    def initDrawing(self, img, label_w, label_h):
        self.pix = img  # CURRENT PIC
        if self.mode == '1':
            self.oriPix = self.pix.copy()
            self.mode = '0'
        self.tmpPix = self.pix.copy()  # LATEST ONE

        self.lastPoint = QPoint()
        self.endPoint = QPoint()
        self.position = QSize((label_w - self.pix.width()) / 2, (label_h - self.pix.height()) / 2)
        self.offset = QPoint(self.position.width(), self.position.height())

        self.move = False
        self.isRelease = False
        self.right_clicked = False
        self.left_clicked = False
        self.newpoint = False
        self.update()

    def drawevent(self):
        painter = QPainter(self)
        painter.begin(self)
        painter.drawPixmap(self.position.width(), self.position.height(), self.pix)
        painter.end()

    def show(self, value):
        if isinstance(value, bool):
            self.isShow = value

    def paintEvent(self, event):
        super().paintEvent(event)
        if self.isShow:
            self.drawevent()

    # draw points on picture
    def drawpoints(self):
        self.pix = self.oriPix.copy()
        pp = QPainter(self.pix)
        pp.setPen(QPen(Qt.yellow, 8, Qt.SolidLine, Qt.RoundCap))

        pp.drawPoints(QtGui.QPolygonF(self.points))
        #print(self.points)
        self.update()

    def drawpolygon(self):
        pp = QPainter(self.pix)
        pp.setPen(QPen(Qt.white, 1))
        pp.setBrush(Qt.white)
        rect = QRect(0, 0, self.pix.width(), self.pix.height())
        pp.drawRect(rect)

        pp.setPen(QPen(Qt.black, 1))
        pp.setBrush(Qt.black)
        pp.drawPolygon(QPolygon(self.points))

    def mousePressEvent(self, event):
        # super().mousePressEvent(self, event)
        # when you want to move a point
        if self.isShow and self.move:
            if event.buttons() == Qt.LeftButton:
                self.movePoint = event.pos() - self.offset
                self.newpoint = True

        # otherwise
        if self.isShow and not self.move:
            if event.buttons() == Qt.LeftButton:

                self.newpoint = True
                self.left_clicked = True
                self.lastPoint = event.pos() - self.offset
                self.points.append(self.lastPoint)
                # always update self.pix
                self.pix = self.tmpPix.copy()
                # draw points
                self.drawpoints()


            elif event.buttons() == QtCore.Qt.RightButton:

                self.right_clicked = True
                # draw polygon according to the given points
                self.drawpolygon()
                self.update()

    def mouseMoveEvent(self, event):
        if self.show and self.move:
            if event.buttons() == Qt.LeftButton:
                self.isMove = True
                pos_x = self.movePoint.x()
                pos_y = self.movePoint.y()
                select_point = QPoint()
                # click around the point you may want to select is fine
                for point in self.points:
                    dis_x = abs(point.x() - pos_x)
                    dis_y = abs(point.y() - pos_y)
                    #
                    if dis_x < 8 and dis_y < 8:
                        if select_point == QPoint():
                            select_point = point
                        else:
                            if abs(point.x() - select_point.x()) + abs(point.y() - select_point.y()) > dis_x + dis_y:
                                select_point = point
                try:
                    self.select_index = self.points.index(select_point)
                except ValueError:
                    QMessageBox.about(self,"Moving Point Error","Cannot find the point you may select.")

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if self.isShow and not self.move:
            if event.button() == Qt.LeftButton:
                # for updating self.pix
                self.tmpPix = self.pix

        # it is allowed to move a point when the polygon has not been drew
        if self.isShow and self.move and not self.right_clicked:
            if event.button() == Qt.LeftButton and self.isMove:
                self.points[self.select_index] = event.pos() - self.offset
                self.isRelease = True
                self.update()

    def resizeEvent(self, event):
        # super().resizeEvent(event)
        pass


class Winform(QWidget):

    def __init__(self, parent=None):
        super(Winform, self).__init__(parent)

        self.setWindowTitle("Image 'Labeler'")
        self.lastPoint = QPoint()
        self.endPoint = None
        self.points = []
        self.start_draw = False
        self.open_image = False
        self.rightc = False
        self.longside = 0  # 0 - width >= height, 1 width < height

        self.initUi()

    def initUi(self):

        desktop = QApplication.desktop()
        rect = desktop.availableGeometry()
        self.standard_width = desktop.width()
        self.standard_height = desktop.height()


        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self.setMinimumSize(desktop.width(), rect.height())

        # 外层(outer layer)
        myLayout = QHBoxLayout()
        # 内部左侧(internal left side)
        leftvbox = QVBoxLayout()
        # 内部右侧(internal right side)
        self.pix = MyLabel(self)
        # 设置大小(set pix size)
        self.pix.setGeometry(80, 0, self.width() - 80, self.height())

        #self.pix.setStyleSheet("border: 2px solid red")

        btn_size = QSize(80, 30)

        btn_clean = QPushButton(self)
        btn_clean.setText("Clean")
        btn_clean.clicked.connect(self.clean)
        btn_clean.setFixedSize(btn_size)

        btn_save = QPushButton(self)
        btn_save.setText("Save")
        btn_save.clicked.connect(self.save)
        btn_save.setFixedSize(btn_size)

        btn_open = QPushButton(self)
        btn_open.setText("Open")
        btn_open.clicked.connect(self.open)
        btn_open.setFixedSize(btn_size)

        btn_draw = QPushButton(self)
        btn_draw.setText("Draw")
        btn_draw.clicked.connect(self.draw)
        btn_draw.setFixedSize(btn_size)

        btn_move = QPushButton(self)
        btn_move.setText("Move")
        btn_move.clicked.connect(self.move)
        btn_move.setFixedSize(btn_size)

        btn_undo = QPushButton(self)
        btn_undo.setText("Undo")
        btn_undo.clicked.connect(self.undo)
        btn_undo.setFixedSize(btn_size)

        leftvbox.addWidget(btn_clean)
        leftvbox.addWidget(btn_save)
        leftvbox.addWidget(btn_open)
        leftvbox.addWidget(btn_draw)
        leftvbox.addWidget(btn_move)
        leftvbox.addWidget(btn_undo)

        leftvbox.addItem(QSpacerItem(80, self.height() - 140, QSizePolicy.Minimum, QSizePolicy.Expanding))

        leftvbox.setContentsMargins(0, 0, 0, 0)

        myLayout_w = QWidget()

        myLayout_w.setLayout(leftvbox)
        myLayout_w.setFixedWidth(80)

        myLayout.addWidget(myLayout_w)

        myLayout.addWidget(self.pix)

        self.setLayout(myLayout)

        self.offset = QPoint(0, 0)
        self.show()


    def resizeWarning(self):
        QMessageBox.information(self, "resizeWarning", "It is not allowed to resize the window after makeing "
                                                       "changes to the picture.")

    def clean(self):
        self.pix.points = []
        img = self.jpg
        self.pix.initDrawing(img, self.pix.width(), self.pix.height())
        self.start_draw = False

        self.update()

    def save(self):
        filepath, type = QFileDialog.getSaveFileName(self, 'Save File', "", "*.jpg *.png")
        self.pix.pix.save(filepath)

    def open(self):
        self.open_image = True
        self.points = []

        imgName, imgType = QFileDialog.getOpenFileName \
            (self, 'Open File', "", "*.jpg *.png * All Files(*)")
        if imgName is not None and imgName != '':
            img = QImageReader(imgName)
            print(img.size())
            if img.size().width() >= img.size().height():
                self.longside = 0
                scale = self.pix.width() / img.size().width()
                height = int(img.size().height() * scale)
                img.setScaledSize(QSize(self.pix.width(), height))
            else:
                self.longside = 1
                scale = self.height() / img.size().height()
                width = int(img.size().width() * scale)
                img.setScaledSize(QSize(width, self.height()))
            # 图片原件(original img)
            self.origin_img = img.read()
            # 显示用图(img for display)
            self.jpg = QPixmap.fromImage(self.origin_img)
            self.change_jpg = self.jpg.copy()
            self.pix.setAlignment(Qt.AlignCenter)
            self.pix.mode = '1'
            self.pix.initDrawing(self.jpg, self.pix.width(), self.pix.height())
            self.pix.show(True)
            self.update()
        else:
            self.open_image = False

    def draw(self):

        if self.open_image and not self.pix.right_clicked:
            if len(self.pix.points) > 0:
                pass
            else:
                img = self.jpg
                self.pix.initDrawing(img, self.pix.width(), self.pix.height())
                self.pix.show(True)

        if self.open_image and self.pix.right_clicked:
            img = self.jpg
            self.pix.initDrawing(img, self.pix.width(), self.pix.height())
            # 调度函数内的画点(Drawing points within a scheduling function)
            self.pix.drawpoints()
            self.pix.newpoint = False
            self.pix.right_clicked = False
            self.update()


    def move(self):
        # you should click "move" button for every time you want to move a point; you cannot continuously move points.
        if self.open_image and len(self.pix.points) > 0:
            self.pix.move = True

    # revoke the latest point
    def undo(self):
        if len(self.pix.points) > 0:
            del self.pix.points[-1]
        img = self.jpg
        self.pix.initDrawing(img, self.pix.width(), self.pix.height())
        self.pix.drawpoints()
        self.update()

    def mouseReleaseEvent(self, event):
        if self.open_image:
            if self.pix.isRelease:
                img = self.jpg
                self.pix.initDrawing(img, self.pix.width(), self.pix.height())
                self.pix.drawpoints()
                self.pix.isRelease = False
                self.update()
            else:
                pass

    def resizeEvent(self, event):
        pass

    def paintEvent(self, event):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = Winform()
    window.showMaximized()

    sys.exit(app.exec())

