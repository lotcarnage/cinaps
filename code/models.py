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


def LoadModel_User(db: flask_sqlalchemy.SQLAlchemy):
    class User(db.Model):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        username = db.Column(db.String(50), unique=True)
        password = db.Column(db.String(50))
        create_at = db.Column(db.DateTime)
    return User


def LoadModel_Project(db: flask_sqlalchemy.SQLAlchemy):
    class Project(db.Model):
        __tablename__ = 'projects'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        name = db.Column(db.String(50), unique=True)
        sales_budget = db.Column(db.Integer)
        state = db.Column(db.Enum(ProjectState))
        create_at = db.Column(db.DateTime)
    return Project


def LoadModel_Task(db: flask_sqlalchemy.SQLAlchemy):
    class Task(db.Model):
        __tablename__ = 'tasks'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        asigned_user_id = db.Column(db.Integer)
        parent_project_id = db.Column(db.Integer)
        subject = db.Column(db.String(50))
        description = db.Column(db.String(50))
        create_at = db.Column(db.DateTime)
        estimation_working_minute = db.Column(db.Integer)
    return Task


def LoadModel_WorkSchedule(db: flask_sqlalchemy.SQLAlchemy):
    class WorkSchedule(db.Model):
        __tablename__ = 'workschedules'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        asigned_user_id = db.Column(db.Integer)
        parent_task_id = db.Column(db.Integer)
        start_at = db.Column(db.DateTime)
        working_minute = db.Column(db.Integer)
    return WorkSchedule
