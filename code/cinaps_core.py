from flask_sqlalchemy import SQLAlchemy
from models import Member, Fiscal, Project, Task, Deliverable, Work, TaskInputDeliverable
import datetime


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


class CinapsCore:
    def Login(login_name: str, password: str) -> Member | None:
        member = Member.query.filter_by(login_name=login_name).first()
        if member is None:
            return None
        hashed_password = _hash_password(password, member.password_salt)
        if member.password != hashed_password:
            return None
        return member

    def __init__(self, db: SQLAlchemy) -> None:
        self.__db = db
        return None

    def AddMember(self, login_name: str, password: str, display_name=str) -> None:
        self.__db.session.add(_new_member(login_name, password, display_name))
        return None

    def AddProject(self, project_name: str, start_datetime: datetime.datetime, expected_finish_datetime: datetime.datetime) -> None:
        new_project = Project(display_name=project_name, start_date=start_datetime, expected_finish_date=expected_finish_datetime)
        self.__db.session.add(new_project)
        return None

    def AddTask(self, subject: str, description: str | None, parent_project_id: int, assigned_member_id: int | None) -> None:
        new_task = Task(subject=subject, description=description, parent_project_id=parent_project_id, asigned_member_id=assigned_member_id)
        self.__db.session.add(new_task)
        return None

    def AddDeliverable(self, label: str, description: str | None, parent_project_id: int, production_task_id: int | None) -> None:
        new_task = Deliverable(label=label, description=description, parent_project_id=parent_project_id, production_task_id=production_task_id)
        self.__db.session.add(new_task)
        return None

    def AddTaskInputDeliverable(self, task_id: int, deliverable_id: id) -> None:
        exists = TaskInputDeliverable.query.filter_by(task_id=task_id, deliverable_id=deliverable_id)
        if exists is None:
            new_task_inout_deliverable = TaskInputDeliverable(task_id=task_id, deliverable_id=deliverable_id)
            self.__db.session.add(new_task_inout_deliverable)
        return None

    def FindMemberById(self, member_id: int) -> Member | None:
        member = Member.query.filter_by(id=member_id).first()
        return member

    def FindTaskById(self, task_id: int) -> Task | None:
        task = Task.query.filter_by(id=int(task_id)).first()
        return task

    def FindDeliverableById(self, deliverable_id: int) -> Deliverable | None:
        deliverable = Deliverable.query.filter_by(id=int(deliverable_id)).first()
        return deliverable

    def GetAllTask(self) -> list[Task]:
        return Task.query.all()

    def GetAllDeliverables(self) -> list[Deliverable]:
        return Deliverable.query.all()

    def GetAllTaskInputDeliverable(self) -> list[TaskInputDeliverable]:
        return TaskInputDeliverable.query.all()

    def Commit(self) -> None:
        self.__db.session.commit()
        return None
