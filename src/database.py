from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import string
import random

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False, unique=True)
    email = db.Column(db.String(80), nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False, unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now())
    update_at = db.Column(db.DateTime, onupdate=datetime.now())
    bookmarks = db.relationship("Bookmark", backref="user")

    def __repr__(self) -> str:
        return 'User >>>{self.username}'


class Bookmark(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text, nullable=False)
    url = db.Column(db.Text, nullable=False)
    short_url = db.Column(db.String(3), nullable=False)
    visiters = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    created_at = db.Column(db.DateTime, default=datetime.now())
    update_at = db.Column(db.DateTime, onupdate=datetime.now())

    def generate_short_character(self):
        characters = string.digits+string.ascii_letters
        picked_characters = ''.join(random.choices(characters, k=3))

        link = self.query.filter_by(short_url=picked_characters).first()

        if link:
            self.generate_short_character()

        else:
            return picked_characters

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.short_url = self.generate_short_character()

    def __repr__(self) -> str:
        return 'Bookmark >>>{self.id}'
