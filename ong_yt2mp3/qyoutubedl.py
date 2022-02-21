import threading
from PyQt6 import QtCore

import youtube_dl


class QLogger(QtCore.QObject):
    messageChanged = QtCore.pyqtSignal(str)

    def debug(self, msg):
        self.messageChanged.emit(msg)

    def warning(self, msg):
        self.messageChanged.emit(msg)

    def error(self, msg):
        self.messageChanged.emit(msg)


class QHook(QtCore.QObject):
    infoChanged = QtCore.pyqtSignal(dict)

    def __call__(self, d):
        self.infoChanged.emit(d.copy())


class QYoutubeDL(QtCore.QObject):

    finished = QtCore.pyqtSignal(bool)

    def download(self, urls, options):
        threading.Thread(
            target=self._execute, args=(urls, options), daemon=True
        ).start()

    def _execute(self, urls, options):
        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download(urls)
        self.finished.emit(True)    # Download complete!
        for hook in options.get("progress_hooks", []):
            if isinstance(hook, QHook):
                hook.deleteLater()
        logger = options.get("logger")
        if isinstance(logger, QLogger):
            logger.deleteLater()
