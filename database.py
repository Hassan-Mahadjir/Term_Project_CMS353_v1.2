from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String,Date,ForeignKey
from datetime import datetime
from flask_login import UserMixin

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SystemDataBase.db'

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
    type=db.Column(db.String(30),default='admin')

    instructors = db.relationship('Instructor', backref='Admin')

    def get_id(self):
           return (self.ad_id)
    
    def __init__(self, user_type, user_object):
        self.user_type = user_type
        self.user_object = user_object

class Instructor(UserMixin, db.Model):
    inst_id = db.Column(db.Integer, primary_key=True)
    inst_name = db.Column(db.String(50), nullable=False)
    inst_email = db.Column(db.String(), nullable=False)
    inst_password = db.Column(db.String(), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.ad_id'))
    type=db.Column(db.String(30),default='instructor')


    def __init__(self, user_type, user_object):
        self.user_type = user_type
        self.user_object = user_object


    groups = db.relationship('Group', backref='Instructor')
    announcements = db.relationship('Announcement', backref='Instructor')

    def get_id(self):
        return (self.inst_id)


class Student(UserMixin, db.Model):
    std_id = db.Column(db.Integer, primary_key=True)
    std_name = db.Column(db.String(50), nullable=False)
    std_email = db.Column(db.String(), nullable=False)
    std_password = db.Column(db.String(), nullable=False)
    type=db.Column(db.String(30),default='student')
    teaching=db.relationship('Instructor',secondary=student_instructor, backref='teachers')


    def __init__(self, user_type, user_object):
        self.user_type = user_type
        self.user_object = user_object
    


    def get_id(self):
        return (self.std_id)



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
    # instructors = db.session.execute(db.select(Instructor)).scalars().all()
    # admin=Admin(ad_id='1',ad_name='Nour',ad_password='barakat',ad_email='nour@gmail.com')
    # instructor=Instructor(inst_id=1,inst_name='Nada',inst_password='Kollah',inst_email='nada@gmail.com',admin_id=1)
    # instructor1=Instructor(inst_id=2,inst_name='Alex',inst_password='russian',inst_email='alex@gmail.com',admin_id=1)
    # instructor2=Instructor(inst_id=3,inst_name='Hadi',inst_password='isik',inst_email='hadi@gmail.com',admin_id=1)

    # student=Student(std_id=1,std_name='Ahmed',std_password='xyz',std_email='ahmed@gmail.com')
    # student2=Student(std_id=2,std_name='Hassan',std_password='zyx',std_email='hassan@gmail.com')
    # student3=Student(std_id=3,std_name='Nada',std_password='xzy',std_email='nada@gmail.com')
    # student4=Student(std_id=5,std_name='Aya',std_password='xzy',std_email='aya@gmail.com')

    # db.session.add_all([admin,instructor,instructor1,instructor2,student,student2,student3,student4])
    # db.session.commit()
    # db.session.commit()