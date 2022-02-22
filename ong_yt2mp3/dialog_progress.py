"""
Based on https://stackoverflow.com/questions/63757798/how-to-integrate-youtube-dl-in-pyqt5
"""
from PyQt6 import QtWidgets

from ong_yt2mp3.qyoutubedl import QLogger, QHook, QYoutubeDL

from ong_yt2mp3.download import get_ydl_opts, base_dir, test_url
import os


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

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

    def download(self):
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
        options = get_ydl_opts(os.path.join(base_dir, "mp3"))
        options['logger'] = qlogger
        options['progress_hooks'] = [qhook]
        options['noprogress'] = True
        self.downloader.download([url], options)
        qhook.infoChanged.connect(self.handle_info_changed)
        qlogger.messageChanged.connect(self.log_edit.appendPlainText)
        self.download_pgb.setRange(0, 1)

    def handle_download_finished(self, b):
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle("Finished")
        dlg.setText("Download finished!")
        button = dlg.exec()
        self.close()

        # if button == QtWidgets.QMessageBox.StandardButton.Ok:
        #     print("OK!")

    def handle_info_changed(self, d):
        if d["status"] == "downloading":
            self.progress_lbl.show()
            total = d["total_bytes"]
            downloaded = d["downloaded_bytes"]
            #self.progress_lbl.setText("{} of {}".format(size(downloaded), size(total)))
            # self.progress_lbl.setText("{} of {}".format(downloaded, total))
            self.progress_lbl.setText("{:.2f}%".format(100.0 * downloaded / total))
            self.download_pgb.setMaximum(total)
            self.download_pgb.setValue(downloaded)
        elif d['status'] == "finished":
            self.handle_download_finished(True)

    def handle_cancel_download(self):
        self.downloader.stop()
        dlg = QtWidgets.QMessageBox(self)
        dlg.setWindowTitle("Canceled")
        dlg.setText("Download canceled by user!")
        button = dlg.exec()
        self.close()


def main():
    import sys

    app = QtWidgets.QApplication(sys.argv)
    w = MainWindow()
    w.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()