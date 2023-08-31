# Tool to download youtube links into mp3 files
It is just a simple wrapper of `yt-dlp` and `pynormalize`

Adapts QT code from https://www.pythonguis.com/examples/python-web-browser/ (including update from PyQt5 to PyQt6)

## Installation

### Prerequisite: install ffmpeg
To install it:
- linux: `apt install ffmpeg`
- windows: download files from https://ffmpeg.org/download.html#build-windows and place files in path 
(typically, current dir)
- macos: with M1 chip, it is needed to be installed using homebrew `brew install ffmpeg`
### Installation
```bash
pip install git+https://github.com/Oneirag/yt2mp3.git
python -m ong_yt2mp3.post_install
```