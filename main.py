from flask import Flask, render_template, request, redirect, url_for, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, Integer, String
from database import *
from flask_login import login_user, LoginManager, current_user, logout_user
from functools import wraps
import random




app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///SystemDataBase.db'
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'

db = SQLAlchemy()
db.init_app(app)

# Configure Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):

    student = db.session.query(Student).get(user_id)
    if student:
        return Student(user_type='student', user_object=student)
    
    instructor = db.session.query(Instructor).get(user_id)
    if instructor:
        return Instructor(user_type='instructor', user_object=instructor)
    
    admin = db.session.query(Admin).get(user_id)
    if admin:
        return Admin(user_type='admin', user_object=admin)
    
    return None



with app.app_context():
    db.create_all()


def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.ad_id != 1:
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function

def instructor_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # If id is not 1 then return abort with 403 error
        if current_user.user_type == 'instructor':
            return abort(403)
        # Otherwise continue with the route function
        return f(*args, **kwargs)

    return decorated_function

@app.route('/')
def home():
    return redirect(url_for('signin'))

@app.route('/home_student')
def home_student():
    return render_template("student_page.html")

@app.route('/home_instructor')
def home_instructor():
    groups = db.session.execute(db.select(Group)).scalars().all()
    return render_template("instructor_page.html", type= [groups])

@app.route('/register', methods=['POST', 'GET'])
@admin_only
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

                return redirect(url_for("home_instructor"))
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


@app.route('/create_group', methods=['POST', 'GET']) 
@instructor_only
def create_group():
      if request.method == "POST":
        groupname= request.form['groupname']
        addchannel= request.form['addchannel']
        gen_grp_id= random.randint(1,100000)
        group=Group(grp_id=gen_grp_id,grp_name=groupname,instructor_id=1)
        db.session.add(group)
        db.session.commit()
        general=Channel(ch_id=random.randint(1,100000),ch_name="General",group_id=gen_grp_id)
        channel=Channel(ch_id=random.randint(1,100000),ch_name=addchannel,group_id=gen_grp_id)
        db.session.add(general)
        db.session.add(channel)
        db.session.commit()
        return redirect(url_for('home_instructor'))
      return render_template('create_group_instructor.html')


@app.route('/group_instructor/<name>', methods=['POST', 'GET'])
@instructor_only
def group_instructor(name):
    groups = db.session.execute(db.select(Group)).scalars().all()
    channels = db.session.execute(db.select(Channel)).scalars().all()

    for group in groups:
        if name==group.grp_name:
            grp1_id=group.grp_id

    if request.method == "POST":
        print("hello")
        channel_name= request.form['add_channel']
        add_channel=Channel(ch_id=random.randint(1,100000),ch_name=channel_name,group_id=grp1_id)
        db.session.add(add_channel)
        db.session.commit()
        return redirect(request.url)

    return render_template('instructor_group_page.html', group_name=name, group_id=grp1_id, type= [channels])

@app.route('/add_student', methods=['POST', 'GET'])
@instructor_only
def add_student():
    students = db.session.execute(db.select(Student)).scalars().all()
    return render_template('add_student_instructor.html', type=[students])


if __name__ == '__main__':
    app.run(debug=True)


