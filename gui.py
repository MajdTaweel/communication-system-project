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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.central_widget = QWidget(self)

        self.top_h_widget = QWidget(self.central_widget)
        self.top_h_box = QtWidgets.QHBoxLayout(self.top_h_widget)

        self.lef_top_v_widget = QWidget(self.top_h_widget)
        self.lef_top_v_box = QtWidgets.QVBoxLayout(self.lef_top_v_widget)

        self.radioButton = []
        i = 0

        self.lef_top_v_box.addStretch()
        for file in glob.glob('*.wav'):
            if file[:-4] != "FDMA":
                sr, data = wavfile.read(file)
                audio_signals[file[:-4]] = AudioSignal(file[:-4], sr, data)
                self.radioButton.append(QtWidgets.QRadioButton(self.lef_top_v_widget))
                self.lef_top_v_box.addWidget(self.radioButton[i])
                self.lef_top_v_box.addStretch()
                i += 1

        self.radioButton[0].click()

        self.right_top_v_widget = QWidget(self.top_h_widget)
        self.right_top_v_box = QtWidgets.QVBoxLayout(self.right_top_v_widget)

        self.percentage_h_widget = QWidget(self.right_top_v_widget)
        self.percentage_h_box = QtWidgets.QHBoxLayout(self.percentage_h_widget)

        self.percentage_label = QtWidgets.QLabel(self.percentage_h_widget)
        self.percentage_label.setText("X% (0 - 100):")

        self.percentage_tf = QtWidgets.QLineEdit(self.percentage_h_widget)
        self.percentage_tf.setFixedWidth(25)

        self.regex_validator = QtGui.QRegExpValidator(QtCore.QRegExp("[0-9]{2}"), self.percentage_tf)
        self.percentage_tf.setValidator(self.regex_validator)

        self.percentage_h_box.addStretch()
        self.percentage_h_box.addWidget(self.percentage_label)
        self.percentage_h_box.addWidget(self.percentage_tf)
        self.percentage_h_box.addStretch()

        self.filter_h_widget = QWidget(self.right_top_v_widget)
        self.filter_h_box = QtWidgets.QHBoxLayout(self.filter_h_widget)

        self.filter_button = QtWidgets.QPushButton(self.filter_h_widget)
        self.filter_button.clicked.connect(self.plot_signal)
        self.filter_button.setStyleSheet("padding: 20px;")

        self.filter_h_box.addStretch()
        self.filter_h_box.addWidget(self.filter_button)
        self.filter_h_box.addStretch()

        self.right_top_v_box.addStretch()
        self.right_top_v_box.addWidget(self.percentage_h_widget)
        self.right_top_v_box.addWidget(self.filter_h_widget)
        self.right_top_v_box.addStretch()

        self.top_h_box.addStretch()
        self.top_h_box.addWidget(self.lef_top_v_widget)
        self.top_h_box.addWidget(self.right_top_v_widget)
        self.top_h_box.addStretch()

        self.middle_v_widget = QWidget(self.central_widget)
        self.middle_v_box = QtWidgets.QVBoxLayout(self.middle_v_widget)

        self.top_middle_h_widget = QWidget(self.middle_v_widget)
        self.top_middle_h_box = QtWidgets.QHBoxLayout(self.top_middle_h_widget)

        self.frequency_tf = QtWidgets.QLineEdit(self.top_middle_h_widget)
        self.frequency_tf.setPlaceholderText("Frequency")

        self.bandwidth_tf = QtWidgets.QLineEdit(self.top_middle_h_widget)
        self.bandwidth_tf.setPlaceholderText("Bandwidth")

        self.top_middle_h_box.addStretch()
        self.top_middle_h_box.addWidget(self.frequency_tf)
        self.top_middle_h_box.addWidget(self.bandwidth_tf)
        self.top_middle_h_box.addStretch()

        self.bottom_middle_h_widget = QWidget(self.middle_v_widget)
        self.bottom_middle_h_box = QtWidgets.QHBoxLayout(self.bottom_middle_h_widget)

        self.transmit_button = QtWidgets.QPushButton("Transmit / Display Filtered Signal", self.bottom_middle_h_widget)
        self.transmit_button.clicked.connect(self.transmit)
        self.transmit_button.setStyleSheet("padding: 10px;")

        self.reset_button = QtWidgets.QPushButton("Reset Channel", self.bottom_middle_h_widget)
        self.reset_button.clicked.connect(self.reset_channel)
        self.reset_button.setStyleSheet("padding: 10px;")

        self.bottom_middle_h_box.addStretch()
        self.bottom_middle_h_box.addWidget(self.transmit_button)
        self.bottom_middle_h_box.addWidget(self.reset_button)
        self.bottom_middle_h_box.addStretch()

        self.middle_v_box.addStretch()
        self.middle_v_box.addWidget(self.top_middle_h_widget)
        self.middle_v_box.addWidget(self.bottom_middle_h_widget)
        self.middle_v_box.addStretch()

        self.regex_validator2 = QtGui.QRegExpValidator(QtCore.QRegExp("[0-9]*"), self.frequency_tf)
        self.frequency_tf.setValidator(self.regex_validator2)

        self.regex_validator3 = QtGui.QRegExpValidator(QtCore.QRegExp("[0-9]*"), self.bandwidth_tf)
        self.bandwidth_tf.setValidator(self.regex_validator3)

        self.setCentralWidget(self.central_widget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 300, 21))
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuInfo = QtWidgets.QMenu(self.menubar)
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.setStatusBar(self.statusbar)

        self.central_layout = QtWidgets.QVBoxLayout(self.central_widget)

        self.receive_h_widget = QWidget(self.central_widget)
        self.receive_h_box = QtWidgets.QHBoxLayout(self.receive_h_widget)

        self.transmission_frequencies = QtWidgets.QComboBox(self.receive_h_widget)
        self.transmission_frequencies.setFixedWidth(100)

        self.receive_button = QtWidgets.QPushButton("Receive From Channel", self.receive_h_widget)
        self.receive_button.setEnabled(False)
        self.receive_button.clicked.connect(self.receive)
        self.receive_button.setStyleSheet("padding: 10px;")

        self.receive_h_box.addStretch()
        self.receive_h_box.addWidget(self.transmission_frequencies)
        self.receive_h_box.addWidget(self.receive_button)
        self.receive_h_box.addStretch()

        self.progress_bar = QtWidgets.QProgressBar(self.central_widget)
        self.progress_bar.setVisible(False)
        self.timer = QtCore.QBasicTimer()
        self.step = 0

        self.receive_h_box.setAlignment(QtCore.Qt.AlignHCenter)
        self.progress_bar.setAlignment(QtCore.Qt.AlignHCenter)

        self.channel_h_widget = QWidget(self.central_widget)
        self.channel_h_box = QtWidgets.QHBoxLayout(self.channel_h_widget)

        self.channel_button = QtWidgets.QPushButton(self.central_widget)
        self.channel_button.setText("Display Channel's Plot")
        self.channel_button.clicked.connect(self.display_channel)
        self.channel_button.setStyleSheet("padding: 20px;")

        self.channel_h_box.addStretch()
        self.channel_h_box.addWidget(self.channel_button)
        self.channel_h_box.addStretch()

        self.central_layout.addWidget(self.top_h_widget)
        self.central_layout.addWidget(self.middle_v_widget)
        self.central_layout.addWidget(self.receive_h_widget)
        self.central_layout.addWidget(self.channel_h_widget)
        self.central_layout.addWidget(self.progress_bar)

        self.actionQuit = QtWidgets.QAction(self)
        self.actionQuit.triggered.connect(self.quit)
        self.actionAbout = QtWidgets.QAction(self)
        self.actionAbout.triggered.connect(self.about)
        self.menuFile.addAction(self.actionQuit)
        self.menuInfo.addAction(self.actionAbout)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuInfo.menuAction())

        self.translate_ui()
        QtCore.QMetaObject.connectSlotsByName(self)
        self.pw = PlotWindow
        self.channel = DSBSC()
        self.transmitted = {}
        self.fpw = FilteredPlotWindow

    def translate_ui(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("main_window", "Communication Systems"))

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
                signal = AudioSignal(key, audio_signals[key].get_sample_rate(), ifft(ifftshift(signal)))
                self.channel.modulate(float(self.frequency_tf.text()), signal, float(self.bandwidth_tf.text()))
                self.transmitted[key] = float(self.frequency_tf.text())
                self.transmission_frequencies.addItem(key)
                if not self.receive_button.isEnabled():
                    self.receive_button.setEnabled(True)

            self.fpw = FilteredPlotWindow(fig)
            self.fpw.show()

    def receive(self):
        signal_name = self.transmission_frequencies.currentText()
        demodulated = self.channel.demodulate(self.transmitted[signal_name])
        fig_time = plt.figure()
        plt.xlabel("Time (seconds)")
        plt.ylabel("Amplitude")
        plt.title("Demodulated " + signal_name + " Signal in Time Domain")
        import numpy as np
        x = np.linspace(0, len(demodulated) // self.channel.get_sample_rate(), num=len(demodulated))
        plt.plot(x, demodulated)

        fig_frequency = plt.figure()
        plt.xlabel("Frequency (kHz)")
        plt.ylabel("Amplitude")
        plt.title("Demodulated " + signal_name + " Signal in Frequency Domain")
        plt.plot(
            fftshift(fftfreq(len(demodulated), 1000 / self.channel.get_sample_rate())), fftshift(fft(demodulated)))

        self.fpw = ChannelPlotWindow([fig_time, fig_frequency])
        self.fpw.show()
        import os
        if not os.path.isdir('./Demodulated'):
            os.mkdir('Demodulated')
        wavfile.write("Demodulated/" + signal_name + " (Demodulated).wav", self.channel.get_sample_rate(),
                      np.asarray(demodulated, dtype=np.float32))

    def display_channel(self):
        if self.channel.get_sample_rate() != 0:
            fig_time = plt.figure()
            plt.xlabel("Time (seconds)")
            plt.ylabel("Amplitude")
            plt.title("Channel in Time Domain")
            import numpy as np
            x = np.linspace(0, len(self.channel.get_channel()) // self.channel.get_sample_rate(),
                            num=len(self.channel.get_channel()))
            plt.plot(x, self.channel.get_channel())

            fig_frequency = plt.figure()
            plt.xlabel("Frequency (kHz)")
            plt.ylabel("Amplitude")
            plt.title("Channel in Frequency Domain")
            plt.plot(
                fftshift(fftfreq(len(self.channel.get_channel()), 1000 / self.channel.get_sample_rate())),
                fftshift(fft(self.channel.get_channel())))
            self.fpw = ChannelPlotWindow([fig_time, fig_frequency])
            self.fpw.show()

    def reset_channel(self):
        while self.transmission_frequencies.currentText() != "":
            self.transmission_frequencies.removeItem(0)
        self.receive_button.setEnabled(False)
        self.transmitted = {}
        self.channel = DSBSC()

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
        import os
        if os.path.isfile("FDMA.wav"):
            os.remove("FDMA.wav")
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

        self.left_v_widget = QWidget(self)
        self.left_v_box = QtWidgets.QVBoxLayout(self.left_v_widget)
        self.left_v_box.setContentsMargins(0, 0, 0, 0)

        self.right_v_widget = QWidget(self)
        self.right_v_box = QtWidgets.QVBoxLayout(self.right_v_widget)
        self.right_v_box.setContentsMargins(4, 0, 10, 0)

        if fig_no == 1:
            self.canvas = Canvas(self.left_v_widget, figures[fig_no], True, animation)
        else:
            self.canvas = Canvas(self.left_v_widget, figures[fig_no])
        self.nav = NavigationToolbar2QT(self.canvas, self.left_v_widget)

        self.label = QtWidgets.QLabel(str(percentage * 100) + "% Energy Bandwidth: " + str(bandwidth) + " kHz",
                                      self.left_v_widget)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setStyleSheet("QLabel {background-color: white; border-top-style: solid; border-top-width: 1px; "
                                 "border-top-color: black;}")
        self.label.setMinimumHeight(100)

        self.button_time = QtWidgets.QPushButton(self.right_v_widget)
        self.button_time.setText("Original Signal")
        self.button_time.clicked.connect(self.change_to_original)

        self.button_frequency = QtWidgets.QPushButton(self.right_v_widget)
        self.button_frequency.setText("Signal's Energy")
        self.button_frequency.clicked.connect(self.change_to_energy)

        self.button_filtered = QtWidgets.QPushButton(self.right_v_widget)
        self.button_filtered.setText("Filtered Signal")
        self.button_filtered.clicked.connect(self.change_to_filtered)

        self.left_v_box.addWidget(self.nav)
        self.left_v_box.addWidget(self.canvas)
        self.left_v_box.addWidget(self.label)

        self.right_v_box.addStretch()
        self.right_v_box.addWidget(self.button_time)
        self.right_v_box.addStretch()
        self.right_v_box.addWidget(self.button_frequency)
        self.right_v_box.addStretch()
        self.right_v_box.addWidget(self.button_filtered)
        self.right_v_box.addStretch()

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.left_v_widget)
        self.layout.addWidget(self.right_v_widget)
        self.setLayout(self.layout)
        self.setMinimumSize(self.width(), self.height())

    def change_to_original(self):
        if self.fig_no != 0:
            self.fig_no = 0
            self.canvas.setParent(None)
            self.canvas.__init__(self.left_v_widget, self.figures[0])
            self.nav.setParent(None)
            self.nav.__init__(self.canvas, self.left_v_widget)
            self.left_v_box.removeWidget(self.label)
            self.left_v_box.addWidget(self.nav)
            self.left_v_box.addWidget(self.canvas)
            self.left_v_box.addWidget(self.label)

    def change_to_energy(self):
        if self.fig_no != 1:
            self.fig_no = 1
            self.canvas.setParent(None)
            self.canvas = Canvas(self.left_v_widget, self.figures[1], True, self.animation)
            self.nav.setParent(None)
            self.nav.__init__(self.canvas, self.left_v_widget)
            self.left_v_box.removeWidget(self.label)
            self.left_v_box.addWidget(self.nav)
            self.left_v_box.addWidget(self.canvas)
            self.left_v_box.addWidget(self.label)

    def change_to_filtered(self):
        if self.fig_no != 2:
            self.fig_no = 2
            self.canvas.setParent(None)
            self.canvas.__init__(self.left_v_widget, self.figures[2])
            self.nav.setParent(None)
            self.nav.__init__(self.canvas, self.left_v_widget)
            self.left_v_box.removeWidget(self.label)
            self.left_v_box.addWidget(self.nav)
            self.left_v_box.addWidget(self.canvas)
            self.left_v_box.addWidget(self.label)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        plt.close('all')


class FilteredPlotWindow(QWidget):
    def __init__(self, figure):
        super().__init__()
        self.setWindowTitle("Plot")

        self.canvas = Canvas(self, figure)
        self.nav = NavigationToolbar2QT(self.canvas, self)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.nav)
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)
        self.setMinimumSize(self.width(), self.height())

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        plt.close('all')


class ChannelPlotWindow(QWidget):
    def __init__(self, figures, fig_no=0):
        super().__init__()
        self.setWindowTitle("Plot")

        self.figures = figures
        self.fig_no = fig_no

        self.left_v_widget = QWidget(self)
        self.left_v_box = QtWidgets.QVBoxLayout(self.left_v_widget)
        self.left_v_box.setContentsMargins(0, 0, 0, 0)

        self.right_v_widget = QWidget(self)
        self.right_v_box = QtWidgets.QVBoxLayout(self.right_v_widget)
        self.right_v_box.setContentsMargins(4, 0, 10, 0)

        self.canvas = Canvas(self.left_v_widget, figures[fig_no])
        self.nav = NavigationToolbar2QT(self.canvas, self.left_v_widget)

        self.left_v_box.addWidget(self.nav)
        self.left_v_box.addWidget(self.canvas)

        self.button_time = QtWidgets.QPushButton(self.right_v_widget)
        self.button_time.setText("Time Domain")
        self.button_time.clicked.connect(self.change_to_time)

        self.button_frequency = QtWidgets.QPushButton(self.right_v_widget)
        self.button_frequency.setText("Frequency Domain")
        self.button_frequency.clicked.connect(self.change_to_frequency)

        self.right_v_box.addStretch()
        self.right_v_box.addWidget(self.button_time)
        self.right_v_box.addStretch()
        self.right_v_box.addWidget(self.button_frequency)
        self.right_v_box.addStretch()

        self.layout = QtWidgets.QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addWidget(self.left_v_widget)
        self.layout.addWidget(self.right_v_widget)
        self.setLayout(self.layout)
        self.setMinimumSize(self.width(), self.height())

    def change_to_time(self):
        if self.fig_no != 0:
            self.fig_no = 0
            self.canvas.setParent(None)
            self.canvas.__init__(self.left_v_widget, self.figures[0])
            self.nav.setParent(None)
            self.nav.__init__(self.canvas, self.left_v_widget)
            self.left_v_box.addWidget(self.nav)
            self.left_v_box.addWidget(self.canvas)

    def change_to_frequency(self):
        if self.fig_no != 1:
            self.fig_no = 1
            self.canvas.setParent(None)
            self.canvas.__init__(self.left_v_widget, self.figures[1])
            self.nav.setParent(None)
            self.nav.__init__(self.canvas, self.left_v_widget)
            self.left_v_box.addWidget(self.nav)
            self.left_v_box.addWidget(self.canvas)

    def closeEvent(self, a0: QtGui.QCloseEvent) -> None:
        plt.close('all')


class Canvas(FigureCanvasQTAgg, FuncAnimation):
    def __init__(self, parent, fig, animate=False, animation=None):
        self.fig = fig
        FigureCanvasQTAgg.__init__(self, self.fig)
        if animate:
            FuncAnimation.__init__(self, self.fig, animation[0], frames=animation[1], repeat_delay=animation[2])
        self.setParent(parent)
        FigureCanvasQTAgg.setSizePolicy(self, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        self.draw()


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
    ui = MainWindow()
    ui.show()
    sys.exit(app.exec_())
