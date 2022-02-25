from PyQt6.QtGui import QIcon
import os


def get_icon(icon_name: str = None):
    if icon_name:
        ICON_PATH = os.path.join(os.path.dirname(__file__))
        icon_filename = os.path.join(ICON_PATH, icon_name)
        print(icon_filename)
        if not os.path.isfile(icon_filename):
            print("Icon file not found!!!!")
        return QIcon(os.path.join(ICON_PATH, icon_name))
    else:
        return QIcon()
