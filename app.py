from flask import Flask

from routes.blueprint import blueprint

app = Flask(__name__)

app.register_blueprint(blueprint, url_prefix='/yt')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)  # Run the app on port 5000
