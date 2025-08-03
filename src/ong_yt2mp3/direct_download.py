URL="https://www.youtube.com/playlist?list=PLDRpzOCW8BJU_Gbh4T-29GSQ8d_Cap9Oi"

from pathlib import Path
import yt_dlp
from download import get_ydl_opts


#URL = 'https://www.youtube.com/watch?v=BaW_jenozKc'
is_video = False  # Set to True if you want to download as video
# is_video = True

download_path = Path(__file__).parent / "downloads"
if is_video:
    download_path /= "videos"
else:
    download_path /= "mp3"

download_path.mkdir(exist_ok=True)

ydl_opts = get_ydl_opts(download_path, is_video=is_video, allow_playlist=True)

# With 'pip install pip-system-certs' you can use the system certificates and avoid SSL errors
# ydl_opts['nocheckcertificate'] = True  # Ignore SSL certificate errors
ydl_opts['concurrent_fragment_downloads'] = 4
ydl_opts['ignoreerrors'] = True  # Ignore errors in the download process
ydl_opts['download_archive'] = download_path.parent / 'downloaded.txt'  # archivo donde se guardan los IDs


with yt_dlp.YoutubeDL(ydl_opts, ) as ydl:
    error_code = ydl.download([URL])

