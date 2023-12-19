from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from datetime import datetime
from flask_login import login_user, LoginManager, current_user, logout_user, UserMixin
from functools import wraps

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

    return decrypted_data.decode('utf-8')

with open('old_key.txt','rb') as file:
    key = file.read()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SystemDataBase.db'
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

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

# updating Data Base
def update_entries_with_new_key(new_key):
    # Update entries in the Admin table
    admins = Admin.query.all()
    for admin in admins:
        admin.ad_password = encrypt_string(decrypt_string(admin.ad_password, key), new_key)
        admin.ad_name = encrypt_string(decrypt_string(admin.ad_name, key), new_key)
        admin.ad_email = encrypt_string(decrypt_string(admin.ad_email, key), new_key)

    # Update entries in the Instructor table
    instructors = Instructor.query.all()
    for instructor in instructors:
        instructor.inst_password = encrypt_string(decrypt_string(instructor.inst_password, key), new_key)
        instructor.inst_email = encrypt_string(decrypt_string(instructor.inst_email, key), new_key)
        instructor.inst_name = encrypt_string(decrypt_string(instructor.inst_name, key), new_key)

    # Update entries in the Student table
    students = Student.query.all()
    for student in students:
        student.std_password = encrypt_string(decrypt_string(student.std_password, key), new_key)
        student.std_name = encrypt_string(decrypt_string(student.std_name, key), new_key)
        student.std_email = encrypt_string(decrypt_string(student.std_email, key), new_key)

    # Update entries in the Announcement table
    announcements = Announcement.query.all()
    for announcement in announcements:
        announcement.ann_title = encrypt_string(decrypt_string(announcement.ann_title, key), new_key)
        announcement.ann_body = encrypt_string(decrypt_string(announcement.ann_body, key), new_key)

    # Update entries in the Group table
    groups = Group.query.all()
    for group in groups:
        group.grp_name = encrypt_string(decrypt_string(group.grp_name, key), new_key)

    # Update entries in the Channel table
    channels = Channel.query.all()
    for channel in channels:
        channel.ch_name = encrypt_string(decrypt_string(channel.ch_name, key), new_key)

    # Commit the changes to the database
    db.session.commit()
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    # Try to load user from each class
    user = Admin.query.get(user_id)
    if user is None:
        user = Instructor.query.get(user_id)
        if user is None:
            
            user = Student.query.get(user_id)
            print('Student singed in')
    
    return user



with app.app_context():
    db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Check if the current user is an admin
        if not current_user.is_authenticated or current_user.user_type != 'admin':
            abort(403)  # Return a 403 Forbidden response if not an admin

        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function

@app.route('/')
def home():
    return redirect(url_for('signin'))


@admin_only
@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        name=request.form['firstName']+" "+request.form['lastName']
        id=int(request.form["id"])
        email= request.form["email"].lower()
        password= request.form["password"]
        type=request.form['type'].lower()
        if type== 'student':
            student=Student(std_id=id,std_name= encrypt_string(name,key),std_password=encrypt_string(password,key),std_email=encrypt_string(email,key))
            db.session.add(student)
            db.session.commit()
        elif type=='instructor':
            instructor=Instructor(inst_id=id,inst_name=encrypt_string(name,key),inst_password=encrypt_string(password,key),inst_email=encrypt_string(email,key),admin_id=1)
            db.session.add(instructor)
            db.session.commit()
        else:
            print("Invalid user type")
        return redirect(url_for('admin'))

    return render_template('addForm.html')




@app.route('/signin', methods=['POST', 'GET'])
def signin():

    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        user_type = request.form['user_type']
        # print(user_type)
        if user_type == 'Admin':
            
            admin = db.session.execute(db.select(Admin).where(Admin.ad_id == 1)).scalar()

            if email == decrypt_string(admin.ad_email,key) and password == decrypt_string(admin.ad_password,key):

                login_user(admin)

                return redirect(url_for("admin"))
            else:
                return redirect(url_for("signin"))
        elif user_type == 'Instructor':
            instructor = db.session.execute(db.select(Instructor).where(Instructor.inst_email == encrypt_string(email,key) )).scalar()
            if email == decrypt_string(instructor.inst_email,key) and password == decrypt_string(instructor.inst_password,key):

                login_user(instructor)

                return redirect(url_for('instructor_group'))
            else:
                return redirect(url_for("signin"))
            
        elif user_type == 'Student':
            student = db.session.execute(db.select(Student).where(Student.std_email == encrypt_string(email,key))).scalar()

            if email == decrypt_string(student.std_email,key) and password == decrypt_string(student.std_password,key):

                login_user(student)

                return redirect(url_for('home_student'))
            else:
                return redirect(url_for("signin"))
        


    return render_template('signin.html')


@app.route('/logout')
def logout():
    logout_user()
    print("logout done")
    return redirect(url_for('signin'))

app.jinja_env.filters['decrypt'] = decrypt_string

@app.route('/admin')
def admin():
    students = db.session.execute(db.select(Student)).scalars().all()
    instructors = db.session.execute(db.select(Instructor)).scalars().all()

    return render_template('admin_page.html', types= [instructors, students], key=key)

@admin_only
@app.route('/edit/<type>/<int:id>/<name>/<email>', methods=['POST', 'GET'])
def edit(type,id,name,email):

    edit_user = {
        'name':name,
        'id':id,
        'email':email,
    }

    if request.method == "POST":
        email = request.form['email']
        id_ = request.form['id']
        fullname=request.form['fullName']
        updated_type=request.form['type']

        if updated_type == 'Student' and type == 'instructor':
            instructor_data = db.session.execute(db.select(Instructor).where(Instructor.inst_id == id_)).scalar()
            db.session.delete(instructor_data)
            db.session.commit()
            new_student=Student(std_name=encrypt_string(fullname,key),std_password=encrypt_string('xyz',key),std_email=encrypt_string(email,key))
            db.session.add(new_student)
            db.session.commit()
    
        elif updated_type == 'Instructor' and type == 'student':

            student_data = db.session.execute(db.select(Student).where(Student.std_id == id_)).scalar()
            db.session.delete(student_data)
            db.session.commit()
            new_instructor=Instructor(inst_name=encrypt_string(fullname,key),inst_password=encrypt_string('xyz',key),inst_email=encrypt_string(email,key),admin_id = 1)
            db.session.add(new_instructor)
            db.session.commit()


        return redirect(url_for('admin'))


    return render_template('edituser.html', user = edit_user)

    

@app.route('/group/<group_id>')
def group(group_id):
    channels = db.session.execute(db.select(Channel).where(Channel.group_id == group_id)).scalars().all()
    return render_template('instructor_group_page.html', channels=channels, group_id = group_id, key=key)

@app.route('/CreateGroup', methods=['POST', 'GET'])
def create_group():
    if request.method == "POST":
        try:
            with app.app_context():
                group_name = request.form['groupName']
                channle_name = request.form["channleName"].lower()

                group = Group(grp_name=encrypt_string(group_name,key) , instructor_id=current_user.inst_id)

                db.session.add(group)
                db.session.commit()

                channle = Channel(ch_name=encrypt_string(channle_name,key), group_id = group.grp_id)
                db.session.add(channle)
                db.session.commit()

                return redirect(url_for('instructor_group'))

        except Exception as e:
            # Handle exceptions appropriately
            print(f"Error: {str(e)}")
            db.session.rollback()

    return render_template('create_group_instructor.html')

@app.route('/insturctorMain')
def instructor_group():
    groups = db.session.execute(db.select(Group).where(Group.instructor_id == current_user.inst_id)).scalars().all()
    return render_template('instructor_page.html',groups = groups,key=key)

@app.route('/annoucemnts/<ch_id><g_id>',methods=['POST','GET'])
def annoucemnts(ch_id,g_id):

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        announcement = Announcement(ann_body=encrypt_string(body,key), ann_title= encrypt_string(title,key), instructor_id=current_user.inst_id, channel_id=ch_id)
        db.session.add(announcement)
        db.session.commit()
    announcements = db.session.execute(db.select(Announcement).where(Announcement.channel_id == ch_id)).scalars().all()
    channels = db.session.execute(db.select(Channel).where(Channel.group_id == g_id)).scalars().all()
    return render_template('instructor_group_page.html', channels=channels, announcements = announcements, key=key)

@app.route('/addChannel/<id>', methods = ['POST','GET'])
def addChannle(id):
    if request.method == 'POST':
        channle_name = request.form['channleName']
        channle = Channel(ch_name=encrypt_string(channle_name,key), group_id = id)
        db.session.add(channle)
        db.session.commit()

        return redirect(url_for('instructor_group'))

    return render_template('add_channel.html')


@app.route('/addStudent/<group_id>', methods = ['POST','GET'])
def add_student(group_id):
    if request.method == 'POST':
        student_id = int(request.form['search'])
        student = db.session.execute(db.select(Student).where(Student.std_id == student_id)).scalar()
        group = db.session.execute(db.select(Group).where(Group.grp_id == group_id)).scalar()

        student.teaching.append(current_user)
        group.grouping.append(student)
        db.session.commit()
        return redirect(url_for('instructor_group'))
    teaching_students  = db.session.execute(db.select(Instructor).where(Instructor.inst_id == current_user.inst_id)).scalar()
    group = db.session.execute(db.select(Group).where(Group.grp_id == group_id)).scalar()
    students_in_group = teaching_students.teachers
    grouping = group.grouping
    list_of_student_in_group = [student_id.std_id for student_id in grouping]
    print(list_of_student_in_group)
    classes =[]
    for student in students_in_group:
        if student.std_id in list_of_student_in_group:
            classes.append(student)
    return render_template('add_student_instructor.html',students_in_group = classes, key=key)

@app.route('/home_student', methods = ['POST','GET'])
def home_student():
    student  = db.session.execute(db.select(Student).where(Student.std_id == current_user.std_id)).scalar()
    student_groups = student.groupers
    return render_template('student_mainpage.html', student_groups = student_groups, key=key)

@app.route('/StudentGroup/<group_id>')
def studentGroup(group_id):
    channels = db.session.execute(db.select(Channel).where(Channel.group_id == group_id)).scalars().all()
    return render_template('group_page.html', channels = channels, key=key)

@app.route('/StudentAnnouncements/<group_id><ch_id>',methods=['POST','GET'])
def studentAnnouncements(group_id, ch_id):

    if request.method == 'POST':
        title = request.form['title']
        body = request.form['body']
        group = db.session.execute(db.select(Group).where(Group.grp_id == group_id)).scalar()
        announcement = Announcement(ann_body=encrypt_string(body,key), ann_title= encrypt_string(title,key), instructor_id=group.instructor_id, channel_id=ch_id)
        student = db.session.execute(db.select(Student).where(Student.std_id == current_user.std_id)).scalar()
        db.session.add(announcement)
        announcement.chatting.append(student)
        db.session.commit()
        
    announcements = db.session.execute(db.select(Announcement).where(Announcement.channel_id == ch_id)).scalars().all()
    channels = db.session.execute(db.select(Channel).where(Channel.group_id == group_id)).scalars().all()
    return render_template('group_page.html', channels = channels, announcements = announcements, key=key)
if __name__ == '__main__':
    today = datetime.now().weekday()
    if today == 0:
        with app.app_context():
            new_key = generate_key()
            with open('old_key.txt','wb') as file:
                file.write(new_key)
            update_entries_with_new_key(new_key)

            
    app.run(debug=True)


