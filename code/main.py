import models
import flask
import datetime
import flask_sqlalchemy

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = flask_sqlalchemy.SQLAlchemy(app)

User = models.LoadModel_User(db)
Project = models.LoadModel_Project(db)
Task = models.LoadModel_Task(db)
WorkSchedule = models.LoadModel_WorkSchedule(db)


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
    response = flask.make_response(flask.redirect(flask.url_for('home')))
    max_age = 60  # 10 sec
    expires = int(datetime.datetime.now().timestamp()) + max_age
    response.set_cookie('session_id', value='hogehoge', max_age=max_age, expires=expires, secure=None, httponly=False)
    return response


@app.route('/home', methods=['get'])
def home():
    session_id = flask.request.cookies.get('session_id')
    print(flask.request.cookies)
    print(session_id)
    if session_id is None:
        return flask.redirect('/')
    projects = Project.query.all()
    tasks = Task.query.all()
    return flask.render_template('home.html', projects=projects, tasks=tasks)


@app.route('/projects', methods=['get'])
def projects():
    projects = Project.query.all()
    for project in projects:
        project.task_count = len(Task.query.filter_by(parent_project_id=project.id).all())
    return flask.render_template('projects.html', projects=projects)


@app.route('/addproject', methods=['post'])
def addproject():
    project_name = flask.request.form.get('project_name')
    new_project = Project(name=project_name, create_at=datetime.datetime.now())
    db.session.add(new_project)
    db.session.commit()
    return flask.redirect('/projects')


@app.route('/projectedit', methods=['get'])
def projectedit():
    project_id = flask.request.args.get('id', '')
    project = Project.query.filter_by(id=project_id).first()
    tasks = Task.query.filter_by(parent_project_id=project_id).all()
    return flask.render_template('projectedit.html', tasks=tasks, project=project)


@app.route('/addtask', methods=['post'])
def addtask():
    project_id = flask.request.form.get('project_id')
    subject = flask.request.form.get('subject')
    description = flask.request.form.get('description')
    new_task = Task(subject=subject, description=description, parent_project_id=project_id)
    db.session.add(new_task)
    db.session.commit()
    return flask.redirect(f'/projectedit?id={project_id}')


def _init_db():
    user = User.query.filter_by(username='testuser', password='hoge').first()
    if user is None:
        user = User(username='testuser', password='hoge')
        db.session.add(user)
        db.session.commit()
    return None


if __name__ == "__main__":
    import sys
    if 1 < len(sys.argv):
        with app.app_context():
            db.create_all()
            _init_db()
    else:
        app.run(debug=True)
