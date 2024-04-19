from flask import Blueprint

from controller.downloadController import fetchDetails, downloadVideo

blueprint = Blueprint('blueprint', __name__)

blueprint.route('/fetch-info', methods=['POST'])(fetchDetails)
blueprint.route('/download', methods=['POST'])(downloadVideo)
