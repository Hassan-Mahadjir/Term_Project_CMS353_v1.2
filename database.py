from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String,Date,ForeignKey
from datetime import datetime

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


class Admin(db.Model):
    ad_id = db.Column(db.Integer, primary_key=True)
    ad_name = db.Column(db.String(50), nullable=False)
    ad_email = db.Column(db.String(), nullable=False)
    ad_password = db.Column(db.String(), nullable=False)
    instructors = db.relationship('Instructor', backref='Admin')

class Instructor(db.Model):
    inst_id = db.Column(db.Integer, primary_key=True)
    inst_name = db.Column(db.String(50), nullable=False)
    inst_email = db.Column(db.String(), nullable=False)
    inst_password = db.Column(db.String(), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.ad_id'))

    # students = db.relationship('Student', backref='Instructor')
    groups = db.relationship('Group', backref='Instructor')
    announcements = db.relationship('Announcement', backref='Instructor')


class Student(db.Model):
    std_id = db.Column(db.Integer, primary_key=True)
    std_name = db.Column(db.String(50), nullable=False)
    std_email = db.Column(db.String(), nullable=False)
    std_password = db.Column(db.String(), nullable=False)
    # instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.inst_id'))
    teaching=db.relationship('Instructor',secondary=student_instructor, backref='teachers')



class Group(db.Model):
    grp_id = db.Column(db.Integer, primary_key=True)
    grp_name = db.Column(db.String(50), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.inst_id'))
    # groups = db.relationship('Instructor', backref='Group')
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
# admin=Admin(ad_id='1',ad_name='Nour',ad_password='barakat',ad_email='nour@gmail.com')
instructor=Instructor(inst_id=2,inst_name='Nada',inst_password='Kollah',inst_email='nada@gmail.com',admin_id=1)
instructor=Instructor(inst_id=3,inst_name='Alex',inst_password='russian',inst_email='alex@gmail.com',admin_id=1)

student=Student(std_id=1,std_name='Ahmed',std_password='xyz',std_email='ahmed@gmail.com',instructor_id=1)
student2=Student(std_id=2,std_name='hasan',std_password='zyx',std_email='hasan@gmail.com',instructor_id=2)
student3=Student(std_id=3,std_name='nada',std_password='xzy',std_email='n@gmail.com',instructor_id=2)

group=Group(grp_id=1,grp_name='CMSE353',instructor_id=1)
group1=Group(grp_id=2,grp_name='CMSE354',instructor_id=2)
group2=Group(grp_id=3,grp_name='CMSE473',instructor_id=1)

channel=Channel(ch_id=1,ch_name='General',group_id=2)
channel1=Channel(ch_id=2,ch_name='Lab',group_id=2)
channel2=Channel(ch_id=3,ch_name='Tutorial',group_id=1)

announcement= Announcement(ann_id=1,ann_title='Term Project',ann_body='Hello world',instructor_id=1)
announcement1= Announcement(ann_id=2,ann_title='Term Project2',ann_body='Hello ',instructor_id=1)
announcement2= Announcement(ann_id=3,ann_title='Term Project3',ann_body='Hi',instructor_id=2)

student=Student(std_id=4,std_name='Athony',std_password='xxx',std_email='anthony@gmail.com',instructor_id=1)


with app.app_context():
    db.session.add(student)
    student.teaching.append(instructor)
    db.session.commit()