from flask import Blueprint

from controller.downloadController import fetchDetails

blueprint = Blueprint('blueprint', __name__)

blueprint.route('/fetch-info', methods=['POST'])(fetchDetails)
