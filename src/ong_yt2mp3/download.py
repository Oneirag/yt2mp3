import sys
import os
import yt_dlp as youtube_dl

base_dir = os.path.join(os.path.expanduser("~"), "Downloads", "yt2mp3")
test_url = "https://www.youtube.com/watch?v=uqQglwBzFT4"    # imperial march


def get_ydl_opts(download_path: str) -> dict:
    """Gets a dict with configurations for YouTube downloader to download mp3 to the given download_path"""
    mp3_template = os.path.join(download_path, "%(title)s.%(ext)s")
    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '320',
        }],
        'noplaylist': True,  # avoid downloading whole playlist
        'outtmpl': mp3_template,
    }
    if sys.platform == "darwin":        # macos
        ffmpeg_path = '/opt/homebrew/bin/ffmpeg'
        if not os.path.isfile(ffmpeg_path):
            raise FileNotFoundError("ffmpeg was not found. Install it with 'brew install ffmpeg'")
        ydl_opts['ffmpeg_location'] = ffmpeg_path
    return ydl_opts


def download_mp3(link: str, destination_path: str = None) -> bool:
    """
    Downloads a mp3 from a YouTube link, retrying 5 times. Returns true if downloaded correctly
    :param link: YouTube link to download
    :param destination_path: path (if non-existing, it will be created) where files will be downloaded
    :return: True of downloaded ok
    """
    if destination_path is None:
        destination_path = base_dir
    os.makedirs(destination_path, exist_ok=True)
    with youtube_dl.YoutubeDL(get_ydl_opts(destination_path)) as ydl:
        for i in range(5):
            try:
                ydl.download([link])
                return True
            except Exception as e:
                print(e)
    return False


if __name__ == '__main__':
    # Testing with the imperial march!!!
    download_mp3(test_url)
