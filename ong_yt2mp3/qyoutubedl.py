import threading
import ctypes
from PyQt6 import QtCore

import youtube_dl


# Adapted from https://www.geeksforgeeks.org/python-different-ways-to-kill-a-thread/
class KillableThread(threading.Thread):

    def get_id(self):
        # returns id of the respective thread
        if hasattr(self, '_thread_id'):
            return self._thread_id
        for id, thread in threading._active.items():
            if thread is self:
                return id

    def raise_exception(self):
        thread_id = self.get_id()
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id,
                                                         ctypes.py_object(SystemExit))
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(thread_id, 0)
            print('Exception raise failure')


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

    def __init__(self):
        super(QYoutubeDL, self).__init__()
        self.th = None

    def download(self, urls, options):
        threading.Thread(
            target=self._execute, args=(urls, options), daemon=True
        ).start()
        self.th = KillableThread(target=self._execute, args=(urls, options), daemon=True)
        self.th.start()

    def _execute(self, urls, options):
        with youtube_dl.YoutubeDL(options) as ydl:
            ydl.download(urls)
        for hook in options.get("progress_hooks", []):
            if isinstance(hook, QHook):
                hook.deleteLater()
        logger = options.get("logger")
        if isinstance(logger, QLogger):
            logger.deleteLater()

    def stop(self):
        if self.th is not None:
            self.th.raise_exception()
            self.th.join()
