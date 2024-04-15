from flask import Flask

from routes.blueprint import blueprint

app = Flask(__name__)

app.register_blueprint(blueprint, url_prefix='/download')

if __name__ == '__main__':
    app.run(debug=True, port=5000)  # Run the app on port 5000
