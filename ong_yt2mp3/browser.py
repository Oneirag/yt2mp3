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
from ong_yt2mp3.icons.icons import get_icon

if sys.platform == "darwin":
    import pync     # Notifications that work in macos


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.destination_dir = base_dir
        os.makedirs(self.destination_dir, exist_ok=True)

        self.first_load = True
        self.downloads = list()

        self.browser = QWebEngineView()
        self.navigate_home()
        self.browser.loadFinished.connect(self.update_title)
        self.setCentralWidget(self.browser)

        navtb = QToolBar("Navigation")
        navtb.setIconSize(QSize(16, 16))
        navtb.setIconSize(QSize(24, 24))
        navtb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.addToolBar(navtb)

        back_btn = QAction(get_icon('arrow-180.png'), "Back", self)
        back_btn.setStatusTip("Back to previous page")
        back_btn.triggered.connect(self.browser.back)
        navtb.addAction(back_btn)

        next_btn = QAction(get_icon('arrow-000.png'), "Forward", self)
        next_btn.setStatusTip("Forward to next page")
        next_btn.triggered.connect(self.browser.forward)
        navtb.addAction(next_btn)

        home_btn = QAction(get_icon('icons8-casa-48.png'), "Home", self)
        home_btn.setStatusTip("Go home")
        home_btn.triggered.connect(self.navigate_home)
        navtb.addAction(home_btn)

        navtb.addSeparator()
        download_btn = QAction(get_icon('icons8-descargar-desde-la-nube-48.png'), "Download", self)
        download_btn.setStatusTip("Download link")
        download_btn.triggered.connect(self.download_mp3_file)
        navtb.addAction(download_btn)

        open_folder_btn = QAction(get_icon('icons8-carpeta-48.png'), "Open downloads", self)
        open_folder_btn.setStatusTip("Open destination folder")
        open_folder_btn.triggered.connect(self.open_destination_path)
        navtb.addAction(open_folder_btn)

        navtb.addSeparator()

        label_path = QLabel("Destination folder")
        navtb.addWidget(label_path)

        change_folder_btn = QAction(get_icon('icons8-abrir-carpeta-48.png'), "Change", self)
        change_folder_btn.setStatusTip("Change destination folder")
        change_folder_btn.triggered.connect(self.change_destination_path)
        navtb.addAction(change_folder_btn)

        self.text_path = QLineEdit()
        self.text_path.setText(self.destination_dir)
        self.text_path.setReadOnly(True)
        navtb.addWidget(self.text_path)

        # self.show()
        self.showMaximized()

    def navigate_home(self):
        self.browser.setUrl(QUrl("https://www.youtube.com"))

    def change_destination_path(self):
        chosen_dir = str(QFileDialog.getExistingDirectory(self, "Select Directory", self.destination_dir))
        if chosen_dir:
            self.destination_dir = chosen_dir
            self.text_path.setText(self.destination_dir)

    def open_destination_path(self):
        import os
        import platform
        import subprocess

        def open_file(path):
            if platform.system() == "Windows":
                os.startfile(path)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])

        """Opens in finder/explorer"""
        open_file(self.destination_dir)

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
    app.setWindowIcon(get_icon('yt2mp3.png'))

    exit(app.exec())


if __name__ == '__main__':
    main()
