from flask import Flask, session, render_template, redirect, flash, request
from flask_bcrypt import Bcrypt
from mysqlconnection import MySQLConnector

app = Flask(__name__)
app.secret_key = 'k3y'
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app,'mydb')


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
    if len(first_name)==0:
        flash('Name cannot be blank', 'registration')
        is_valid = False
    if len(last_name)==0:
        flash('Name cannot be blank', 'registration')
        is_valid = False
    if len(email)==0:
        flash('Email cannot be blank', 'registration')
        is_valid = False
    #use regex to confirm the email is valid
    if len(password) < 3:
        flash('Password must be at least three characters','registration')
        is_valid = False
    if is_valid:
        print "hello world"
        #save to db
        hashed_pw = bcrypt.generate_password_hash(password)
        query = 'insert into mydb.users(first_name, last_name, email, password, created_at, updated_at) values(:first_name, :last_name, :email, :password, NOW(), NOW());'
        data = {
        'first_name': first_name,
        'last_name': last_name,
        'email': email,
        'password': hashed_pw
        }
        mysql.query_db(query, data)
        print query, "this works"
        return redirect('/success')
    else:
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    email = request.form['email']
    password = request.form['password']

    query = 'select  * from users where email= :email;'
    data= {'email': email}
    user = mysql.query_db(query, data)
    if bcrypt.check_password_hash(user[0]['password'], password):
        print "YOU ARE LOGGED IN"
        return redirect('/success')
    else:
        flash('invalid credentials.','login')
        return redirect('/')

app.run(debug=True)
