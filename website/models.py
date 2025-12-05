from . import db
from flask_login import UserMixin
from sqlalchemy.sql import func
import secrets
import string
import random
from datetime import datetime,timezone,timedelta
class Subjects(db.Model):
    id = db.Column(db.String(64), primary_key=True, default = ''.join(random.choices(string.ascii_letters + string.digits, k=16)))
    name = db.Column(db.String(150),default="Untitled Draft")
    datetime = db.Column(db.String(150),default=datetime.now(timezone(timedelta(hours=8))).strftime("%d/%m/%Y %H:%M:%S"))
    lote = db.Column(db.String(150),default="")
    lote_level = db.Column(db.String(150),default="")
    elective1 = db.Column(db.String(150),default="")
    elective2 = db.Column(db.String(150),default="")
    elective3 = db.Column(db.String(150),default="")
    reserve_choice = db.Column(db.String(150),default="")
    group1 = db.Column(db.String(150),default="")
    group2 = db.Column(db.String(150),default="")
    group3 = db.Column(db.String(150),default="")
    group4 = db.Column(db.String(150),default="")
    group5 = db.Column(db.String(150),default="")
    group6 = db.Column(db.String(150),default="")
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    selected = db.Column(db.Boolean,default=False)
    course = db.Column(db.String(150),default="")
    # This is the database for the subject choices
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    subjects = db.relationship('Subjects')
    otp = db.Column(db.String(6))
    name = db.Column(db.String(150),default="")
    verified = db.Column(db.Boolean)
    role = db.Column(db.String(150))
    notes = db.Column(db.String(10000),default="")
    year_group = db.Column(db.Integer,default=0)
    studying_igcse = db.Column(db.String,default="I am not sure of my plans for IGCSE")
    studying_ib = db.Column(db.String,default="I am not sure of my plans for IB")
    # This is the database for the users
class Block(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subjects = db.Column(db.String(10000))
    # This is the database for the blocks