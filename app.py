from flask import Flask
from flask_apscheduler import APScheduler

from controller.downloadController import scheduled_task
from routes.blueprint import blueprint

app = Flask(__name__)

app.register_blueprint(blueprint, url_prefix='/yt')
scheduler = APScheduler()


@scheduler.task('interval', id='my_job', hour='*/6', minute='0')
def delete_files():
    print("\n 🕒 Scheduled job started! 🕒 \n")
    scheduled_task()
    print("\n 🛑 Scheduled job ended! 🛑 \n")


if __name__ == '__main__':
    scheduler.init_app(app)
    scheduler.start()
    app.run(host='0.0.0.0', debug=False, port=5000)  # Run the app on port 5000
