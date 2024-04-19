import os
from flask import request, send_file

from service.DownloadService import fetchInfo, downloadVideos, delete_old_files


def fetchDetails():
    global json_data
    if request.is_json:
        # Retrieve the JSON data from the request
        json_data = request.get_json()
    return fetchInfo(json_data['url'])


def downloadVideo():
    if request.is_json:
        json_data = request.get_json()

        videos = json_data.get('videos', [])
        is_video = json_data.get('isVideo', False)
    file_path = downloadVideos(videos, is_video)
    return send_file(file_path, as_attachment=True, download_name=os.path.basename(file_path))


# Schedule this function to run every 6 hours and clean the download folder
def scheduled_task():
    print("🧹🌊 Starting cleanup! Checking for old downloads... 🔍")
    parent_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    download_dir = os.path.join(parent_directory, "downloads")

    directory = download_dir + "/video/"
    delete_old_files(directory)
    print(f"📹 Removed old video files from {directory}! (if any) 🗑 \n")

    directory = download_dir + "/audio/"
    delete_old_files(directory)
    print(f"🔊 Removed old audio files from {directory}! (if any) 🗑 \n")

    print("🎉 Cleanup complete! Everything is tidy now. 🙂")
