import threading
from PyQt6 import QtCore

import youtube_dl


# Raised when a Download Thread is manually stopped
class StopDownloadException(Exception):
    pass


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
    stop = False

    def __call__(self, d):
        if self.stop:
            raise StopDownloadException("Download Process canceled by the user")
        self.infoChanged.emit(d.copy())


class QYoutubeDL(QtCore.QObject):

    def __init__(self):
        super(QYoutubeDL, self).__init__()
        self.th = None
        self.title = None
        self.hooks = list()

    def download(self, urls, options):
        self.th = threading.Thread(target=self._execute, args=(urls, options), daemon=True)
        self.th.start()

    def _execute(self, urls, options):
        for hook in options.get("progress_hooks", []):
            if isinstance(hook, QHook):
                self.hooks.append(hook)
        try:
            with youtube_dl.YoutubeDL(options) as ydl:
                info = ydl.extract_info(urls[0], download=False)
                self.title = info['title']
                ydl.download(urls)
            for hook in self.hooks:
                hook.deleteLater()
            logger = options.get("logger")
            if isinstance(logger, QLogger):
                logger.deleteLater()
        except Exception as e:
            print(e)

    def stop(self):
        if self.th is not None:
            for hook in self.hooks:
                hook.stop = True

