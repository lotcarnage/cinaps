import flask_sqlalchemy
import enum


class ProjectState(enum.Enum):
    PREPARING = 0
    DOING = 1
    COMPLETED = 2
    LOST = 3


class TaskState(enum.Enum):
    WAITING = 0
    WORKING = 1
    WAITING_REVIEW = 2
    COMPLETED = 3
    CANCELED = 4


def LoadModel_Member(db: flask_sqlalchemy.SQLAlchemy):
    class Member(db.Model):
        __tablename__ = 'members'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        login_name = db.Column(db.String(50), unique=True)
        password = db.Column(db.String(50))
        display_name = db.Column(db.String(50))
        create_at = db.Column(db.DateTime)
    return Member


def LoadModel_Fiscal(db: flask_sqlalchemy.SQLAlchemy):
    class Fiscal(db.Model):
        __tablename__ = 'fiscals'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        display_name = db.Column(db.String(50), unique=True)
        sales_goal = db.Column(db.Integer)
        state = db.Column(db.Enum(ProjectState))
        start_date = db.Column(db.DateTime)
        end_date = db.Column(db.DateTime)
    return Fiscal


def LoadModel_Project(db: flask_sqlalchemy.SQLAlchemy):
    class Project(db.Model):
        __tablename__ = 'projects'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        fiscal_id = db.Column(db.Integer)
        sales_budget = db.Column(db.Integer)
        display_name = db.Column(db.String(50), unique=True)
        state = db.Column(db.Enum(ProjectState))
        start_date = db.Column(db.DateTime)
        expected_finish_date = db.Column(db.DateTime)
    return Project


def LoadModel_Task(db: flask_sqlalchemy.SQLAlchemy):
    class Task(db.Model):
        __tablename__ = 'tasks'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        asigned_member_id = db.Column(db.Integer)
        reviewer_id = db.Column(db.Integer)
        parent_project_id = db.Column(db.Integer)
        subject = db.Column(db.String(50))
        description = db.Column(db.String(50))
        create_at = db.Column(db.DateTime)
        man_minute = db.Column(db.Integer)
        limit_datetime = db.Column(db.DateTime)
    return Task


def LoadModel_Work(db: flask_sqlalchemy.SQLAlchemy):
    class Work(db.Model):
        __tablename__ = 'works'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
        member_id = db.Column(db.Integer, db.ForeignKey('members.id'), nullable=False)
        start_datetime = db.Column(db.DateTime)
        span_minute = db.Column(db.Integer)
    return Work
