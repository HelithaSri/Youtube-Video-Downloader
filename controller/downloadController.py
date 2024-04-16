from flask import request

from service.DownloadService import fetchInfo


def fetchDetails():
    if request.is_json:
        # Retrieve the JSON data from the request
        json_data = request.get_json()
    return fetchInfo(json_data['url'])
