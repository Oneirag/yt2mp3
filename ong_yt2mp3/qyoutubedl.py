import os.path
import threading
from PyQt6 import QtCore

import youtube_dl
import pynormalize


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
        logger = options.get("logger")
        try:
            with youtube_dl.YoutubeDL(options) as ydl:
                info = ydl.extract_info(urls[0], download=False)
                self.title = info['title']
                ydl.download(urls)
            mp3_filename = options['outtmpl'] % dict(title=self.title,
                                                     ext=options["postprocessors"][0]['preferredcodec'])
            dirname, filename = os.path.split(mp3_filename)
            out_mp3_dir = dirname   # overwrite original file
            # out_mp3_dir = os.path.join(dirname, "normalized")
            # out_mp3_filename = os.path.join(out_mp3_dir, filename)
            if os.path.isfile(mp3_filename):
                self.hooks[0](dict(filename=mp3_filename, status="normalizing"))
                pynormalize.logger = logger     # Force using own logger
                pynormalize.process_files([mp3_filename], target_dbfs=-13.5,
                                          directory=out_mp3_dir)
                # os.replace(mp3_filename, out_mp3_filename)
                # os.rmdir(out_mp3_dir)
                self.hooks[0](dict(filename=filename, status="normalizing_finished"))

            for hook in self.hooks:
                hook.deleteLater()
            if isinstance(logger, QLogger):
                logger.deleteLater()
        except Exception as e:
            print(e)

    def stop(self):
        if self.th is not None:
            for hook in self.hooks:
                hook.stop = True

