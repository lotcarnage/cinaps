import flask

app = flask.Flask(__name__)


@app.route('/', methods=['get', 'post'])
def index():
    user_id = flask.request.form.get('user_id')
    password = flask.request.form.get('password')
    print(user_id, password)
    return flask.render_template('index.html')


if __name__ == "__main__":
    app.run(debug=True)
