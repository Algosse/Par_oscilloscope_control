"""
    Debut d'une librairie pour séparer les programmes du Par du reste du main.
    J'ai rencontré des problèmes avec cette séparation. J'ai donc conservé un seul fichier main.
    Ce fichier est une archive

"""


from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
import cv2
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from PyQt5.QtWidgets import QWidget
import numpy as np


def initialiseCamera(window):
    availableCameras = []

    for i in range(5):
        cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
        if cap != None and cap.isOpened():
            availableCameras.append(i)
            cap.release()

    window.ui.CameraSelect.clear()
    for camera in availableCameras:
        window.ui.CameraSelect.addItem(str(camera))


class VideoThread(QThread):

    def __init__(self):
        super().__init__()
        self.running = True

    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        while self.running:
            ret, cv_img = cap.read()
            if ret:
                self.change_pixmap_signal.emit(cv_img)


class DisplayCamera(QWidget):
    def __init__(self, target):
        super().__init__()
        self.labelTarget = target

        self.display_width = 281
        self.display_height = 251

        # create the video capture thread
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.labelTarget.setPixmap(qt_img)

    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(
            rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(
            self.display_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
