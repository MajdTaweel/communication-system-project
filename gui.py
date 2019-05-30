import glob
import sys

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget
from matplotlib.animation import FuncAnimation
from scipy.io import wavfile

from AudioSignal import AudioSignal
from main import filter_and_plot, display_filtered_spectrum

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT
from DSBSC import DSBSC
import matplotlib
import matplotlib.pyplot as plt
from scipy.fftpack import *

matplotlib.rc("figure", autolayout=True)
audio_signals = {}


class MainWindow(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window

        self.central_widget = QWidget(main_window)

        self.top_h_widget = QWidget(self.central_widget)
        self.top_h_box = QtWidgets.QHBoxLayout(self.top_h_widget)

        self.verticalLayoutWidget = QWidget(self.top_h_widget)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 20, 0, 0)

        self.progress_bar = QtWidgets.QProgressBar(self.central_widget)

        self.vertical_layout_widget2 = QWidget(self.top_h_widget)
        self.vertical_layout2 = QtWidgets.QVBoxLayout(self.vertical_layout_widget2)

        self.percentage_h_widget = QWidget(self.vertical_layout_widget2)
        self.percentage_h_box = QtWidgets.QHBoxLayout(self.percentage_h_widget)

        self.percentage_label = QtWidgets.QLabel(self.percentage_h_widget)
        self.percentage_label.setText("X% (0 - 100):")

        self.percentage_tf = QtWidgets.QLineEdit(self.percentage_h_widget)
        self.percentage_tf.setFixedWidth(25)

        self.regex_validator = QtGui.QRegExpValidator(QtCore.QRegExp("[0-9]{2}"), self.percentage_tf)
        self.percentage_tf.setValidator(self.regex_validator)

        self.percentage_h_box.addWidget(self.percentage_label)
        self.percentage_h_box.addWidget(self.percentage_tf)

        self.filter_button = QtWidgets.QPushButton(self.central_widget)
        self.filter_button.clicked.connect(self.plot_signal)

        self.vertical_layout2.addStretch()
        self.vertical_layout2.addWidget(self.percentage_h_widget)
        self.vertical_layout2.addStretch()
        self.vertical_layout2.addWidget(self.filter_button)
        self.vertical_layout2.addStretch()
        self.vertical_layout_widget2.move(self.verticalLayoutWidget.width(), 0)

        self.top_h_box.addStretch()
        self.top_h_box.addWidget(self.verticalLayoutWidget)
        self.top_h_box.addStretch()
        self.top_h_box.addWidget(self.vertical_layout_widget2)
        self.top_h_box.addStretch()

        width, height = 300, 155

        self.top_h_widget.setFixedWidth(width)

        rect = QtCore.QRect(20, 20, 271, 16)
        y_coordinate = 70

        self.radioButton = []
        i = 0

        for file in glob.glob('*.wav'):
            if file[:-4] != "FDMA":
                sr, data = wavfile.read(file)
                audio_signals[file[:-4]] = AudioSignal(file[:-4], sr, data)
                self.radioButton.append(QtWidgets.QRadioButton(self.verticalLayoutWidget))
                self.verticalLayout.addWidget(self.radioButton[i])
                i += 1

        self.radioButton[0].click()
        self.verticalLayoutWidget.setGeometry(rect)
        self.percentage_h_widget.setGeometry(
            QtCore.QRect(20, y_coordinate - 2, self.percentage_h_widget.width(),
                         self.percentage_h_widget.height()))
        self.progress_bar.setGeometry(QtCore.QRect(70, y_coordinate + 60, 180, 10))

        self.bottom_v_widget = QWidget(self.central_widget)
        self.bottom_v_box = QtWidgets.QVBoxLayout(self.bottom_v_widget)
        self.bottom_v_widget.setFixedWidth(width)

        self.horizontal_layout2_widget = QWidget(self.bottom_v_widget)
        self.horizontal_layout2 = QtWidgets.QHBoxLayout(self.horizontal_layout2_widget)

        self.send_button = QtWidgets.QPushButton(self.horizontal_layout2_widget)
        self.send_button.setText("Transmit")
        self.send_button.clicked.connect(self.transmit)

        self.horizontal_layout3_widget = QWidget(self.bottom_v_widget)
        self.horizontal_layout3 = QtWidgets.QHBoxLayout(self.horizontal_layout3_widget)

        self.frequency_tf = QtWidgets.QLineEdit(self.horizontal_layout3_widget)
        self.frequency_tf.setPlaceholderText("Frequency")

        self.bandwidth_tf = QtWidgets.QLineEdit(self.horizontal_layout3_widget)
        self.bandwidth_tf.setPlaceholderText("Bandwidth")

        self.horizontal_layout3.addWidget(self.frequency_tf)
        self.horizontal_layout3.addWidget(self.bandwidth_tf)

        self.bottom_v_widget.move(0, height)

        self.receive_button = QtWidgets.QPushButton(self.horizontal_layout2_widget)
        self.receive_button.setText("Receive From Channel")
        self.receive_button.setEnabled(False)
        self.receive_button.clicked.connect(self.receive)

        self.horizontal_layout2.addStretch()
        self.horizontal_layout2.addWidget(self.send_button)
        self.horizontal_layout2.addStretch()
        self.horizontal_layout2.addWidget(self.receive_button)
        self.horizontal_layout2.addStretch()

        self.horizontal_layout2_widget.move(0, height)

        self.channel_button = QtWidgets.QPushButton(self.bottom_v_widget)
        self.channel_button.setText("Display Channel's Plot")
        self.channel_button.clicked.connect(self.display_channel)

        self.bottom_v_box.addWidget(self.horizontal_layout3_widget)
        self.bottom_v_box.addStretch()
        self.bottom_v_box.addWidget(self.horizontal_layout2_widget)
        self.bottom_v_box.addStretch()
        self.bottom_v_box.addWidget(self.channel_button)

        self.regex_validator2 = QtGui.QRegExpValidator(QtCore.QRegExp("[0-9]*"), self.frequency_tf)
        self.frequency_tf.setValidator(self.regex_validator2)

        self.regex_validator3 = QtGui.QRegExpValidator(QtCore.QRegExp("[0-9]*"), self.bandwidth_tf)
        self.bandwidth_tf.setValidator(self.regex_validator3)

        height += self.bottom_v_widget.height() * 5

        height += self.channel_button.height()

        main_window.setFixedSize(width, height)
        self.progress_bar.setVisible(False)
        self.timer = QtCore.QBasicTimer()
        self.step = 0
        main_window.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar(main_window)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 300, 21))
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuInfo = QtWidgets.QMenu(self.menubar)
        main_window.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(main_window)
        main_window.setStatusBar(self.statusbar)
        self.actionQuit = QtWidgets.QAction(main_window)
        self.actionQuit.triggered.connect(self.quit)
        self.actionAbout = QtWidgets.QAction(main_window)
        self.actionAbout.triggered.connect(self.about)
        self.menuFile.addAction(self.actionQuit)
        self.menuInfo.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuInfo.menuAction())
        self.translate_ui(main_window)
        QtCore.QMetaObject.connectSlotsByName(main_window)
        self.pw = None
        self.channel = None
        self.transmitted = {}
        self.fpw = None

    def translate_ui(self, main_window):
        _translate = QtCore.QCoreApplication.translate
        main_window.setWindowTitle(_translate("main_window", "Communication Systems"))

        i = 0
        for key in audio_signals:
            self.radioButton[i].setText(_translate("main_window", key))
            i += 1

        self.filter_button.setText(_translate("main_window", "Filter and Plot"))
        self.menuFile.setTitle(_translate("main_window", "File"))
        self.menuInfo.setTitle(_translate("main_window", "Info"))
        self.actionQuit.setText(_translate("main_window", "Quit"))
        self.actionAbout.setText(_translate("main_window", "About"))

    def plot_signal(self):
        self.percentage_tf.setEnabled(False)
        self.step = 0
        self.timer.start(100, self)

    def transmit(self):
        if self.bandwidth_tf.text() != "" and self.frequency_tf.text() != "":
            key = ""
            for rb in self.radioButton:
                if rb.isChecked():
                    key = rb.text()
                    break

            fig, signal = display_filtered_spectrum(audio_signals[key], float(self.bandwidth_tf.text()))
            if key not in self.transmitted:
                signal = AudioSignal(key, audio_signals[key].get_sample_rate(), signal)
                self.channel = DSBSC(float(self.frequency_tf.text()), signal)
                self.transmitted[key] = float(self.bandwidth_tf.text())

            self.fpw = FilteredPlotWindow(fig)
            self.fpw.show()

    def receive(self):
        self.channel.demodulate()

    def display_channel(self):
        fig = plt.figure()
        plt.xlabel("Frequency (kHz)")
        plt.ylabel("Amplitude")
        import numpy as np
        x = np.linspace(0, len(self.channel.get_channel()) // self.channel.get_sample_rate(),
                        num=len(self.channel.get_channel()))
        plt.plot(x, self.channel.get_channel())
        self.fpw = FilteredPlotWindow(fig)
        self.fpw.show()

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
            if self.percentage_tf.text() != "":
                self.progress_bar.setVisible(True)
                self.step += 1
                self.progress_bar.setValue(self.step)

                figures, per, bw, animate = filter_and_plot(key, audio_signals[key], int(self.percentage_tf.text()),
                                                            self.step, self.progress_bar)

                self.step += 100 - self.step
                self.progress_bar.setValue(self.step)

                self.pw = PlotWindow(figures, per, bw, animate)
                self.pw.show()

            self.percentage_tf.setEnabled(True)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        super(MainWindow, self).closeEvent(a0)
        quit()

    @staticmethod
    def quit():
        sys.exit()

    @staticmethod
    def about():
        AboutDialog()


class PlotWindow(QWidget):
    def __init__(self, figures, percentage, bandwidth, animation, fig_no=0):
        super().__init__()
        self.setWindowTitle("Plot")

        self.figures = figures
        self.percentage = percentage
        self.bandwidth = bandwidth
        self.animation = animation
        self.fig_no = fig_no

        if fig_no == 1:
            self.canvas = Canvas(self, figures[fig_no], True, animation)
        else:
            self.canvas = Canvas(self, figures[fig_no])
        nav = NavigationToolbar2QT(self.canvas, self)
        nav.move(self.width() / 4, 0)
        self.canvas.move(0, nav.sizeHint().height())

        self.v_widget = QWidget(self)
        self.v_box = QtWidgets.QVBoxLayout(self.v_widget)

        self.button_time = QtWidgets.QPushButton(self.v_widget)
        self.button_time.setText("Original Signal")
        self.button_time.clicked.connect(self.change_to_original)

        self.button_frequency = QtWidgets.QPushButton(self.v_widget)
        self.button_frequency.setText("Signal's Energy")
        self.button_frequency.clicked.connect(self.change_to_energy)

        self.button_filtered = QtWidgets.QPushButton(self.v_widget)
        self.button_filtered.setText("Filtered Signal")
        self.button_filtered.clicked.connect(self.change_to_filtered)

        self.label = QtWidgets.QLabel(str(percentage * 100) + "% Energy Bandwidth: " + str(bandwidth) + " kH", self)
        self.label.move(0, self.height() + nav.sizeHint().height())
        self.label.setFixedSize(self.width(), self.label.height() + 20)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("QLabel {background-color: white; border-top-style: solid; border-top-width: 1px; "
                                 "border-top-color: black;}")

        self.v_widget.move(self.width(), 0)
        self.v_widget.setFixedHeight(self.height() + nav.sizeHint().height())

        self.v_box.addStretch()
        self.v_box.addWidget(self.button_time)
        self.v_box.addStretch()
        self.v_box.addWidget(self.button_frequency)
        self.v_box.addStretch()
        self.v_box.addWidget(self.button_filtered)
        self.v_box.addStretch()

        self.setFixedSize(self.width() + self.v_widget.width(),
                          self.height() + nav.sizeHint().height() + self.label.height())

    def change_to_original(self):
        if self.fig_no != 0:
            pw = PlotWindow(self.figures, self.percentage, self.bandwidth, self.animation, fig_no=0)
            self.close()
            pw.show()

    def change_to_energy(self):
        if self.fig_no != 1:
            pw = PlotWindow(self.figures, self.percentage, self.bandwidth, self.animation, fig_no=1)
            self.close()
            pw.show()

    def change_to_filtered(self):
        if self.fig_no != 2:
            pw = PlotWindow(self.figures, self.percentage, self.bandwidth, self.animation, fig_no=2)
            self.close()
            pw.show()


class FilteredPlotWindow(QWidget):
    def __init__(self, figure):
        super().__init__()
        self.setWindowTitle("Plot")

        self.canvas = Canvas(self, figure)

        nav = NavigationToolbar2QT(self.canvas, self)
        nav.move(self.width() / 4, 0)
        self.canvas.move(0, nav.sizeHint().height())

        self.setFixedSize(self.width(), self.height() + nav.sizeHint().height())


class Canvas(FigureCanvasQTAgg, FuncAnimation):
    def __init__(self, parent, fig, animate=False, animation=None):
        self.fig = fig
        FigureCanvasQTAgg.__init__(self, self.fig)
        if animate:
            FuncAnimation.__init__(self, self.fig, animation[0], frames=animation[1], repeat_delay=animation[2])
        self.setParent(parent)
        FigureCanvasQTAgg.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        FigureCanvasQTAgg.updateGeometry(self)
        self.draw()

    def set_fig(self, fig):
        self.fig = fig


class AboutDialog(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("About")
        QtWidgets.QMessageBox.question(self, "About", "Team members:\n\n" + "Majd Taweel\t1161422\n" +
                                       "Ibrahim Mualla\t1160346\n" + "Yazan Yahya\t1162259\n",
                                       QtWidgets.QMessageBox.Ok)
        self.setFixedSize(self.width(), self.height())
        self.show()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    mw = QtWidgets.QMainWindow()
    ui = MainWindow(mw)
    mw.show()
    sys.exit(app.exec_())
