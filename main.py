from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from datetime import datetime
# from database import *
from flask_login import login_user, LoginManager, current_user, logout_user, UserMixin
from functools import wraps




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
    ad_name = db.Column(db.String(50), nullable=False)
    ad_email = db.Column(db.String(), nullable=False)
    ad_password = db.Column(db.String(), nullable=False)
    type=db.Column(db.String(30),default='admin')

    instructors = db.relationship('Instructor', backref='Admin')

    def get_id(self):
           return (self.ad_id)
    

class Instructor(UserMixin, db.Model):
    inst_id = db.Column(db.Integer, primary_key=True)
    inst_name = db.Column(db.String(50), nullable=False)
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
    std_name = db.Column(db.String(50), nullable=False)
    std_email = db.Column(db.String(), nullable=False)
    std_password = db.Column(db.String(), nullable=False)
    type=db.Column(db.String(30),default='student')
    teaching=db.relationship('Instructor',secondary=student_instructor, backref='teachers')

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

# Configure Flask-Login
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

@app.route('/home_student')
def home_student():
    return render_template("student_page.html")

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
            student=Student(std_id=id,std_name=name,std_password=password,std_email=email)
            db.session.add(student)
            db.session.commit()
        elif type=='instructor':
            instructor=Instructor(inst_id=id,inst_name=name,inst_password=password,inst_email=email,admin_id=1)
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
        print(user_type)
        if user_type == 'Admin':
            
            admin = db.session.execute(db.select(Admin).where(Admin.ad_id == 1)).scalar()

            if email == admin.ad_email and password == admin.ad_password:

                login_user(admin)

                return redirect(url_for("admin"))
            else:
                return redirect(url_for("signin"))
        elif user_type == 'Instructor':
            instructor = db.session.execute(db.select(Instructor).where(Instructor.inst_email == email)).scalar()

            if email == instructor.inst_email and password == instructor.inst_password:

                login_user(instructor)

                return redirect(url_for('instructor_group'))
            else:
                return redirect(url_for("signin"))
            
        elif user_type == 'Student':
            student = db.session.execute(db.select(Student).where(Student.std_email == email)).scalar()

            if email == student.std_email and password == student.std_password:

                login_user(student)

                return render_template('student_mainpage.html')
            else:
                return redirect(url_for("signin"))
        


    return render_template('signin.html')


@app.route('/logout')
def logout():
    logout_user()
    print("logout done")
    return redirect(url_for('signin'))

@app.route('/admin')
def admin():
    students = db.session.execute(db.select(Student)).scalars().all()
    instructors = db.session.execute(db.select(Instructor)).scalars().all()

    return render_template('admin_page.html', types= [instructors, students])

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
            new_student=Student(std_name=fullname,std_password='xyz',std_email=email)
            db.session.add(new_student)
            db.session.commit()
    
        elif updated_type == 'Instructor' and type == 'student':

            student_data = db.session.execute(db.select(Student).where(Student.std_id == id_)).scalar()
            db.session.delete(student_data)
            db.session.commit()
            new_instructor=Instructor(inst_name=fullname,inst_password='xyz',inst_email=email,admin_id = 1)
            db.session.add(new_instructor)
            db.session.commit()


        return redirect(url_for('admin'))


    return render_template('edituser.html', user = edit_user)

    

@app.route('/group/<group_id>')
def group(group_id):
    channels = db.session.execute(db.select(Channel).where(Channel.group_id == group_id)).scalars().all()
    print(channels)
    return render_template('instructor_group_page.html', channels=channels)

@app.route('/CreateGroup', methods=['POST', 'GET'])
def create_group():
    if request.method == "POST":
        print(current_user)
        group_name = request.form['groupName']
        channle_name= request.form["channleName"].lower()

        group = Group(grp_name=group_name, instructor_id=current_user.inst_id)
        db.session.add(group)
        db.session.commit()
        # channel = Channel(ch_name=channle_name, group_id=group.grp_id)
        
        # db.session.add(channel)

        

        return redirect(url_for('instructor_group'))

    return render_template('create_group_instructor.html')

@app.route('/insturctorMain')
def instructor_group():
    groups = db.session.execute(db.select(Group).where(Group.instructor_id == current_user.inst_id)).scalars().all()
    return render_template('instructor_page.html',groups = groups)

@app.route('/insturctorMain')
def load_annoucement():
    return redirect(url_for('instructor_group'))

if __name__ == '__main__':
    app.run(debug=True)


