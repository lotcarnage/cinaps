from models import Member, Fiscal, Project, Task, Work, Deliverable
import flask
import datetime
from flask_sqlalchemy_wrapper import db
from cinaps_core import CinapsCore
import cinaps_dfd

app = flask.Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db.init_app(app)
cinaps = CinapsCore(db)


def _date_str_to_datetime(date_str: str) -> datetime.datetime | None:
    if date_str == "":
        return None
    return datetime.datetime.strptime(date_str, '%Y-%m-%d')


def _extract_date_str(dt: datetime.datetime):
    if dt is None:
        return ""
    return f'{dt.year:4}-{dt.month:02}-{dt.day:02}'


def _extract_time_str(dt: datetime.datetime):
    if dt is None:
        return ""
    return f'{dt.hour:02}:{dt.minute:02}'


def _load_tasks():
    tasks = Task.query.all()
    members = Member.query.all()
    works = Work.query.all()
    member_dict = {member.id: member for member in members}
    task_sheduled_time_dict = {task.id: 0 for task in tasks}
    task_progress_time_dict = {task.id: 0 for task in tasks}
    now = datetime.datetime.now()
    for work in works:
        if (work.start_datetime + datetime.timedelta(minutes=work.span_minute)) <= now:
            task_progress_time_dict[work.task_id] += work.span_minute
        task_sheduled_time_dict[work.task_id] += work.span_minute
    for task in tasks:
        if task.asigned_member_id in member_dict:
            task.asigned_member_name = member_dict[task.asigned_member_id].display_name
        else:
            task.asigned_member_name = '未割り当て'
        task.sheduled_time = task_sheduled_time_dict[task.id]
        task.progress_time = task_progress_time_dict[task.id]
        man_minute = 0 if task.man_minute is None else task.man_minute
        task.limit_date = _extract_date_str(task.limit_datetime)
        task.man_days = man_minute // (8 * 60)
        task.man_hours = (man_minute % (8 * 60)) // 60
        task.man_minutes = (man_minute % 60)
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
    member: Member | None = CinapsCore.Login(login_name, password)
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
    member = cinaps.FindMemberById(member_id)
    projects = Project.query.all()
    tasks = _load_tasks()
    my_asigned_tasks = [task for task in tasks if task.asigned_member_id == member.id]
    members = Member.query.all()
    return flask.render_template('home.html', member=member, projects=projects, tasks=my_asigned_tasks, members=members)


@app.route('/projects', methods=['get'])
def projects():
    projects = Project.query.all()
    for project in projects:
        project.task_count = len(Task.query.filter_by(parent_project_id=project.id).all())
    for project in projects:
        project.start_date = _extract_date_str(project.start_date)
        project.expected_finish_date = _extract_date_str(project.expected_finish_date)
    return flask.render_template('projects.html', projects=projects)


@app.route('/projects_dfd', methods=['get'])
def projects_dfd():
    deliverables = cinaps.GetAllDeliverables()
    tasks = cinaps.GetAllTask()
    task_input_deliverables = cinaps.GetAllTaskInputDeliverable()
    dfd_tasks = [cinaps_dfd.DfdTask(task, task_input_deliverables) for task in tasks]
    dfd_deliverables = [cinaps_dfd.DfdDeliverable(deliverable) for deliverable in deliverables]
    deliverable_to_task_edges = [cinaps_dfd.DfdDeliverableToTask(task_input_deliverable.deliverable_id, task_input_deliverable.task_id) for task_input_deliverable in task_input_deliverables]
    task_to_deliverable_edges = [cinaps_dfd.DfdTaskToDeliverable(dfd_deliverable.id, dfd_deliverable.production_task_id) for dfd_deliverable in dfd_deliverables]
    projects = Project.query.all()
    members = Member.query.all()
    for project in projects:
        project.task_count = len(Task.query.filter_by(parent_project_id=project.id).all())
    for project in projects:
        project.start_date = _extract_date_str(project.start_date)
        project.expected_finish_date = _extract_date_str(project.expected_finish_date)
    return flask.render_template(
        'projects_dfd.html',
        projects=projects,
        members=members,
        dfd_tasks=dfd_tasks, dfd_deliverables=dfd_deliverables,
        task_to_deliverable_edges=task_to_deliverable_edges,
        deliverable_to_task_edges=deliverable_to_task_edges)


@app.route('/newproject', methods=['get'])
def newproject():
    return flask.render_template('newproject.html')


@app.route('/addproject', methods=['post'])
def addproject():
    project_name = flask.request.form.get('project_name')
    start_date = flask.request.form.get('start_date')
    expected_finish_date = flask.request.form.get('expected_finish_date')
    start_date = _date_str_to_datetime(start_date)
    expected_finish_date = _date_str_to_datetime(expected_finish_date)
    cinaps.AddProject(project_name, start_date, expected_finish_date)
    cinaps.Commit()
    return flask.redirect('/projects')


@app.route('/projectedit', methods=['get'])
def projectedit():
    project_id = flask.request.args.get('id', '')
    project = Project.query.filter_by(id=project_id).first()
    tasks = Task.query.filter_by(parent_project_id=project_id).all()
    deliverables = Deliverable.query.filter_by(parent_project_id=project_id).all()
    members = Member.query.all()
    tasks = _load_tasks()
    tasks_in_project = [task for task in tasks if task.parent_project_id == int(project_id)]
    return flask.render_template('projectedit.html', tasks=tasks_in_project, project=project, members=members, deliverables=deliverables)


@app.route('/addtask', methods=['post'])
def addtask():
    project_id = flask.request.form.get('project_id')
    subject = flask.request.form.get('subject')
    description = flask.request.form.get('description')
    asigned_member_id = flask.request.form.get('asigned_member_id')
    cinaps.AddTask(subject, description, project_id, asigned_member_id)
    db.session.commit()
    return flask.redirect(f'/projectedit?id={project_id}')


@app.route('/adddeliverable', methods=['post'])
def adddeliverable():
    project_id = flask.request.form.get('project_id')
    label = flask.request.form.get('label')
    description = flask.request.form.get('description')
    cinaps.AddDeliverable(label, description, project_id, None)
    db.session.commit()
    return flask.redirect(f'/projectedit?id={project_id}')


@app.route('/updatetask', methods=['post'])
def updatetask():
    task_id = flask.request.form.get('task_id')
    subject = flask.request.form.get('subject')
    description = flask.request.form.get('description')
    asigned_member_id = flask.request.form.get('asigned_member_id')
    reviewer_id = flask.request.form.get('reviewer_id')
    state = flask.request.form.get('state')
    limit_datetime = flask.request.form.get('limit_datetime')
    man_days = flask.request.form.get('man_days')
    man_hours = flask.request.form.get('man_hours')
    man_minutes = flask.request.form.get('man_minutes')
    man_days = 0 if man_days is None else man_days
    man_hours = 0 if man_hours is None else man_hours
    man_minutes = 0 if man_minutes is None else man_minutes
    man_minute = int(man_days) * 8 * 60 + int(man_hours) * 60 + int(man_minutes)
    task = cinaps.FindTaskById(int(task_id))
    task.subject = subject
    task.description = description
    task.asigned_member_id = asigned_member_id
    task.reviewer_id = reviewer_id
    task.state = state
    task.limit_datetime = _date_str_to_datetime(limit_datetime)
    task.man_minute = man_minute
    db.session.commit()
    return flask.redirect('/home')


@app.route('/updatetaskdepend', methods=['post'])
def updatetaskdepend():
    task_id = flask.request.form.get('task_id')
    subject = flask.request.form.get('subject')
    description = flask.request.form.get('description')
    asigned_member_id = flask.request.form.get('asigned_member_id')
    state = flask.request.form.get('state')
    depends = flask.request.form.get('depends')
    print(depends, task_id, subject)
    depends = depends.rstrip(',').split(',')
    print(depends)
    task = cinaps.FindTaskById(int(task_id))
    task.subject = subject
    task.description = description
    task.asigned_member_id = asigned_member_id
    task.state = state
    for depend_deliverable_id in depends:
        cinaps.AddTaskInputDeliverable(task_id, depend_deliverable_id)
    db.session.commit()
    return flask.redirect('/projects_dfd')


@app.route('/updatedeliverable', methods=['post'])
def updatedeliverable():
    deliverable_id = flask.request.form.get('deliverable_id')
    deliverable_label = flask.request.form.get('deliverable_label')
    producer_task_id = flask.request.form.get('producer_task_id')
    description = flask.request.form.get('description')
    deliverable = cinaps.FindDeliverableById(int(deliverable_id))
    deliverable.label = deliverable_label
    deliverable.description = description
    deliverable.production_task_id = producer_task_id
    db.session.commit()
    return flask.redirect('/projects_dfd')


@app.route('/calendar', methods=['get'])
def calendar():
    session_id = flask.request.cookies.get('session_id')
    member_id = flask.request.cookies.get('member_id')
    if session_id is None:
        return flask.redirect('/')
    target_day = flask.request.args.get('date', '')
    print(target_day)
    if target_day == "":
        target_day = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        target_day = _date_str_to_datetime(target_day)
    member = Member.query.filter_by(id=int(member_id)).first()
    tasks = Task.query.all()
    next_day = target_day + datetime.timedelta(days=1)
    works = Work.query.filter_by(member_id=member.id).all()
    works = [work for work in works if (target_day <= work.start_datetime < next_day)]
    task_name_dict = {task.id: task.subject for task in tasks}
    for work in works:
        work.task_name = task_name_dict[work.task_id]
        work.start_time = _extract_time_str(work.start_datetime)
        work.end_time = _extract_time_str(work.start_datetime + datetime.timedelta(minutes=work.span_minute))
    works = sorted(works, key=lambda x: x.start_time)
    my_tasks = [task for task in tasks if task.asigned_member_id == member.id]
    return flask.render_template('calendar.html', tasks=my_tasks, works=works, date=_extract_date_str(target_day))


@app.route('/addwork', methods=['post'])
def addwork():
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
    new_work = Work(task_id=task_id, member_id=task.asigned_member_id, start_datetime=s_d, span_minute=span_minute)
    db.session.add(new_work)
    db.session.commit()
    print(start_date)
    return flask.redirect(flask.url_for('calendar', date=start_date))


@app.route('/editwork_task', methods=['post'])
def editwork_task():
    work_id = int(flask.request.form.get('work_id'))
    task_id = flask.request.form.get('task_id')
    start_date = flask.request.form.get('start_date')
    work = Work.query.filter_by(id=work_id).first()
    if task_id is None:
        return flask.redirect('/calendar')
    if task_id == 'delete':
        db.session.delete(work)
    else:
        work.task_id = task_id
    db.session.commit()
    print(start_date)
    return flask.redirect(flask.url_for('calendar', date=start_date))


@app.route('/delete_work', methods=['post'])
def delete_work():
    work_id = flask.request.form.get('work_id')
    work = Work.query.filter_by(id=int(work_id)).first()
    db.session.delete(work)
    db.session.commit()
    return flask.redirect('/calendar')


def _make_salt():
    import secrets
    return secrets.token_hex(32)


def _hash_password(password: str, salt: str) -> str:
    import hashlib
    return hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 2)


def _new_member(login_name: str, password: str, display_name: str) -> Member:
    salt = _make_salt()
    hashed_password = _hash_password(password, salt)
    return Member(login_name=login_name, password=hashed_password, display_name=display_name, password_salt=salt)


def _init_db():
    user = Member.query.filter_by(login_name='test').first()
    if user is None:
        cinaps.AddMember(login_name='test', password='test', display_name='作業員A')
        cinaps.AddMember(login_name='test2', password='hoge', display_name='作業員B')
        cinaps.AddMember(login_name='test3', password='hoge', display_name='作業員C')
        cinaps.Commit()
    return None


if __name__ == "__main__":
    import sys
    if 1 < len(sys.argv):
        with app.app_context():
            db.create_all()
            _init_db()
    else:
        app.run(debug=True)
