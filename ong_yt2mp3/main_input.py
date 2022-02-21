"""
Asks for a path to download mp3 and the asks for youtube links to download into that directory
"""
from __future__ import unicode_literals
import os
import pynormalize
from ong_yt2mp3.download import download_mp3, base_dir


def get_mp3_dict(mp3_dir: str) -> dict:
    """Returns a dictionary of files (keys) and modification time (values)"""
    file_dict = {}
    for f in os.listdir(mp3_dir):
        if f.endswith(".mp3"):
            filename = os.path.join(mp3_dir, f)
            file_dict[filename] = os.path.getmtime(filename)
    return file_dict


def normalize_files(files: list = None, directory="mp3", target_dbfs=-13.5):
    """Normalizes volume of mp3 from the given list of files"""
    if files is None:
        files = get_mp3_dict(directory).keys()

    pynormalize.process_files(
        Files=files,
        target_dbfs=target_dbfs,
        directory=directory
    )


def download_youtube(destination_path: str):
    """Downloads files to the given path. Returns a list of downloaded files"""
    existing_mp3 = get_mp3_dict(destination_path)

    while True:
        link = input("Insert the youtube link: ")
        if not link:
            break
        download_mp3(link, destination_path)

    current_mp3 = get_mp3_dict(destination_path)
    downloaded_files = [f for f in current_mp3 if f not in existing_mp3 or existing_mp3[f] < current_mp3[f]]
    return downloaded_files


def main():
    mp3_subdirectory = input(f"Select destination directory (relative to {base_dir}) [Default: mp3]: ") or "mp3"
    mp3_directory = os.path.join(base_dir, mp3_subdirectory)
    print(f"Downloading to {mp3_directory}")
    os.makedirs(mp3_directory, exist_ok=True)
    downloaded_files = download_youtube(mp3_directory)

    if len(downloaded_files) == 0:
        # normalize volume of mp3 audio files
        yes_no = input("¿Normalize audio of mp3 files? (yes/no): ")
        if yes_no.upper() in ("YES", "Y"):
            normalize = True
            downloaded_files = get_mp3_dict(mp3_directory).keys()
        else:
            normalize = False
    else:
        normalize = True

    if normalize:
        print("Normalizing volume of files")
        normalize_files(downloaded_files, mp3_directory)

    print("Done")


if __name__ == '__main__':
    main()
