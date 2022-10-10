from db import db
from sqlalchemy.sql import func
import os
from datetime import datetime


class Posts(db.Model):
    __tablename__ = 'posts'

    post_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    description = db.Column(db.String(1000))
    image_path = db.Column(db.String(255), unique=True)
    updated_at = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))

    def save(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_list_of_dict(cls):
        return [r.__dict__ for r in cls.query.filter_by().all()]

    @classmethod
    def find_by_id(cls, post_id):
        return cls.query.filter_by(post_id=post_id).first()
