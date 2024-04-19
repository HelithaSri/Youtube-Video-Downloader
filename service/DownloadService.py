import datetime
import json
import os
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup
from pytube import YouTube


def fetchInfo(url):
    if "youtu.be" in url:
        url = url.replace("https://youtu.be/", "https://www.youtube.com/watch?v=")

    video_info = []
    parsed_url = urlparse(url)
    allowed_netlocs = ['youtube.com', 'www.youtube.com', 'youtu.be']
    if parsed_url.netloc not in allowed_netlocs:
        return None  # Not a YouTube URL

    video_id_match = re.search(r'(v/|embed/|watch\?v=)([^&]+)', url)
    playlist_id_match = re.search(r'list=([^&]+)', url)

    if video_id_match:
        video_id = video_id_match.group(2)
        # Process single video
        try:
            # (Replace with a reliable user-agent string)
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(f'https://www.youtube.com/watch?v={video_id}', headers=headers)

            if response.status_code != 200:
                return None  # Error fetching page

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract data based on HTML structure (may change)
            thumbnail_meta = soup.find('link', itemprop='thumbnailUrl')
            title_meta = soup.find('meta', itemprop='name')

            if not (thumbnail_meta and title_meta):
                return None  # Data not found

            thumbnail_url = thumbnail_meta['href']
            title = title_meta['content']

            video_info.append({'video_id': video_id, 'title': title, 'thumbnail_url': thumbnail_url,
                               'source_url': url})
            return video_info
        except Exception as e:
            print(f"Error parsing HTML for video: {e}")
            return None

    elif playlist_id_match:
        playlist_id = playlist_id_match.group(1)

        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            return None  # Error fetching page

        soup = BeautifulSoup(response.text, 'html.parser')
        script_tags = soup.find_all('script')

        # Search for the script tag containing the video information
        for script_tag in script_tags:
            if 'ytInitialData' in str(script_tag):
                data_str = str(script_tag)
                break

        # Extract the JSON-like string containing video information
        json_str = re.search(r'({.*})', data_str).group(1)
        data = json.loads(json_str)

        videos = data['contents']['twoColumnBrowseResultsRenderer']['tabs'][0]['tabRenderer']['content'][
            'sectionListRenderer']['contents'][0]['itemSectionRenderer']['contents'][0]['playlistVideoListRenderer'][
            'contents']

        # Extract video information
        for video in videos:
            video_renderer = video.get('playlistVideoRenderer')
            if video_renderer:
                video_id = video_renderer['videoId']
                video_title = video_renderer['title']['runs'][0]['text']
                thumbnail_url = video_renderer['thumbnail']['thumbnails'][-1]['url']
                source_url = f'https://www.youtube.com/watch?v={video_id}'
                video_info.append({'video_id': video_id, 'title': video_title, 'thumbnail_url': thumbnail_url,
                                   'source_url': source_url})
        return video_info

    else:
        # Not a valid video or playlist URL
        return None


def downloadVideos(videos, is_video):
    print(videos)

    parent_directory = os.path.abspath(os.path.join(os.getcwd(), os.pardir))

    download_dir = os.path.join(parent_directory, "downloads")
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
        print("Create downloads folder in " + download_dir)
    if not os.path.exists(download_dir + "/video"):
        os.makedirs(download_dir + "/video")
        print("Create video folder in " + download_dir + "/video")
    if not os.path.exists(download_dir + "/audio"):
        os.makedirs(download_dir + "/audio")
        print("Create audio folder in " + download_dir + "/audio")

    audio_dir = download_dir + "/audio/"
    video_dir = download_dir + "/video/"

    for idx, video_id in enumerate(videos):
        idx = idx + 1
        try:
            print(f"Downloading... {idx} - {video_id}...")
            yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")

            if is_video:
                file_name = remove_forbidden_characters(yt.title) + ".mp4"
                stream = yt.streams.first()
                stream.download(filename=video_dir + file_name)
                file_path = os.path.join(video_dir, file_name)
                print(f"Video {idx} downloaded successfully!")

            else:
                file_name = remove_forbidden_characters(yt.title) + ".mp3"
                stream = yt.streams.filter(only_audio=True).first()
                stream.download(filename=audio_dir + file_name)
                print(f"Audio {idx} downloaded successfully!")
                file_path = os.path.join(audio_dir, file_name)
        except Exception as e:
            print(f"Error downloading video {idx}: {str(e)}")
    print("Path to the downloaded file:", file_path)
    print("Downloaded successfully!")
    return file_path


def remove_forbidden_characters(title):
    forbidden_pattern = r'[\\/:\*\?"<>|()]'
    clean_title = re.sub(forbidden_pattern, '', title)
    return clean_title


def delete_old_files(directory):
    now = datetime.datetime.now()
    one_hour_ago = now - datetime.timedelta(hours=1)

    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            creation_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))

            if creation_time < one_hour_ago:
                os.remove(file_path)
                print(f"🗑 Deleted {file_path}")
