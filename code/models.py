import flask_sqlalchemy


def LoadModel_User(db: flask_sqlalchemy.SQLAlchemy):
    class User(db.Model):
        __tablename__ = 'users'
        username = db.Column(db.String(50), primary_key=True, unique=True)
        password = db.Column(db.String(50))
        create_at = db.Column(db.DateTime)
    return User
