from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String,Date,ForeignKey
from datetime import datetime
from flask_login import UserMixin
from Crypto.Cipher import DES
from Crypto.Random import get_random_bytes

def pad_data(data):
    # Pad the data to be a multiple of 8 bytes (DES block size)
    while len(data) % 8 != 0:
        data += b'\x00'
    return data

def generate_key():
    # Generate a random 8-byte key
    return get_random_bytes(8)

def encrypt_string(data, key):
    # Convert string to bytes and pad the data
    data_bytes = data.encode('utf-8')
    padded_data = pad_data(data_bytes)

    # Create a DES cipher object with the key and the ECB mode
    cipher = DES.new(key, DES.MODE_ECB)

    # Encrypt the padded data
    encrypted_data = cipher.encrypt(padded_data)

    return encrypted_data

def decrypt_string(encrypted_data, key):
    # Create a DES cipher object with the key and the ECB mode
    cipher = DES.new(key, DES.MODE_ECB)

    # Decrypt the data
    decrypted_data = cipher.decrypt(encrypted_data)

    # Remove padding and return decrypted bytes
    decrypted_data = decrypted_data.rstrip(b'\x00')

    return decrypted_data

# Example usage:
key = b'\r\x8b\x9e\xb0\x8f\x04S\xff'
# print(f"KEY: {key}")

encrypted_data = encrypt_string('hello, this Hassan, yeahhh', key)
# print("Encrypted data:", encrypted_data)

# decrypted_data = decrypt_string(b'\x1d\xca^\x11\xd8\xaa3\xe6\xcd\x8e\x80ET\xc2\x1e\xfb\xac\x985\xfb\xfbX\xa6\xde\xa4\x87\xa4\xd5\xb3\xe8\xfd\xec', key).decode('utf-8')
# print(decrypted_data)


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SystemDataBase2.db'

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
    ad_name = db.Column(db.String(), nullable=False)
    ad_email = db.Column(db.String(), nullable=False)
    ad_password = db.Column(db.String(), nullable=False)
    type=db.Column(db.String(30),default='admin')

    instructors = db.relationship('Instructor', backref='Admin')

    def get_id(self):
           return (self.ad_id)
    

class Instructor(UserMixin, db.Model):
    inst_id = db.Column(db.Integer, primary_key=True)
    inst_name = db.Column(db.String(), nullable=False)
    inst_email = db.Column(db.String(), nullable=False)
    inst_password = db.Column(db.String(), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('admin.ad_id'))
    type=db.Column(db.String(30),default='instructor')

    groups = db.relationship('Group', backref='Instructor')
    announcements = db.relationship('Announcement', backref='Instructor')

    def get_id(self):
        return (self.inst_id)


class Student(UserMixin, db.Model):
    std_id = db.Column(db.Integer, primary_key=True)
    std_name = db.Column(db.String(), nullable=False)
    std_email = db.Column(db.String(), nullable=False)
    std_password = db.Column(db.String(), nullable=False)
    type=db.Column(db.String(30),default='student')
    teaching=db.relationship('Instructor',secondary=student_instructor, backref='teachers')

    def get_id(self):
        return (self.std_id)



class Group(db.Model):
    grp_id = db.Column(db.Integer, primary_key=True)
    grp_name = db.Column(db.String(), nullable=False)
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.inst_id'))
    grouping=db.relationship('Student',secondary=classes, backref='groupers')


class Channel(db.Model):
    ch_id = db.Column(db.Integer, primary_key=True)
    ch_name = db.Column(db.String(), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.grp_id'))
    announcement = db.relationship('Announcement', backref='Channel')

class Announcement(db.Model):
    ann_id = db.Column(db.Integer, primary_key=True)
    ann_title = db.Column(db.String(), nullable=False)
    ann_body= db.Column(db.String(), nullable=False)
    ann_date=db.Column(db.Date,default=datetime.now().date())
    instructor_id = db.Column(db.Integer, db.ForeignKey('instructor.inst_id'))
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.ch_id'))
    chatting=db.relationship('Student',secondary=chat, backref='chatters')
    

with app.app_context():
     db.create_all()

with app.app_context():
    name = encrypt_string('Ahmed', key)
    password = encrypt_string('xyz', key)
    email = encrypt_string('ahmed@gmail.com',key)

    student=Student(std_id=110,std_name=name,std_password=password,std_email=email)
    db.session.add(student)
    db.session.commit()