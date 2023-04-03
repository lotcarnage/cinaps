import models
import flask
import datetime
import flask_sqlalchemy

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = flask_sqlalchemy.SQLAlchemy(app)

User = models.LoadModel_User(db)


def _try_login(user_id: str, password: str) -> bool:
    user = User.query.filter_by(username=user_id, password=password).first()
    return user is not None


@app.route('/', methods=['get'])
def index():
    return flask.render_template('index.html')


@app.route('/login', methods=['post'])
def login():
    user_id = flask.request.form.get('user_id')
    password = flask.request.form.get('password')
    if _try_login(user_id, password) is False:
        return flask.redirect('/')
    response_html = flask.render_template('home.html')
    response = flask.make_response(response_html)
    max_age = 10  # 10 sec
    expires = int(datetime.datetime.now().timestamp()) + max_age
    response.set_cookie('session_id', value='hogehoge', max_age=max_age, expires=expires, path='/', secure=None, httponly=False)
    return flask.redirect('/home', Response=response)


@app.route('/home', methods=['get'])
def home():
    session_id = flask.request.cookies.get('session_id')
    print(flask.request.cookies)
    print(session_id)
    if session_id is None:
        return flask.redirect('/')
    return flask.render_template('home.html')


def _init_db():
    user = User.query.filter_by(username='testuser', password='hoge').first()
    if user is None:
        user = User(username='testuser', password='hoge')
        db.session.add(user)
        db.session.commit()
    return None


if __name__ == "__main__":
    if False:
        with app.app_context():
            db.create_all()
            _init_db()
    else:
        app.run(debug=True)
