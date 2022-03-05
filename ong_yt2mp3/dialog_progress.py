"""
Based on https://stackoverflow.com/questions/63757798/how-to-integrate-youtube-dl-in-pyqt5
"""
from PyQt6 import QtWidgets, QtCore

from ong_yt2mp3.qyoutubedl import QLogger, QHook, QYoutubeDL

from ong_yt2mp3.download import get_ydl_opts, base_dir, test_url
import os


class MainWindow(QtWidgets.QMainWindow):
    close_signal = QtCore.pyqtSignal(QtWidgets.QMainWindow)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.filename = None
        self.tmpfilename = None

        self.url_le = QtWidgets.QLineEdit()
        self.download_btn = QtWidgets.QPushButton(self.tr("Download"))
        if parent is not None:
            self.download_btn.hide()
        self.cancel_download_btn = QtWidgets.QPushButton(self.tr("Cancel"))
        if parent is not None:
            self.download_btn.hide()

        self.progress_lbl = QtWidgets.QLabel()
        self.download_pgb = QtWidgets.QProgressBar()
        self.log_edit = QtWidgets.QPlainTextEdit(readOnly=True)

        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        lay = QtWidgets.QGridLayout(central_widget)
        lay.addWidget(QtWidgets.QLabel(self.tr("url:")))
        lay.addWidget(self.url_le, 0, 1)
        lay.addWidget(self.download_btn, 0, 2)
        lay.addWidget(self.cancel_download_btn, 0, 3)
        lay.addWidget(self.progress_lbl, 1, 1, 1, 2)
        lay.addWidget(self.download_pgb, 2, 1, 1, 2)
        lay.addWidget(self.log_edit, 3, 1, 1, 2)
        self.progress_lbl.hide()

        self.downloader = QYoutubeDL()

        self.download_btn.clicked.connect(self.download)
        self.cancel_download_btn.clicked.connect(self.handle_cancel_download)

        self.url_le.setText(test_url)

        self.resize(640, 480)

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
            destination_dir = os.path.join(base_dir, "mp3")
        options.update(get_ydl_opts(destination_dir))
        qhook.infoChanged.connect(self.handle_info_changed)
        qlogger.messageChanged.connect(self.log_edit.appendPlainText)
        self.download_pgb.setRange(0, 1)
        self.downloader.download([url], options)

    def handle_download_finished(self, b):
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle("Finished")
        dlg.setText("Download '{}' finished!".format(self.filename))
        button = dlg.exec()
        self.close()

    def handle_info_changed(self, d):
        try:
            if d["status"] == "downloading":
                self.progress_lbl.show()
                total = d["total_bytes"]
                downloaded = d["downloaded_bytes"]
                speed_kbps = d.get('speed', 0) / 1024
                self.tmpfilename = d.get('tmpfilename')
                self.filename = d.get('filename')
                total_mb = total / 1024 / 1024 if total else 0
                percentage = 100.0 * downloaded / total
                self.progress_lbl.setText(f"{percentage:.2f}% of {total_mb:.2f}Mb [{speed_kbps:.2f}kb/s]")
                self.download_pgb.setMaximum(total)
                self.download_pgb.setValue(downloaded)
            elif d['status'] == "finished":
                pass    # download finished, but still normalizing
                self.tmpfilename = None
            #     self.filename = d.get('filename')
            #     self.handle_download_finished(True)
            elif d['status'] == "normalizing":
                pass
            elif d['status'] == "yt2mp3_finished":
                self.filename = d.get("filename")
                self.handle_download_finished(True)
            else:
                pass
        finally:
            pass

    def handle_cancel_download(self):
        self.downloader.stop()
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle("Download canceled")
        dlg.setText("Download '{}' canceled by user!".format(self.filename))
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