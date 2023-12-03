from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

static = {"firstName": "name",
            "lastName": "lastname",
            "userName": "userName",
            "email": "email@at.com",
            "password": "password",
            "type": "type"
            }

@app.route('/')
def home():
    return render_template("instructor_page.html")

@app.route('/home_student')
def home_student():
    return render_template("student_page.html")

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        result = {"firstName": request.form['firstName'],
                  "lastName": request.form['lastName'],
                  "userName": request.form['userName'],
                  "email": request.form["email"],
                  "password": request.form["password"],
                  "type": request.form['type']}
        print(result)

        return redirect(url_for('home'))

    return render_template('addForm.html')

@app.route('/signin', methods=['POST', 'GET'])
def signin():

    if request.method == "POST":

        result1 = {"email": request.form["email"],
                  "password": request.form['password']}

        if result1["email"] == static["email"] and result1["password"] == static["password"]:
            return redirect(url_for('home_student'))
        else:
            return render_template('signin.html')

    return render_template('signin.html')


@app.route('/group')
def group():
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
