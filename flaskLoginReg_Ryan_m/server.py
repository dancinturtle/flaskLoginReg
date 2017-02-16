from flask import Flask, session, render_template, redirect, flash, request
from flask_bcrypt import Bcrypt
from mysqlconnection import MySQLConnector

app = Flask(__name__)
app.secret_key = 'specialpassword'
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app,'login_registration')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users', methods=['POST'])
def create():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    is_valid = True
    if len(first_name) == 0:
        flash('Name cannot be blank', 'registration')
        is_valid = False
    if len(last_name) == 0:
        flash('Name cannot be blank', 'registration')
        is_valid = False
    if len(email) == 0:
        flash('Email cannot be blank', 'registration')
        is_valid = False
    #use regex to confirm the email is valid
    if len(password) < 3:
        flash('password must be at least three characters', 'registration')
        is_valid = False
    if is_valid:
        #save into DB
        hashed_pw = bcrypt.generate_password_hash(password)
        query = 'INSERT INTO login_registration.users (first_name,last_name, email, password, created_at, updated_at) VALUES(:first_name, :last_name, :email, :password, NOW(), NOW());'
        data = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': hashed_pw,
        }
        mysql.query_db(query, data)
        print query, "this works"
        return redirect('/success')
    else:
        #redirect to registration page and show errors
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    query = 'SELECT * FROM users WHERE email = :email;'
    data = {'email': email}

    user = mysql.query_db(query, data)
    #print user[0]['password']
    if bcrypt.check_password_hash(user[0]['password'], password):
        return redirect('/success')
    else:
        flash('invalid credentials.', 'login')
        return redirect('/')

app.run(debug=True)
