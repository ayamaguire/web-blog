import flask

web_app = flask.Flask(__name__)


@web_app.route('/')
def hello_world():
    return "Hello, world."


if __name__ == '__main__':
    web_app.run()
