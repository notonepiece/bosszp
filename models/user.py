# models.py
from db import db
from app import app

class User(db.Model):
    uid = db.Column(db.Integer, primary_key=True)
    account = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)

    def __repr__(self):
        return f'<User {self.account}>'

with app.app_context():
    db.create_all()
