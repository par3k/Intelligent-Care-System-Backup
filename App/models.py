# -*- coding: utf-8 -*-
from . import db, login_manager
from flask_login import UserMixin
from datetime import datetime

# Set the Data base Model


@login_manager.user_loader
def load_user(worker_id):
    return Worker.query.get(worker_id)


class Worker(db.Model, UserMixin):
    __tablename__ = 'worker'
    id = db.Column(db.Integer, primary_key=True)  # For @login_manager.user_loader
    username = db.Column(db.CHAR(20), unique=True, nullable=False)
    email = db.Column(db.CHAR(120), unique=True, nullable=False)
    password = db.Column(db.VARCHAR(100), nullable=False)
    posts = db.relationship('Care_Post', backref='worker', lazy=True)  # For Post the Notice


class Patient(db.Model):
    __tablename__ = 'patient'
    id = db.Column(db.Integer, primary_key=True)  # For @login_manager.user_loader
    name = db.Column(db.CHAR(20), unique=True, nullable=False)
    sex = db.Column(db.CHAR(1), unique=False, nullable=True)
    age = db.Column(db.CHAR(2), unique=False, nullable=True)


class Care_Post(db.Model):  # For Care Post
    __tablename__ = 'c_post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)
    worker_id = db.Column(db.Integer, db.ForeignKey('worker.id'), nullable=False)

    def __repr__(self):
        return f"Care_Post('{self.title}', '{self.date_posted}')"


class Notice_Post(db.Model):  # For Notice Post
    __tablename__ = 'n_post'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=True, default=datetime.utcnow)