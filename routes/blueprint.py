from flask import Blueprint

from controller.downloadController import fetchSingleDetails

blueprint = Blueprint('blueprint', __name__)

blueprint.route('/fetch/single', methods=['GET'])(fetchSingleDetails)
