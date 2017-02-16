from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
import re
app = Flask(__name__)
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app,'login_registration')
app.secret_key='ThisisSecretcoy'

@app.route('/')
def index():
    return render_template('/index.html')

@app.route('/process', methods=['POST'])
def process():
    PASS = re.compile(r'^(?=.*?\d)(?=.*?[A-Z])(?=.*?[a-z])[A-Za-z\d]{8,}$')
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    valid = True

    if len(request.form['first_name']) < 2:
        valid = False
        flash("First Name cannot be blank or need to have more than one characters")
    elif not request.form["first_name"].isalpha():
        valid = False
        flash("First name field cannot have a number")
    if len(request.form['last_name']) < 2:
        valid = False
        flash("Last Name cannot be blank or need to have more than one characters")
    elif not request.form["last_name"].isalpha()< 2:
        valid = False
        flash("Last name field cannot have a number")
    if not EMAIL_REGEX.match(request.form['email']):
        valid = False
        flash('invalid email format/cannot be blank')
    if not PASS.match(request.form['password']):
        valid = False
        flash('cannot be blank and password must contain at least 8 characters with 1 uppercase, 1 lowercase, 1 number')
    if request.form['confirm_password'] != request.form['password']:
        valid = False
        flash('password does not match')

    if valid:
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        email = request.form['email']
        password = request.form['password']
        pw_hash = bcrypt.generate_password_hash(password)

        newquery = "INSERT INTO Users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
        data = {
            'first_name': first_name,
            'last_name': last_name,
            'email': email,
            'password': pw_hash
                }

        logged_id = mysql.query_db(newquery,data)
        session['user_id'] = logged_id
        query = "SELECT * FROM Users"
        emails = mysql.query_db(query)
        return render_template('success.html', all_emails=emails)


    return redirect('/')


@app.route('/log_in', methods=['POST'])
def login():
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
    email = request.form['email']
    password = request.form['password']
    user_query = "SELECT * FROM Users WHERE email = :email LIMIT 1"
    query_data = { 'email': email }
    user = mysql.query_db(user_query, query_data) # user will be returned in a list
    if not EMAIL_REGEX.match(email):
        flash('invalid email format/cannot be blank')
        return redirect('/')
    if len(user) > 0:
        if bcrypt.check_password_hash(user[0]['password'], password):
            session['user_id'] = user[0]['id']
            return render_template('/success.html')
    else:
        flash("password email combonation does not match")
        return redirect('/')



@app.route('/log_out')
def logout():
    session.pop('user_id')
    flash('You were logged out')
    return render_template('/index.html')

app.run(debug=True)
