import flask_sqlalchemy


def LoadModel_User(db: flask_sqlalchemy.SQLAlchemy):
    class User(db.Model):
        __tablename__ = 'users'
        username = db.Column(db.String(50), primary_key=True, unique=True)
        password = db.Column(db.String(50))
        create_at = db.Column(db.DateTime)
    return User


def LoadModel_Task(db: flask_sqlalchemy.SQLAlchemy):
    class Task(db.Model):
        __tablename__ = 'tasks'
        id = db.Column(db.Integer, primary_key=True, autoincrement=True)
        subject = db.Column(db.String(50))
        description = db.Column(db.String(50))
        create_at = db.Column(db.DateTime)
    return Task
