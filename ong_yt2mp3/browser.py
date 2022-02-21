"""
Modified from https://www.pythonguis.com/examples/python-web-browser/
"""

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import *

from plyer import notification
import pync


import os
import sys

from ong_yt2mp3.download import download_mp3

ICON_PATH = os.path.join(os.path.dirname(__file__), "images")


class RunnableDownloadProcess(QRunnable):
    def __init__(self, link):
        QRunnable.__init__(self)
        self.link = link
        self.th = None

    def run(self):
        download_mp3(self.link)

    def start(self):
        QThreadPool.globalInstance().start(self)

    def stop(self):
        if self.th:
            self.th.stop()


class DownloadThread(QThread):

    def __init__(self, link):
        QThread.__init__(self)
        self.link = link

    def run(self):
        download_mp3(self.link)

    def stop(self):
        self.terminate()


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.first_load = True
        self.downloads = list()

        self.browser = QWebEngineView()
        self.browser.setUrl(QUrl("https://www.youtube.com"))

        self.browser.loadFinished.connect(self.update_title)
        self.setCentralWidget(self.browser)

        self.status = QStatusBar()
        self.setStatusBar(self.status)

        download_menu = self.menuBar().addMenu("&Download")
        download_file_action = QAction(QIcon(os.path.join(ICON_PATH, 'disk--arrow.png')), "Download mp3", self)
        download_file_action.setStatusTip("Download mp3 file from youtube")
        download_menu.triggered.connect(self.download_mp3_file)
        download_menu.addAction(download_file_action)

        cancel_download_action = QAction(QIcon(os.path.join(ICON_PATH, 'cross-circle.png')), "Cancel mp3 downloads", self)
        cancel_download_action.setStatusTip("Cancel all mp3 downloads")
        download_menu.triggered.connect(self.cancel_downloads)
        download_menu.addAction(cancel_download_action)

        # self.show()
        self.showMaximized()

        self.setWindowIcon(QIcon(os.path.join(ICON_PATH, 'ma-icon-64.png')))

    def download_mp3_file(self):
        link = self.browser.url().url()
        # self.status.setStatusTip(f"Downloading mp3 from {link}")
        download_process = RunnableDownloadProcess(link=link)
        #download_process = DownloadThread(link=link)
        #download_process.setTerminationEnabled(True)
        self.downloads.append(download_process)
        download_process.start()
        # self.downloads[-1].start()
        notifiy(f"Downloading mp3 from {link}")
        # download_mp3(link)

    def cancel_downloads(self):
        for p in self.downloads:
            p.stop()

    def update_title(self, ok):
        title = self.browser.page().title()
        self.setWindowTitle("%s - MooseAche" % title)
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
    app.setApplicationName("MooseAche")
    app.setOrganizationName("MooseAche")
    app.setOrganizationDomain("MooseAche.org")

    window = MainWindow()

    exit(app.exec())
    #app.exec_()


if __name__ == '__main__':
    main()
