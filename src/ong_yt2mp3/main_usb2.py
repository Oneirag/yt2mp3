"""
Lists all mp3 from a directory (defaults to E:\musica), looks for them in youtube and downloads
them again
"""

from __future__ import unicode_literals
import youtube_dl
import os

mp3_template = os.path.join(os.path.dirname(__file__),
                            "mp3",
                            "%(title)s.%(ext)s")


from youtubesearchpython import VideosSearch
files = [f.split(".")[0] for f in os.listdir(r"E:\musica") if f.endswith(".mp3")]
#print(files)
#print("Insert the video to search")
#search = input("")
for search in files:
    print(f"Searching {search}")
    videosSearch = VideosSearch(search, limit=2)

    print(videosSearch.result())
    result = videosSearch.result()['result'][0]
    id = result['id']
    link = f"https://www.youtube.com/watch?v={id}"

    #print("Insert the link")
    #link = input("")


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

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([link])
