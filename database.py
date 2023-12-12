from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String,Date,ForeignKey
from datetime import datetime
from flask_login import UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///TeamsDataBase.db'

db = SQLAlchemy()
db.init_app(app)

student_instructor=db.Table('student_instructor',db.Column('std_id',db.Integer,db.ForeignKey('student.std_id')),
                         db.Column('inst_id',db.Integer,db.ForeignKey('instructor.inst_id'))
                         )
classes=db.Table('classes',db.Column('grp_id',db.Integer,db.ForeignKey('group.grp_id')),
                         db.Column('std_id',db.Integer,db.ForeignKey('student.std_id'))
                         )
chat=db.Table('chat',db.Column('ann_id',db.Integer,db.ForeignKey('announcement.ann_id')),
                         db.Column('std_id',db.Integer,db.ForeignKey('student.std_id'))
                         )


class Admin(UserMixin, db.Model):
    ad_id = db.Column(db.Integer, primary_key=True)
    ad_name = db.Column(db.String(50), nullable=False)
    ad_email = db.Column(db.String(), nullable=False)
    ad_password = db.Column(db.String(), nullable=False)
    instructors = db.relationship('Instructor', backref='Admin')

    def get_id(self):
           return (self.ad_id)

class Instructor(db.Model):
    inst_id = db.Column(db.Integer, primary_key=True)
    inst_name = db.Column(db.String(50), nullable=False)
    inst_email = db.Column(db.String(), nullable=False)
    inst_password = db.Column(db.String(), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.ad_id'))

    groups = db.relationship('Group', backref='Instructor')
    announcements = db.relationship('Announcement', backref='Instructor')


class Student(db.Model):
    std_id = db.Column(db.Integer, primary_key=True)
    std_name = db.Column(db.String(50), nullable=False)
    std_email = db.Column(db.String(), nullable=False)
    std_password = db.Column(db.String(), nullable=False)
    teaching=db.relationship('Instructor',secondary=student_instructor, backref='teachers')



class Group(db.Model):
    grp_id = db.Column(db.Integer, primary_key=True)
    grp_name = db.Column(db.String(50), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.inst_id'))
    grouping=db.relationship('Student',secondary=classes, backref='groupers')


class Channel(db.Model):
    ch_id = db.Column(db.Integer, primary_key=True)
    ch_name = db.Column(db.String(50), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.grp_id'))

class Announcement(db.Model):
    ann_id = db.Column(db.Integer, primary_key=True)
    ann_title = db.Column(db.String(50), nullable=False)
    ann_body= db.Column(db.String(), nullable=False)
    ann_date=db.Column(db.Date,default=datetime.now().date())
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.inst_id'))
    chatting=db.relationship('Student',secondary=chat, backref='chatters')
    

# with app.app_context():
#      db.create_all()

with app.app_context():
    students = db.session.execute(db.select(Student)).scalars().all()
    instructors = db.session.execute(db.select(Instructor)).scalars().all()


    # db.session.commit()

users= [instructors, students]

for type in users:
    if type == type[0]:
        for user in type:
             print(user)