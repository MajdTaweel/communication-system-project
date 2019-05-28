import glob
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
from scipy.io import wavfile

from AudioSignal import AudioSignal
from main import filter_and_plot

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from matplotlib.figure import Figure

audio_signals = {}


class MainWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        main_window.setObjectName("main_window")
        self.centralwidget = QtWidgets.QWidget(main_window)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.clicked.connect(self.plot_signal)
        self.progress_bar = QtWidgets.QProgressBar(self.centralwidget)
        self.horizontal_layout_widget = QtWidgets.QWidget(self.centralwidget)
        self.horizontal_layout = QtWidgets.QHBoxLayout(self.horizontal_layout_widget)
        self.horizontal_layout.setContentsMargins(0, 0, 0, 0)
        self.percentage_label = QtWidgets.QLabel(self.horizontal_layout_widget)
        self.percentage_label.setText("X% (0 - 100):")
        self.percentage_tf = QtWidgets.QLineEdit(self.horizontal_layout_widget)
        self.percentage_tf.setFixedWidth(25)
        self.regex_validator = QtGui.QRegExpValidator(QtCore.QRegExp("[0-9]{2}"), self.percentage_tf)
        self.percentage_tf.setValidator(self.regex_validator)
        self.horizontal_layout.addWidget(self.percentage_label)
        self.horizontal_layout.addWidget(self.percentage_tf)

        width, height = 300, 155
        rect = QtCore.QRect(20, 20, 271, 16)
        y_coordinate = 70

        self.radioButton = []
        i = 0

        for file in glob.glob('*.wav'):
            sr, data = wavfile.read(file)
            audio_signals[file[:-4]] = AudioSignal(file[:-4], sr, data)
            self.radioButton.append(QtWidgets.QRadioButton(self.verticalLayoutWidget))
            self.radioButton[i].setObjectName("radioButton")
            self.verticalLayout.addWidget(self.radioButton[i])
            i += 1
            rect.setHeight(rect.height() + 27)
            height += 27
            y_coordinate += 27

        self.verticalLayoutWidget.setGeometry(rect)
        main_window.resize(width, height)
        self.pushButton.setGeometry(QtCore.QRect(210, y_coordinate, 75, 23))
        self.horizontal_layout_widget.setGeometry(
            QtCore.QRect(20, y_coordinate - 2, self.horizontal_layout_widget.width(),
                         self.horizontal_layout_widget.height()))
        self.progress_bar.setGeometry(QtCore.QRect(70, y_coordinate + 30, 180, 10))
        main_window.setMaximumSize(width, height)
        main_window.setMinimumSize(width, height)
        self.progress_bar.setVisible(False)
        self.timer = QtCore.QBasicTimer()
        self.step = 0
        main_window.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 300, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuInfo = QtWidgets.QMenu(self.menubar)
        self.menuInfo.setObjectName("menuInfo")
        main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        self.statusbar.setObjectName("statusbar")
        main_window.setStatusBar(self.statusbar)
        self.actionQuit = QtWidgets.QAction(main_window)
        self.actionQuit.setObjectName("actionQuit")
        self.actionQuit.triggered.connect(self.quit)
        self.actionAbout = QtWidgets.QAction(main_window)
        self.actionAbout.setObjectName("actionAbout")
        self.actionAbout.triggered.connect(self.about)
        self.menuFile.addAction(self.actionQuit)
        self.menuInfo.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuInfo.menuAction())
        self.translate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)

    def translate_ui(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "Communication Systems"))

        i = 0
        for key in audio_signals:
            self.radioButton[i].setText(_translate("main_window", key))
            i += 1

        self.pushButton.setText(_translate("main_window", "Filter and Plot"))
        self.menuFile.setTitle(_translate("main_window", "File"))
        self.menuInfo.setTitle(_translate("main_window", "Info"))
        self.actionQuit.setText(_translate("main_window", "Quit"))
        self.actionAbout.setText(_translate("main_window", "About"))

    def plot_signal(self):
        self.percentage_tf.setEnabled(False)
        self.step = 0
        self.timer.start(100, self)

    def timerEvent(self, event):
        if self.step >= 100:
            self.timer.stop()
            self.progress_bar.setVisible(False)
            return
        if self.step == 0:
            key = ""
            for rb in self.radioButton:
                self.step += 1
                self.progress_bar.setValue(self.step)
                if rb.isChecked():
                    key = rb.text()
                    break
            if key != "":
                self.progress_bar.setVisible(True)
                self.step += 1
                self.progress_bar.setValue(self.step)
                per, bw, animate = filter_and_plot(key, audio_signals[key], int(self.percentage_tf.text()), self.step,
                                                   self.progress_bar)
                self.step += 100 - self.step
                self.progress_bar.setValue(self.step)
                BandwidthDialog(key, per, bw)
            self.percentage_tf.setEnabled(True)

    @staticmethod
    def quit():
        sys.exit()

    @staticmethod
    def about():
        AboutDialog()


class BandwidthDialog(QtWidgets.QWidget):

    def __init__(self, key, percentage, bandwidth):
        super().__init__()
        self.title = 'Bandwidth'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 200
        self.key = key
        self.percentage = percentage
        self.bandwidth = bandwidth
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        QtWidgets.QMessageBox.question(self, self.key, str(self.percentage * 100) + "% Energy Bandwidth: \n\n"
                                       + str(self.bandwidth) + " kHz\n", QtWidgets.QMessageBox.Ok)
        self.show()


class AboutDialog(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'About'
        self.left = 10
        self.top = 10
        self.width = 320
        self.height = 200
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        QtWidgets.QMessageBox.question(self, "About", "Team members:\n\n" + "Majd Taweel\t1161422\n" +
                                       "Ibrahim Mualla\t1160346\n" + "Yazan Yahya\t1162259\n",
                                       QtWidgets.QMessageBox.Ok)
        self.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mw = QtWidgets.QMainWindow()
    ui = MainWindow(mw)
    mw.show()
    sys.exit(app.exec_())
