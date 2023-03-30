import flask
import datetime

app = flask.Flask(__name__)


def _try_login(user_id: str, password: str):
    return True


@app.route('/', methods=['get', 'post'])
def index():
    session_id = flask.request.cookies.get('session_id')
    print(session_id)
    if flask.request.method == 'GET':
        if session_id is not None:
            response_html = flask.render_template('home.html')
        else:
            response_html = flask.render_template('index.html')
    elif flask.request.method == 'POST':
        user_id = flask.request.form.get('user_id')
        password = flask.request.form.get('password')
        if _try_login(user_id, password):
            response_html = flask.render_template('home.html')
            response = flask.make_response(response_html)
            max_age = 60 * 60 * 24 * 2  # 2 days
            expires = int(datetime.datetime.now().timestamp()) + max_age
            response.set_cookie('session_id', value='hogehoge', max_age=max_age, expires=expires, path='/', secure=None, httponly=False)
            return response
        else:
            response_html = flask.render_template('index.html')
    return response_html


if __name__ == "__main__":
    app.run(debug=True)
