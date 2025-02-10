"""
Based on https://stackoverflow.com/questions/63757798/how-to-integrate-youtube-dl-in-pyqt5
"""
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import QCoreApplication, Qt
from superqt import QDoubleRangeSlider

from ong_yt2mp3.qyoutubedl import QLogger, QHook, QYoutubeDL

from ong_yt2mp3.download import get_ydl_opts, base_dir, test_url
import os
import datetime
from pynormalize import AudioSegment


class MainWindow(QtWidgets.QMainWindow):
    close_signal = QtCore.pyqtSignal(QtWidgets.QMainWindow)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filename = None
        self.tmpfilename = None
        self.destination_dir = None

        self.duration = None

        self.url_le = QtWidgets.QLineEdit()
        self.download_btn = QtWidgets.QPushButton(QCoreApplication.translate("DownloadWindow", "Download"))
        if parent is not None:
            self.download_btn.hide()
        self.cancel_download_btn = QtWidgets.QPushButton(QCoreApplication.translate("DownloadWindow", "Cancel"))
        if parent is not None:
            self.download_btn.hide()

        self.cut_range_slider = QDoubleRangeSlider()
        self.cut_range_slider.setOrientation(Qt.Orientation.Horizontal)
        self.cut_start = QtWidgets.QLabel("00:00:00")
        self.cut_end = QtWidgets.QLabel("00:00:00")

        self.progress_lbl = QtWidgets.QLabel()
        self.download_pgb = QtWidgets.QProgressBar()
        self.log_edit = QtWidgets.QPlainTextEdit(readOnly=True)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        lay = QtWidgets.QGridLayout(central_widget)
        lay.addWidget(QtWidgets.QLabel(QCoreApplication.translate("DownloadWindow", "url:")))
        lay.addWidget(self.url_le, 0, 1)
        lay.addWidget(self.download_btn, 0, 2)
        lay.addWidget(self.cancel_download_btn, 0, 3)
        lay.addWidget(self.progress_lbl, 1, 1, 1, 2)
        lay.addWidget(self.download_pgb, 2, 1, 1, 2)

        lay.addWidget(self.cut_start, 3, 0, 1, 1)
        lay.addWidget(self.cut_range_slider, 3, 1, 1, 2)
        lay.addWidget(self.cut_end, 3, 3)

        lay.addWidget(self.log_edit, 4, 1, 1, 2)
        self.progress_lbl.hide()

        self.downloader = QYoutubeDL()

        self.download_btn.clicked.connect(self.download)
        self.cancel_download_btn.clicked.connect(self.handle_cancel_download)
        self.cut_range_slider.valueChanged.connect(self.handle_cut_range_changed)

        self.url_le.setText(test_url)

        self.resize(640, 480)

    def handle_cut_range_changed(self, new_value):
        min_v, max_v = map(int, new_value)

        def fmt(value):
            return str(datetime.timedelta(seconds=int(value)))

        self.cut_start.setText(fmt(min_v))
        self.cut_end.setText(fmt(max_v))

    def download(self, destination_dir: str = None):
        qhook = QHook()
        qlogger = QLogger()
        url = self.url_le.text()
        options = {
            "format": "bestvideo[height=144]+bestaudio/best",
            "noplaylist": True,
            "postprocessors": [{"key": "FFmpegMetadata"}],
            "noprogress": True,
            "logger": qlogger,
            "progress_hooks": [qhook],
        }
        if destination_dir is None:
            self.destination_dir = os.path.join(base_dir, "mp3")
        else:
            self.destination_dir = destination_dir
        options.update(get_ydl_opts(self.destination_dir))
        qhook.infoChanged.connect(self.handle_info_changed)
        qlogger.messageChanged.connect(self.log_edit.appendPlainText)
        self.download_pgb.setRange(0, 1)
        self.downloader.download([url], options)

    def handle_download_finished(self, b):
        min, max = self.cut_range_slider.value()
        if not (min == 0 and max == self.duration):
            if self.filename and os.path.isfile(os.path.join(self.destination_dir, self.filename)):
                filename = os.path.join(self.destination_dir, self.filename)
                segment = AudioSegment.from_mp3(filename)
                segment = segment[min*1000:max*1000]
                segment.export(filename)

        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle(QCoreApplication.translate("DownloadWindow", "Finished"))
        dlg.setText(QCoreApplication.translate("DownloadWindow", "Download '{}' finished!").format(self.filename))
        button = dlg.exec()
        self.close()

    def handle_info_changed(self, d):
        try:
            if d["status"] == "downloading":
                self.progress_lbl.show()
                total = d["total_bytes"]
                downloaded = d["downloaded_bytes"]
                speed_kbps = (d.get('speed') or 0) / 1024
                self.tmpfilename = d.get('tmpfilename')
                self.filename = d.get('filename')
                total_mb = total / 1024 / 1024 if total else 0
                percentage = 100.0 * downloaded / total
                self.progress_lbl.setText(
                    QCoreApplication.translate("DownloadWindow",
                                               "Downloaded {percentage:.2f}% of {total_mb:.2f}Mb [{speed_kbps:.2f}kb/s]"
                                               ).format(percentage=percentage, total_mb=total_mb, speed_kbps=speed_kbps)
                )
                self.download_pgb.setMaximum(total)
                self.download_pgb.setValue(downloaded)
            elif d['status'] == "finished":
                pass  # download finished, but still normalizing
                self.tmpfilename = None
            #     self.filename = d.get('filename')
            #     self.handle_download_finished(True)
            elif d['status'] == "normalizing":
                pass
            elif d['status'] == "yt2mp3_finished":
                self.filename = d.get("filename")
                self.handle_download_finished(True)
            elif d['status'] == "duration":
                self.duration = d.get("duration")
                self.cut_range_slider.setRange(0, self.duration)
                self.cut_range_slider.setValue((0, self.duration))
            else:
                pass
        finally:
            pass

    def handle_cancel_download(self):
        self.downloader.stop()
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle(QCoreApplication.translate("DownloadWindow", "Download canceled"))
        dlg.setText(
            QCoreApplication.translate("DownloadWindow", "Download '{}' canceled by user!").format(self.filename))
        if self.filename:
            if os.path.isfile(self.filename):
                os.remove(self.filename)
        if self.tmpfilename:
            if os.path.isfile(self.tmpfilename):
                os.remove(self.tmpfilename)
        button = dlg.exec()
        self.close()

    def close(self) -> bool:
        self.close_signal.emit(self)
        return super().close()


def main():
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
