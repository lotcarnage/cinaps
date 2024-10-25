from flask_sqlalchemy import SQLAlchemy
from models import Member, Fiscal, Project, Task, Work

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
    def Login(login_name:str, password:str) -> Member | None:
        member = Member.query.filter_by(login_name=login_name).first()
        if member is None:
            return None
        hashed_password = _hash_password(password, member.password_salt)
        if member.password != hashed_password:
            return None
        return member

    def __init__(self, db:SQLAlchemy) -> None:
        self.__db = db
        return None

    def AddMember(self, login_name:str, password:str, display_name=str) -> None:
        self.__db.session.add(_new_member(login_name, password, display_name))
        return None
    
    def FindMemberById(self, member_id:int) -> Member | None:
        member = Member.query.filter_by(id=member_id).first()
        return member


    def Commit(self) -> None:
        self.__db.session.commit()
        return None


