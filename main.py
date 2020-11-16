# -*- coding: utf-8 -*-

import sys
import os
import visa
import Oscilloscope_control as ui_osc
import time
from Utils import ui_test
from Acq_script import nucleo_acquisition
from Acq_script import test_acquisition
from PyQt5 import QtWidgets, QtCore
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread, QPoint
import cv2
import numpy as np


class MyWindow(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        QtWidgets.QMainWindow.__init__(self)
        self.ui = ui_osc.Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.btn_disconnect.setEnabled(False)
        self.ui.btn_ld_osc.setEnabled(False)
        self.ui.btn_apply.setEnabled(False)
        self.ui.actionDisconnect.setEnabled(False)
        self.ui.actionLoad_from_oscilloscope.setEnabled(False)
        self.ui.lbl_cmd.setEnabled(False)
        self.ui.cmd_line.setEnabled(False)
        self.ui.btn_send_cmd.setEnabled(False)
# =============================================================================
#   Variables
# =============================================================================
        self.oscilloscope = None
# =============================================================================
#   other initialization
# =============================================================================
        self.update_res()

# =============================================================================
#   Connection of menu to actions
# =============================================================================
        self.ui.actionConnect.triggered.connect(self.instrument_connect)
        self.ui.actionDisconnect.triggered.connect(self.instrument_disconnect)
        self.ui.actionLoad_from_file_2.triggered.connect(self.load_file)
        self.ui.actionLoad_from_oscilloscope.triggered.connect(
            self.read_instrument)
        self.ui.actionSave.triggered.connect(self.save)
        self.ui.actionQuit.triggered.connect(self.close)
# =============================================================================
#       Help Menu connection
# =============================================================================
        self.ui.actionAcquisition.triggered.connect(
            lambda: os.startfile("Help/Acquisition.pdf"))
        self.ui.actionAlias.triggered.connect(
            lambda: os.startfile("Help/Alias.pdf"))
        self.ui.actionCalibrate.triggered.connect(
            lambda: os.startfile("Help/Calibrate.pdf"))
        self.ui.actionCursor.triggered.connect(
            lambda: os.startfile("Help/Cursor.pdf"))
        self.ui.actionDiagnostic.triggered.connect(
            lambda: os.startfile("Help/Diagnostic.pdf"))
        self.ui.actionDisplay.triggered.connect(
            lambda: os.startfile("Help/Display.pdf"))
        self.ui.actionFile_System.triggered.connect(
            lambda: os.startfile("Help/File_System.pdf"))
        self.ui.actionHardcopy.triggered.connect(
            lambda: os.startfile("Help/Hardcopy.pdf"))
        self.ui.actionHistogram.triggered.connect(
            lambda: os.startfile("Help/Histogram.pdf"))
        self.ui.actionHorizontal.triggered.connect(
            lambda: os.startfile("Help/Horizontal.pdf"))
        self.ui.actionMath.triggered.connect(
            lambda: os.startfile("Help/Math.pdf"))
        self.ui.actionMeasurement.triggered.connect(
            lambda: os.startfile("Help/Measurement.pdf"))
        self.ui.actionMiscellaneous.triggered.connect(
            lambda: os.startfile("Help/Miscellaneous.pdf"))
        self.ui.actionSave_and_Recall.triggered.connect(
            lambda: os.startfile("Help/Save_and_Reccal.pdf"))
        self.ui.actionStatus_and_Error.triggered.connect(
            lambda: os.startfile("Help/Status_and_Error.pdf"))
        self.ui.actionTrigger.triggered.connect(
            lambda: os.startfile("Help/Trigger.pdf"))
        self.ui.actionVertical.triggered.connect(
            lambda: os.startfile("Help/Vertical.pdf"))
        self.ui.actionWaveform_Transfert.triggered.connect(
            lambda: os.startfile("Help/Waveform_Transfert.pdf"))
        self.ui.actionZoom.triggered.connect(
            lambda: os.startfile("Help/Zoom.pdf"))


# =============================================================================
#   Connection of button actions
# =============================================================================
        self.ui.btn_connect.clicked.connect(self.instrument_connect)
        self.ui.btn_disconnect.clicked.connect(self.instrument_disconnect)
        self.ui.btn_ld_file.clicked.connect(self.load_file)
        self.ui.btn_ld_osc.clicked.connect(self.read_instrument)
        self.ui.btn_save.clicked.connect(self.save)
        self.ui.btn_apply.clicked.connect(self.apply_changes)
        self.ui.btn_send_cmd.clicked.connect(self.send_cmd)
        self.ui.btn_acq.clicked.connect(self.start_acquisition)

# =============================================================================
#   Other connection
# =============================================================================
        self.ui.hor_sca.currentIndexChanged.connect(self.update_res)
        self.ui.channel1.toggled.connect(self.update_res)
        self.ui.channel2.toggled.connect(self.update_res)
        self.ui.channel3.toggled.connect(self.update_res)
        self.ui.channel4.toggled.connect(self.update_res)
        self.ui.acq_grp.toggled.connect(self.active_acq)
        self.ui.check_data_start.stateChanged.connect(
            lambda: self.ui.data_start.setEnabled(self.ui.check_data_start.isChecked()))
        self.ui.check_data_stop.stateChanged.connect(
            lambda: self.ui.data_stop.setEnabled(self.ui.check_data_stop.isChecked()))
        self.ui.hor_res.currentIndexChanged.connect(self.data_stop_update)
        self.ui.acq_script.currentIndexChanged.connect(self.acq_script_param)


# =============================================================================
#   Run video
# =============================================================================

        self.playCamera = True
        self.cameraScreenShot = QPixmap()
        self.cameraScreenShotRef = QPixmap()
        self.initialiseCamera()
        self.display_width = self.ui.CameraDisplay.size().width()
        self.display_height = self.ui.CameraDisplay.size().height()
        # Draw on image
        self.drawing = False
        self.globalDrawing = True

        # Draw Rect
        self.resetRectangle()
        self.isPlacingCorner = False
        self.placingCorner = None
        
        # Calibrate
        self.isPlacingCalibrate = False
        self.cornerCalibrateNumber = 0
        
        # Attack
        self.ui.AttackResolution.setValue(1)
        self.ui.AttackResolution.setMinimum(0.1)
        self.ui.AttackResolution.setSingleStep(0.1)
        self.ui.StartAttack.setEnabled(False)
        
        # Printer caracteristics
        self.printerHeigh = 100
        self.printerWidth = 100

        # create the video capture thread
        self.thread = VideoThread(0)
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()
        
        self.corners = {
            'tl': QPoint(0, 0),
            'tr': QPoint(0, 0),
            'bl': QPoint(0, 0),
            'br': QPoint(0, 0)
        }
        self.calibrationCorners = {
            'tl': QPoint(-1, -1),
            'tr': QPoint(-1, -1),
            'bl': QPoint(-1, -1),
            'br': QPoint(-1, -1)
        }
        self.cornerNames = ['tl','tr','br','bl']
        
        

# =============================================================================
#   Circuit Recognition Connections
# =============================================================================

        self.ui.CameraSelect.currentIndexChanged.connect(self.changeCam)
        self.ui.toogleCamera.clicked.connect(self.toogleCamera)
        self.ui.placeCornerTL.clicked.connect(
            lambda: self.placeCorner('tl'))
        self.ui.placeCornerTR.clicked.connect(
            lambda: self.placeCorner('tr'))
        self.ui.placeCornerBL.clicked.connect(
            lambda: self.placeCorner('bl'))
        self.ui.resetRectangle.clicked.connect(self.resetRectangle)
        self.ui.DrawRectangle.clicked.connect(lambda : self.drawRectangle(self.corners))
        self.ui.CalibrateCam.clicked.connect(self.calibrateCam)
        self.ui.StartAttack.clicked.connect(self.startAttack)
        
# =============================================================================
#   Functions
# =============================================================================

    def send_cmd(self):
        cmd = self.ui.cmd_line.text()
        if cmd[len(cmd) - 1] == '?':
            self.ui.log.append(self.oscilloscope.query(cmd) + "\n")
            with open("log.txt", "w") as log:
                log.write(self.ui.log.toPlainText())
        else:
            self.oscilloscope.write(cmd)

    def instrument_connect(self):
        rm = visa.ResourceManager()
        try:
            self.oscilloscope = rm.open_resource(self.ui.osc_name.text())
            self.ui.btn_disconnect.setEnabled(True)
            self.ui.btn_ld_osc.setEnabled(True)
            self.ui.btn_apply.setEnabled(True)
            self.ui.actionDisconnect.setEnabled(True)
            self.ui.actionLoad_from_oscilloscope.setEnabled(True)
            self.ui.lbl_cmd.setEnabled(True)
            self.ui.cmd_line.setEnabled(True)
            self.ui.btn_send_cmd.setEnabled(True)
            self.ui.groupBox.setEnabled(True)
            self.ui.data_stop.setText(self.oscilloscope.query("DATa:STOP?"))
            self.ui.log.append('connected to ' + self.ui.osc_name.text())
            with open("log.txt", "w") as log:
                log.write(self.ui.log.toPlainText())
            return 1
        except:
            self.ui.log.append('oscilloscope connection problem')
            with open("log.txt", "w") as log:
                log.write(self.ui.log.toPlainText())
            return 0

    def instrument_disconnect(self):
        try:
            self.oscilloscope.close()
            self.oscilloscope = None
            self.ui.btn_disconnect.setEnabled(False)
            self.ui.btn_ld_osc.setEnabled(False)
            self.ui.btn_apply.setEnabled(False)
            self.ui.actionDisconnect.setEnabled(False)
            self.ui.actionLoad_from_oscilloscope.setEnabled(False)
            self.ui.lbl_cmd.setEnabled(False)
            self.ui.cmd_line.setEnabled(False)
            self.ui.btn_send_cmd.setEnabled(False)
            self.ui.groupBox.setEnabled(False)
            self.ui.log.append('disconnected from' + self.ui.osc_name.text())
            with open("log.txt", "w") as log:
                log.write(self.ui.log.toPlainText())
        except:
            self.ui.log.append('oscilloscope disconnection problem')
            with open("log.txt", "w") as log:
                log.write(self.ui.log.toPlainText())

    def load_file(self):
        if self.ui.check_vert_app.isChecked():
            self.load_vertical()
        if self.ui.check_hor_app.isChecked():
            self.load_horizontal()
        if self.ui.check_trig_app.isChecked():
            self.load_trigger()

    def read_instrument(self):
        self.ui.log.append('read_instrument : not implemented')
        with open("log.txt", "w") as log:
            log.write(self.ui.log.toPlainText())

    def save(self):
        if self.ui.check_vert_app.isChecked():
            self.save_vertical()
        if self.ui.check_hor_app.isChecked():
            self.save_horizontal()
        if self.ui.check_trig_app.isChecked():
            self.save_trigger()

    def close(self):
        QtCore.QCoreApplication.instance().quit()

    def apply_changes(self):
        self.ui.log.append('apply change to instrument')
        with open("log.txt", "w") as log:
            log.write(self.ui.log.toPlainText())
        if self.ui.check_vert_app.isChecked():
            self.apply_vertical()
        if self.ui.check_hor_app.isChecked():
            self.apply_horizontal()
        if self.ui.check_trig_app.isChecked():
            self.apply_trigger()
        if self.ui.check_wfm_app.isChecked():
            self.apply_wfm()

    def update_res(self):
        self.ui.hor_res.clear()
        index = self.ui.hor_sca.currentIndex()
        f = open('dictionnaries/resolutions.txt', 'r')
        for i in range(0, index + 1):
            s = (f.readline()).rstrip()
        f.close()
        del f
        del index
        tmp = s.split(';')
        del s
        act_ch = self.activated_channel()
        if act_ch > 0:
            for i in range(0, len(tmp) - (self.activated_channel() - 1)):
                self.ui.hor_res.addItem(tmp[i])

    def data_stop_update(self):
        if (not(self.ui.data_stop.isEnabled()) and type(self.oscilloscope) != type(None)):
            self.ui.data_stop.setText(
                self.oscilloscope.query("HORizontal:RECOrdlength?"))

    def activated_channel(self):
        res = self.ui.channel1.isChecked() + self.ui.channel2.isChecked() + \
            self.ui.channel3.isChecked()
        if (res < 3):
            res = res + self.ui.channel4.isChecked()
        return res

    def apply_vertical(self):
        self.ui.log.append('apply vertical settings')
        with open("log.txt", "w") as log:
            log.write(self.ui.log.toPlainText())
        # Channel 1
        if self.ui.channel1.isChecked():
            self.oscilloscope.write("SELECT:CH1 ON")
            self.oscilloscope.write("CH1:SCA " + self.ui.ch1_sca.currentText())
            self.oscilloscope.write("CH1:POS " + self.ui.ch1_pos.text())
        else:
            self.oscilloscope.write("SELECT:CH1 OFF")
        # Channel 2
        if self.ui.channel2.isChecked():
            self.oscilloscope.write("SELECT:CH2 ON")
            self.oscilloscope.write("CH2:SCA " + self.ui.ch2_sca.currentText())
            self.oscilloscope.write("CH2:POS " + self.ui.ch2_pos.text())
        else:
            self.oscilloscope.write("SELECT:CH2 OFF")
        # Channel 3
        if self.ui.channel3.isChecked():
            self.oscilloscope.write("SELECT:CH3 ON")
            self.oscilloscope.write("CH3:SCA " + self.ui.ch3_sca.currentText())
            self.oscilloscope.write("CH3:POS " + self.ui.ch3_pos.text())
        else:
            self.oscilloscope.write("SELECT:CH3 OFF")
        # Channel 4
        if self.ui.channel4.isChecked():
            self.oscilloscope.write("SELECT:CH4 ON")
            self.oscilloscope.write("CH4:SCA " + self.ui.ch4_sca.currentText())
            self.oscilloscope.write("CH4:POS " + self.ui.ch4_pos.text())
        else:
            self.oscilloscope.write("SELECT:CH4 OFF")

    def apply_horizontal(self):
        self.ui.log.append('apply horizontal settings')
        with open("log.txt", "w") as log:
            log.write(self.ui.log.toPlainText())
        self.oscilloscope.write("HOR:POS " + self.ui.hor_pos.text())
        self.oscilloscope.write("HOR:MAI:SCA " + self.ui.hor_sca.currentText())
        if (len(self.ui.hor_res.currentText()) > 0):
            self.oscilloscope.write("HOR:RESO " + str(10 * float(
                self.ui.hor_res.currentText()) * float(self.ui.hor_sca.currentText())))

    def apply_trigger(self):
        self.ui.log.append('apply trigger settings')
        with open("log.txt", "w") as log:
            log.write(self.ui.log.toPlainText())
        self.oscilloscope.write(
            "TRIGger:A:EDGE:SOU " + self.ui.trig_sou.currentText())
        self.oscilloscope.write(
            "TRIGger:A:EDGE:COUP " + self.ui.trig_cou.currentText())
        self.oscilloscope.write(
            "TRIGger:A:EDGE:SLO " + self.ui.trig_slo.currentText())
        self.oscilloscope.write("TRIGger:A:LEVel " + self.ui.trig_lvl.text())

    def apply_wfm(self):
        self.ui.log.append('apply Waveform parameter settings')
        with open("log.txt", "w") as log:
            log.write(self.ui.log.toPlainText())
        self.oscilloscope.write(
            "DATa:SOUrce " + self.ui.data_sou.currentText())
        self.oscilloscope.write(
            "DATa:ENCdg " + self.ui.data_encoding.currentText())
        self.oscilloscope.write("DATa:STARt " + self.ui.data_start.text())
        self.oscilloscope.write("DATa:STOP " + self.ui.data_stop.text())

    def save_vertical(self):
        f = open('dictionnaries/vertical_parameters.txt', 'w')
        if self.ui.channel1.isChecked():
            f.write("channel1;1\n")
        else:
            f.write("channel1;0\n")
        f.write("ch1_pos;" + self.ui.ch1_pos.text() + "\n")
        f.write("ch1_sca;" + str(self.ui.ch1_sca.currentIndex()) + "\n")
        if self.ui.channel2.isChecked():
            f.write("channel2;1\n")
        else:
            f.write("channel2;0\n")
        f.write("ch2_pos;" + self.ui.ch2_pos.text() + "\n")
        f.write("ch2_sca;" + str(self.ui.ch2_sca.currentIndex()) + "\n")
        if self.ui.channel3.isChecked():
            f.write("channel3;1\n")
        else:
            f.write("channel3;0\n")
        f.write("ch3_pos;" + self.ui.ch3_pos.text() + "\n")
        f.write("ch3_sca;" + str(self.ui.ch3_sca.currentIndex()) + "\n")
        if self.ui.channel4.isChecked():
            f.write("channel4;1\n")
        else:
            f.write("channel4;0\n")
        f.write("ch4_pos;" + self.ui.ch4_pos.text() + "\n")
        f.write("ch4_sca;" + str(self.ui.ch4_sca.currentIndex()) + "\n")
        f.close()

    def save_horizontal(self):
        f = open('dictionnaries/horizontal_parameters.txt', 'w')
        f.write("hor_pos;" + self.ui.hor_pos.text() + "\n")
        f.write("hor_sca;" + str(self.ui.hor_sca.currentIndex()) + "\n")
        f.write("hor_res;" + str(self.ui.hor_res.currentIndex()) + "\n")
        f.close()

    def save_trigger(self):
        f = open('dictionnaries/trigger_parameters.txt', 'w')
        f.write("trig_sou;" + str(self.ui.trig_sou.currentIndex()) + "\n")
        f.write("trig_cou;" + str(self.ui.trig_cou.currentIndex()) + "\n")
        f.write("trig_slo;" + str(self.ui.trig_slo.currentIndex()) + "\n")
        f.write("trig_lvl;" + self.ui.trig_lvl.text() + "\n")
        f.close()

    def load_vertical(self):
        f = open('dictionnaries/vertical_parameters.txt', 'r')
        s = f.readlines()
        f.close()
        # Channel 1
        t = (s[0].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setChecked(int(" + t[1] + "))")
        t = (s[1].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setText(str(" + t[1] + "))")
        t = (s[2].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setCurrentIndex(int(" + t[1] + "))")
        # Channel 2
        t = (s[3].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setChecked(int(" + t[1] + "))")
        t = (s[4].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setText(str(" + t[1] + "))")
        t = (s[5].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setCurrentIndex(int(" + t[1] + "))")
        # Channel 3
        t = (s[6].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setChecked(int(" + t[1] + "))")
        t = (s[7].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setText(str(" + t[1] + "))")
        t = (s[8].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setCurrentIndex(int(" + t[1] + "))")
        # Channel 4
        t = (s[9].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setChecked(int(" + t[1] + "))")
        t = (s[10].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setText(str(" + t[1] + "))")
        t = (s[11].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setCurrentIndex(int(" + t[1] + "))")

    def load_horizontal(self):
        f = open('dictionnaries/horizontal_parameters.txt', 'r')
        s = f.readlines()
        f.close()
        t = (s[0].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setText(str(" + t[1] + "))")
        t = (s[1].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setCurrentIndex(int(" + t[1] + "))")
        t = (s[2].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setCurrentIndex(int(" + t[1] + "))")

    def load_trigger(self):
        f = open('dictionnaries/trigger_parameters.txt', 'r')
        s = f.readlines()
        f.close()
        t = (s[0].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setCurrentIndex(int(" + t[1] + "))")
        t = (s[1].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setCurrentIndex(int(" + t[1] + "))")
        t = (s[2].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setCurrentIndex(int(" + t[1] + "))")
        t = (s[3].rstrip()).split(';')
        eval("self.ui." + t[0] + ".setText(str(" + t[1] + "))")

    def active_acq(self):
        self.ui.acq_script.clear()
        self.ui.parameter_edit.clear()
        if self.ui.acq_grp.isEnabled():
            for file in os.listdir("Acq_script/"):
                if file.endswith(".py"):
                    self.ui.acq_script.addItem(file[0:len(file) - 3])

    def acq_script_param(self):
        if len(self.ui.acq_script.currentText()) > 0:
            param_file = open(
                "Acq_script/" + self.ui.acq_script.currentText() + ".dat", "r")
            l = param_file.readlines()
            param_file.close()
            self.ui.parameter_edit.clear()
            for i in range(0, len(l)):
                self.ui.parameter_edit.append(l[i].rstrip())

    def start_acquisition(self):
        if type(self.oscilloscope) != type(None):
            self.ui.log.append('start acquisition')
            with open("log.txt", "w") as log:
                log.write(self.ui.log.toPlainText())
            with open("Acq_script/" + self.ui.acq_script.currentText() + ".dat", "w") as p:
                p.write(self.ui.parameter_edit.toPlainText())
# =============================================================================
#             self.acquisition= eval(self.ui.acq_script.currentText() + ".External()")
#             self.acquisition.countChanged.connect(self.onCountChanged)
#             self.acquisition.start(self)
# =============================================================================
            eval(self.ui.acq_script.currentText() + ".run(self)")
            self.ui.log.append('Acquisition done')

    def onCountChanged(self, val):
        self.ui.progressBar.setValue(val)

    def initialiseCamera(self):
        availableCameras = []

        for i in range(5):
            cap = cv2.VideoCapture(i, cv2.CAP_DSHOW)
            if cap != None and cap.isOpened():
                availableCameras.append(i)
                cap.release()

        self.ui.CameraSelect.clear()
        for camera in availableCameras:
            self.ui.CameraSelect.addItem(str(camera))

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""

        qt_img = self.convert_cv_qt(cv_img)
        self.cameraScreenShot = qt_img
        self.cameraScreenShotRef = qt_img.copy()
        self.ui.CameraDisplay.setPixmap(qt_img)

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

    def changeCam(self):
        """ Reboot the thread with the right cam index"""
        cam = self.ui.CameraSelect.currentIndex()

        self.thread.stop()
        self.thread = VideoThread(cam)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

        if not self.playCamera:
            self.toogleCamera()

    def closeEvent(self, event):
        """ Method called when the window is closed """
        self.thread.stop()
        event.accept()

    def toogleCamera(self, pause = False):
        if self.playCamera or pause:
            self.thread.pause()
            self.playCamera = False
        else:
            self.thread.resume()
            self.playCamera = True        

        text = ""
        if self.playCamera:
            text = 'Take Picture'
        else:
            text = 'Restore Camera'
        self.ui.toogleCamera.setText(text)

    def mousePressEvent(self, event):
        """ Place a corner of a rectangle """
        if event.button() == Qt.LeftButton:
            self.point = event.pos()
            self.point = self.ui.CameraDisplay.mapFrom(
                self.ui.centralwidget, event.pos())
            # offset of 21 because the Widget centralWidget is not at 0,0 of the main window
            self.point.setY(self.point.y() - 21)
            
            if self.isPlacingCorner:    # Define processor location
                self.corners[self.placingCorner] = self.point
                self.updateRectLabels()
                self.isPlacingCorner = False
            
            if self.isPlacingCalibrate: # Calibrate Camera
                self.calibrationCorners[self.cornerNames[self.cornerCalibrateNumber]] = self.point
                self.cornerCalibrateNumber += 1
                if self.cornerCalibrateNumber == 4:
                    self.drawRectangle(self.calibrationCorners, Qt.yellow)
                    self.isPlacingCalibrate = False
                    self.ui.CalibrateCam.setText("Re-calibrate")
                    self.ui.StartAttack.setEnabled(True)
                

    def placeCorner(self, corner):
        self.isPlacingCorner = True
        self.placingCorner = corner

    def updateRectLabels(self):
        self.ui.cornerTLX.setText(str(self.corners['tl'].x()))
        self.ui.cornerTLY.setText(str(self.corners['tl'].y()))
        self.ui.cornerTRX.setText(str(self.corners['tr'].x()))
        self.ui.cornerTRY.setText(str(self.corners['tr'].y()))
        self.ui.cornerBLX.setText(str(self.corners['bl'].x()))
        self.ui.cornerBLY.setText(str(self.corners['bl'].y()))

    def resetRectangle(self):
        self.corners = {
            'tl': QPoint(-1, -1),
            'tr': QPoint(-1, -1),
            'bl': QPoint(-1, -1),
            'br': QPoint(-1, -1)
        }
        self.updateRectLabels()
        self.ui.CameraDisplay.setPixmap(self.cameraScreenShotRef)
        self.cameraScreenShot = self.cameraScreenShotRef.copy()

    def drawRectangle(self, rectangle, color = Qt.red):
        painter = QPainter(self.cameraScreenShot)
        painter.setPen(QPen(color, 2,
                            Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))

        if rectangle['br'] == QPoint(0,0):
            newX = rectangle['bl'].x() - rectangle['tl'].x() + \
                rectangle['tr'].x()
            newY = rectangle['tr'].y() - rectangle['tl'].y() + \
                rectangle['bl'].y()

            rectangle["br"] = QPoint(newX, newY)

        painter.drawLine(rectangle['tl'], rectangle['tr'])
        painter.drawLine(rectangle['tr'], rectangle['br'])
        painter.drawLine(rectangle['br'], rectangle['bl'])
        painter.drawLine(rectangle['tl'], rectangle['bl'])

        self.ui.CameraDisplay.setPixmap(self.cameraScreenShot)
    
    def calibrateCam(self):
        print("Go to (0,0)")
        self.toogleCamera(True)
        self.ui.CameraDisplay.setPixmap(self.cameraScreenShotRef)
        self.cameraScreenShot = self.cameraScreenShotRef.copy()
        
        self.calibrationCorners = {
            'tl': QPoint(-1, -1),
            'tr': QPoint(-1, -1),
            'bl': QPoint(-1, -1),
            'br': QPoint(-1, -1)
        }

        self.isPlacingCalibrate = True
        self.cornerCalibrateNumber = 0
        
        self.ui.CalibrateCam.setText("Calibrating...")
        
    def startAttack(self):
        print('start')
        resolution = self.ui.AttackResolution.value()
        print(resolution)
        
        
class VideoThread(QThread):
    """ Thread displaying opencv VideoCapture (allow the interaction with the window while displaying) """

    def __init__(self, cam):
        super().__init__()
        self.running = True
        self.cam = cam
        self.play = True

    change_pixmap_signal = pyqtSignal(np.ndarray)

    def run(self):
        # capture from web cam
        cap = cv2.VideoCapture(self.cam, cv2.CAP_DSHOW)
        while self.running:
            while self.play:
                ret, cv_img = cap.read()
                if ret:
                    # Send the image thru a slot to MyWindow.update_image
                    self.change_pixmap_signal.emit(cv_img)

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self.play = False
        self.running = False
        self.wait()

    def pause(self):
        self.play = False

    def resume(self):
        self.play = True


if __name__ == '__main__':
    test = 0
    app = QtWidgets.QApplication(sys.argv)
    window = MyWindow()
    window.show()
    if test:
        ui_test.vertival_test(window, 1)
        time.sleep(1)
        ui_test.vertival_test(window, 2)
        time.sleep(1)
        ui_test.vertival_test(window, 3)
        time.sleep(1)
        ui_test.vertival_test(window, 4)
        time.sleep(1)
        ui_test.Trigger_test(window)
        time.sleep(1)
        ui_test.horizontal_test(window)
    sys.exit(app.exec_())
