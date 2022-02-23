"""
Modified from https://www.pythonguis.com/examples/python-web-browser/
"""

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import *

from plyer import notification
import os
import sys
from ong_yt2mp3.download import base_dir

if sys.platform == "darwin":
    import pync     # Notifications that work in macos

ICON_PATH = os.path.join(os.path.dirname(__file__), "images")


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.destination_dir = os.path.join(base_dir, "mp3")

        self.first_load = True
        self.downloads = list()

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.youtube.com"))

        self.browser.loadFinished.connect(self.update_title)
        self.setCentralWidget(self.browser)

        self.status = QStatusBar()
        self.setStatusBar(self.status)
        self.status.setStatusTip("Downloading to ")

        download_menu = self.menuBar().addMenu("&Download")
        download_file_action = QAction(QIcon(os.path.join(ICON_PATH, 'disk--arrow.png')), "Download mp3", self)
        download_file_action.setStatusTip("Download mp3 file from youtube")
        download_file_action.triggered.connect(self.download_mp3_file)
        download_menu.addAction(download_file_action)
        download_menu.addSeparator()
        config_path_action = QAction(QIcon(), "Config path", self)
        config_path_action.setStatusTip("Define directory for downloading files")
        config_path_action.triggered.connect(self.change_destination_path)
        download_menu.addAction(config_path_action)


        # self.show()
        self.showMaximized()

    def change_destination_path(self):
        chosen_dir = str(QFileDialog.getExistingDirectory(self, "Select Directory", self.destination_dir))
        if chosen_dir:
            self.destination_dir = chosen_dir

    def download_mp3_file(self):
        link = self.browser.url().url()
        # self.status.setStatusTip(f"Downloading mp3 from {link}")
        from ong_yt2mp3.dialog_progress import MainWindow as ProgressWindow
        p = ProgressWindow(parent=self)
        p.url_le.setText(link)
        p.show()
        p.download(self.destination_dir)

    def update_title(self, ok):
        title = self.browser.page().title()
        self.setWindowTitle("%s - OngYouTubeDownloader" % title)
        if self.first_load:
            import time
            time.sleep(1.5)       # Needs a bit of time to load page JS
            self.browser.page().runJavaScript(
                'document.getElementById("lightbox").getElementsByClassName("buttons")[0].children[1].click();')
            self.first_load = False


def notifiy(msg, title="Python"):
    if sys.platform != "darwin":
        notification.notify(msg, title=title)
    else:
        pync.notify(msg, title=title)


def main():
    app = QApplication(sys.argv)
    #app.setApplicationName("MooseAche")
    #app.setOrganizationName("MooseAche")
    #app.setOrganizationDomain("MooseAche.org")

    window = MainWindow()
    app.setWindowIcon(QIcon(os.path.join(ICON_PATH, 'yt2mp3.png')))

    exit(app.exec())


if __name__ == '__main__':
    main()
