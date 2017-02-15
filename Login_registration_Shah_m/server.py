from flask import Flask, session, render_template, redirect, flash, request
from flask_bcrypt import Bcrypt
from mysqlconnection import MySQLConnector

app = Flask(__name__)
app.secret_key = 'specialpassword'
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app, 'logreg')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/users', methods=['POST'])
def create():
    name = request.form['name']
    email = request.form['email']
    password = request.form['password']
    is_valid = True
    if len(name) == 0:
        flash('Name cannot be blank','registration')
        is_valid = False
    if len(email) == 0:
        flash('Email cannot be blank','registration')
        is_valid = False
    #use regex to confirm the emails is valid
    if len(password) > 16:
        flash('Password must be at least three characters','registration')
        is_valid = False

    if is_valid:
        #save into DB
        hashed_pw = bcrypt.generate_password_hash(password)
        query = 'INSERT INTO users (name, email, password, created_at, updated_at) VALUES(:name, :email, :password, NOW(), NOW());'
        data = {
          'name': name,
          'email': email,
          'password': hashed_pw,
        }
        mysql.query_db(query, data)
        return redirect('/success')
    else:
        #redirect to registration page show errors
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    query = 'SELECT * FROM users WHERE email = :email;'
    data = {'email': email}

    user = mysql.query_db(query, data)
    #print user[0] ['password']
    if user and bcrypt.check_password_hash(user[0]['password'], password):
        return redirect('/succes')
    else:
      flash('Invalid credentials.' 'login')
      return redirect('/')

app.run(debug=True)
