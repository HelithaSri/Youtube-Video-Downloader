import json
import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


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
