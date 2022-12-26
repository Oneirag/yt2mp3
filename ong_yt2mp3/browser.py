"""
Modified from https://www.pythonguis.com/examples/python-web-browser/
"""

from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from PyQt6.QtGui import *
from PyQt6.QtWebEngineWidgets import *

import os
import sys
from time import sleep
from ong_yt2mp3.download import base_dir
from ong_yt2mp3.icons.icons import get_icon
from ong_yt2mp3.dialog_progress import MainWindow as ProgressWindow
from ong_yt2mp3.js_addblock import addblock_js_script


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.destination_dir = base_dir
        os.makedirs(self.destination_dir, exist_ok=True)

        self.first_load = True
        self.downloads = list()
        self.download_windows = list()

        self.browser = QWebEngineView()
        self.handle_navigate_home()
        self.browser.loadFinished.connect(self.handle_update_title)
        self.browser.urlChanged.connect(self.handle_url_changed)
        self.setCentralWidget(self.browser)

        navtb = QToolBar(QCoreApplication.translate("BrowserWindow", "Navigation"))
        navtb.setIconSize(QSize(24, 24))
        navtb.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)

        self.addToolBar(navtb)

        back_btn = QAction(get_icon('arrow-180.png'),
                           QCoreApplication.translate("BrowserWindow", "Back"), self)
        back_btn.setStatusTip(QCoreApplication.translate(
                "BrowserWindow",
                "Go to previous page",
            ))
        back_btn.triggered.connect(self.browser.back)
        navtb.addAction(back_btn)

        next_btn = QAction(get_icon('arrow-000.png'),
                           QCoreApplication.translate("BrowserWindow", "Forward"), self)
        next_btn.setStatusTip(QCoreApplication.translate(
                "BrowserWindow",
                "Go to next page",
            ))
        next_btn.triggered.connect(self.browser.forward)
        navtb.addAction(next_btn)

        home_btn = QAction(get_icon('icons8-casa-48.png'),
                           QCoreApplication.translate("BrowserWindow", "Home"), self)
        home_btn.triggered.connect(self.handle_navigate_home)
        navtb.addAction(home_btn)
        home_btn.setStatusTip(QCoreApplication.translate(
                "BrowserWindow",
                "Go to home page",
            ))

        navtb.addSeparator()
        download_btn = QAction(get_icon('icons8-descargar-desde-la-nube-48.png'),
                               QCoreApplication.translate("BrowserWindow", "Download"), self)
        download_btn.triggered.connect(self.handle_download_mp3_file)
        navtb.addAction(download_btn)
        download_btn.setStatusTip(QCoreApplication.translate(
                "BrowserWindow",
                "Download currently opened link as mp3",
            ))

        open_folder_btn = QAction(get_icon('icons8-carpeta-48.png'),
                                  QCoreApplication.translate("BrowserWindow", "Open download folder"), self)
        open_folder_btn.triggered.connect(self.handle_open_destination_path)
        navtb.addAction(open_folder_btn)
        open_folder_btn.setStatusTip(QCoreApplication.translate(
                "BrowserWindow",
                "Open download folder",
            ))

        navtb.addSeparator()

        label_path = QLabel(QCoreApplication.translate("BrowserWindow", "Destination folder:"))
        navtb.addWidget(label_path)

        self.text_path = QLineEdit()
        self.text_path.setText(self.destination_dir)
        self.text_path.setReadOnly(True)
        navtb.addWidget(self.text_path)

        change_folder_btn = QAction(get_icon('icons8-abrir-carpeta-48.png'),
                                    QCoreApplication.translate("BrowserWindow", "Change folder"), self)
        change_folder_btn.triggered.connect(self.handle_change_destination_path)
        navtb.addAction(change_folder_btn)
        change_folder_btn.setStatusTip(QCoreApplication.translate(
                "BrowserWindow",
                "Change destination folder",
            ))

        navtb.addSeparator()
        label_downloads = QLabel(QCoreApplication.translate("BrowserWindow", "Active downloads:"))
        navtb.addWidget(label_downloads)
        self.download_combobox = QComboBox()
        self.download_combobox.activated.connect(self.handle_download_combo)
        navtb.addWidget(self.download_combobox)

        # self.show()
        self.showMaximized()

    def handle_url_changed(self, new_url):
        """Event fired when a new page is opened. Js for add blocker is injected here"""
        self.browser.page().runJavaScript(
            addblock_js_script
        )

    def handle_download_combo(self, idx):
        window = self.download_windows[idx]
        # this will remove minimized status
        # and restore window with keeping maximized/normal state
        window.setWindowState(window.windowState() & ~Qt.WindowState.WindowMinimized | Qt.WindowState.WindowActive)

        # this will activate the window
        window.activateWindow()
        pass

    def handle_navigate_home(self):
        self.browser.setUrl(QUrl("https://www.youtube.com"))

    def handle_change_destination_path(self):
        chosen_dir = str(QFileDialog.getExistingDirectory(self, "Select Directory", self.destination_dir))
        if chosen_dir:
            self.destination_dir = chosen_dir
            self.text_path.setText(self.destination_dir)

    def handle_open_destination_path(self):
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

    def handle_close_signal(self, window):
        try:
            idx = self.download_windows.index(window)
        except ValueError:
            idx = None
        self.download_windows.pop(idx)
        self.download_combobox.removeItem(idx)

    def handle_download_mp3_file(self):
        link = self.browser.url().url()
        # self.status.setStatusTip(f"Downloading mp3 from {link}")
        p = ProgressWindow(parent=self)
        p.close_signal.connect(self.handle_close_signal)
        p.url_le.setText(link)
        p.show()
        p.download(self.destination_dir)
        self.downloads.append(link)
        self.download_windows.append(p)
        for _ in range(20):
            if p.downloader.title is None:
                sleep(0.1)
            else:
                break
        self.download_combobox.addItem(p.downloader.title if p.downloader.title is not None else link)

    def handle_update_title(self, ok):
        title = self.browser.page().title()
        self.setWindowTitle("%s - OngYouTubeDownloader" % title)
        if self.first_load:
            self.browser.page().runJavaScript(
                """
                buttons = document.getElementById("lightbox").getElementsByTagName("ytd-button-renderer");
                for(const button of buttons){
                    const txt = typeof button.innerText === 'string' ? button.innerText.toUpperCase() : '';
                    if (txt  == "RECHAZAR TODO"){
                        // alert("click!");
                        button.getElementsByTagName("button")[0].click();
                    }
                }
                """)
            self.first_load = False


def main():
    app = QApplication(sys.argv)

    defaultLocale = QLocale.system().name()

    translator = QTranslator()
    translation_file = os.path.join(os.path.dirname(__file__), "i18n", f"{defaultLocale}.xml.qm")
    exists_translation_file = os.path.isfile(translation_file)
    if exists_translation_file:
        print(f"Translation file '{translation_file}' found and used")
    else:
        print(f"Translation file '{translation_file}' NOT FOUND, default translation will be used")

    translator.load(translation_file)
    app.installTranslator(translator)

    window = MainWindow()
    app.setWindowIcon(get_icon('yt2mp3.png'))

    exit(app.exec())


if __name__ == '__main__':
    main()
