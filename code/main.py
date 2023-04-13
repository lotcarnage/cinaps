import models
import flask
import datetime
import flask_sqlalchemy

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = flask_sqlalchemy.SQLAlchemy(app)

Member = models.LoadModel_Member(db)
Fiscal = models.LoadModel_Fiscal(db)
Project = models.LoadModel_Project(db)
Task = models.LoadModel_Task(db)
WorkTime = models.LoadModel_WorkTime(db)


def _extract_date_str(dt: datetime.datetime):
    return f'{dt.year:4}-{dt.month:02}-{dt.day:02}'


def _extract_time_str(dt: datetime.datetime):
    return f'{dt.hour:02}:{dt.minute:02}'


def _load_tasks():
    tasks = Task.query.all()
    members = Member.query.all()
    worktimes = WorkTime.query.all()
    member_dict = {member.id: member for member in members}
    task_sheduled_time_dict = {task.id: 0 for task in tasks}
    task_progress_time_dict = {task.id: 0 for task in tasks}
    now = datetime.datetime.now()
    for worktime in worktimes:
        if (worktime.start_datetime + datetime.timedelta(minutes=worktime.span_minute)) <= now:
            task_progress_time_dict[worktime.task_id] += worktime.span_minute
        task_sheduled_time_dict[worktime.task_id] += worktime.span_minute
    for task in tasks:
        if task.asigned_member_id in member_dict:
            task.asigned_member_name = member_dict[task.asigned_member_id].display_name
        else:
            task.asigned_member_name = '未割り当て'
        task.sheduled_time = task_sheduled_time_dict[task.id]
        task.progress_time = task_progress_time_dict[task.id]
        task.man_minute = 0 if task.man_minute is None else task.man_minute
    return tasks


def _find_member_by_task(task):
    member = Member.query.filter_by(id=task.asigned_member_id).first()
    return member


@app.route('/', methods=['get'])
def index():
    return flask.render_template('index.html')


@app.route('/login', methods=['post'])
def login():
    login_name = flask.request.form.get('login_name')
    password = flask.request.form.get('password')
    member = Member.query.filter_by(login_name=login_name, password=password).first()
    if member is None:
        return flask.redirect('/')
    response = flask.make_response(flask.redirect(flask.url_for('home')))
    max_age = 60 * 30  # 30 minute
    expires = int(datetime.datetime.now().timestamp()) + max_age
    response.set_cookie('session_id', value='hogehoge', max_age=max_age, expires=expires, secure=None, httponly=False)
    response.set_cookie('member_id', value=str(member.id), max_age=max_age, expires=expires, secure=None, httponly=False)
    return response


@app.route('/home', methods=['get'])
def home():
    session_id = flask.request.cookies.get('session_id')
    member_id = flask.request.cookies.get('member_id')
    if session_id is None:
        return flask.redirect('/')
    member = Member.query.filter_by(id=member_id).first()
    projects = Project.query.all()
    tasks = _load_tasks()
    my_asigned_tasks = [task for task in tasks if task.asigned_member_id == member.id]
    return flask.render_template('home.html', member=member, projects=projects, tasks=my_asigned_tasks)


@app.route('/projects', methods=['get'])
def projects():
    projects = Project.query.all()
    for project in projects:
        project.task_count = len(Task.query.filter_by(parent_project_id=project.id).all())
    for project in projects:
        project.start_date = _extract_date_str(project.start_date)
        project.expected_finish_date = _extract_date_str(project.expected_finish_date)
    return flask.render_template('projects.html', projects=projects)


@app.route('/newproject', methods=['get'])
def newproject():
    return flask.render_template('newproject.html')


@app.route('/addproject', methods=['post'])
def addproject():
    project_name = flask.request.form.get('project_name')
    start_date = flask.request.form.get('start_date')
    expected_finish_date = flask.request.form.get('expected_finish_date')
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    expected_finish_date = datetime.datetime.strptime(expected_finish_date, '%Y-%m-%d')
    new_project = Project(display_name=project_name, start_date=start_date, expected_finish_date=expected_finish_date)
    db.session.add(new_project)
    db.session.commit()
    return flask.redirect('/projects')


@app.route('/projectedit', methods=['get'])
def projectedit():
    project_id = flask.request.args.get('id', '')
    project = Project.query.filter_by(id=project_id).first()
    tasks = Task.query.filter_by(parent_project_id=project_id).all()
    members = Member.query.all()
    tasks = _load_tasks()
    tasks_in_project = [task for task in tasks if task.parent_project_id == int(project_id)]
    return flask.render_template('projectedit.html', tasks=tasks_in_project, project=project, members=members)


@app.route('/addtask', methods=['post'])
def addtask():
    project_id = flask.request.form.get('project_id')
    subject = flask.request.form.get('subject')
    description = flask.request.form.get('description')
    asigned_member_id = flask.request.form.get('asigned_member_id')
    new_task = Task(subject=subject, description=description, parent_project_id=project_id, asigned_member_id=asigned_member_id)
    print(new_task)
    db.session.add(new_task)
    db.session.commit()
    return flask.redirect(f'/projectedit?id={project_id}')


@app.route('/calendar', methods=['get'])
def calendar():
    session_id = flask.request.cookies.get('session_id')
    member_id = flask.request.cookies.get('member_id')
    if session_id is None:
        return flask.redirect('/')
    member = Member.query.filter_by(id=int(member_id)).first()
    tasks = Task.query.all()
    today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    next_day = today + datetime.timedelta(days=1)
    worktimes = WorkTime.query.filter_by(member_id=member.id).all()
    worktimes = [worktime for worktime in worktimes if (today <= worktime.start_datetime < next_day)]
    task_name_dict = {task.id: task.subject for task in tasks}
    for worktime in worktimes:
        worktime.task_name = task_name_dict[worktime.task_id]
        worktime.start_time = _extract_time_str(worktime.start_datetime)
        worktime.end_time = _extract_time_str(worktime.start_datetime + datetime.timedelta(minutes=worktime.span_minute))
    worktimes = sorted(worktimes, key=lambda x: x.start_time)
    my_tasks = [task for task in tasks if task.asigned_member_id == member.id]
    return flask.render_template('calendar.html', tasks=my_tasks, worktimes=worktimes)


@app.route('/addworktime', methods=['post'])
def addworktime():
    task_id = flask.request.form.get('task_id')
    start_date = flask.request.form.get('start_date')
    start_time = flask.request.form.get('start_time')
    end_time = flask.request.form.get('end_time')
    d = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    s = datetime.datetime.strptime(start_time, '%H:%M')
    e = datetime.datetime.strptime(end_time, '%H:%M')
    s_d = datetime.datetime(year=d.year, month=d.month, day=d.day, hour=s.hour, minute=s.minute)
    span_minute = (e - s).total_seconds() // 60
    task = Task.query.filter_by(id=task_id).first()
    new_worktime = WorkTime(task_id=task_id, member_id=task.asigned_member_id, start_datetime=s_d, span_minute=span_minute)
    db.session.add(new_worktime)
    db.session.commit()
    return flask.redirect('/calendar')


@app.route('/editworktime_task', methods=['post'])
def editworktime_task():
    worktime_id = int(flask.request.form.get('worktime_id'))
    task_id = flask.request.form.get('task_id')
    worktime = WorkTime.query.filter_by(id=worktime_id).first()
    if task_id is None:
        return flask.redirect('/calendar')
    if task_id == 'delete':
        db.session.delete(worktime)
    else:
        worktime.task_id = task_id
    db.session.commit()
    return flask.redirect('/calendar')


@app.route('/delete_worktime', methods=['post'])
def delete_worktime():
    worktime_id = flask.request.form.get('worktime_id')
    worktime = WorkTime.query.filter_by(id=int(worktime_id)).first()
    db.session.delete(worktime)
    db.session.commit()
    return flask.redirect('/calendar')


def _init_db():
    user = Member.query.filter_by(login_name='testuser', password='hoge').first()
    if user is None:
        user = Member(login_name='testuser', password='hoge', display_name='作業員A')
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
