from flask import Flask, request, redirect, render_template, flash, session
from mysqlconnection import MySQLConnector
from flask_bcrypt import Bcrypt
import re

app = Flask(__name__)
app.secret_key= "heythere"
mysql = MySQLConnector(app,'login')
bcrypt = Bcrypt(app)
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
PW_REGEX = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$')

@app.route('/')
def index():
    query = "SELECT * FROM users"
    users = mysql.query_db(query)
    return render_template('index.html', users=users)

@app.route('/success')
def success():
    query = "SELECT * FROM users WHERE id = :specific_id;"
    data = {'specific_id': session['userid']}
    users = mysql.query_db(query, data)
    return render_template('success.html', users=users[0])

@app.route('/users', methods=['POST'])
def create_user():
    first_name= request.form['first_name']
    last_name= request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    status = True
    if not re.search(r'^[a-zA-Z]+$', last_name):
        flash('Last name must only have letters!')
        status = False
    if not re.search(r'^[a-zA-Z]+$', first_name):
        flash('First name must only have letters!')
        status = False
    if len(request.form['email']) < 1:
            flash("Email cannot be blank!")
            status = False
    if not EMAIL_REGEX.match(request.form['email']):
            flash("Invalid Email Address!")
            status = False
    if len(request.form['first_name']) < 3:
             flash("First Name cannot be empty and must be more than 2 letters!")
             status = False
    if len(request.form['last_name']) < 3:
             flash("Last Name cannot be empty and must be more than 2 letters!")
             status = False
    if len(request.form['password']) < 1:
            flash("Password cannot be blank!")
            status = False
    if len(request.form['password']) < 9:
            flash("Password should be more than 8 characters")
            status = False
    if not PW_REGEX.match(request.form['password']):
            flash("Invalid Password! Must have 1 uppercase letter and 1 number.")
            status = False
    if len(request.form['confirm']) < 1:
            flash("Confirm Password cannot be blank!")
            status = False
    if request.form['confirm'] != request.form['password']:
            flash("Password does not match confirm password")
            status = False
    if status == True:
            pw_hash = bcrypt.generate_password_hash(password)
            insert_query = "INSERT INTO users (email, first_name, last_name, password, created_at) VALUES (:email, :first_name, :last_name, :password, NOW())"
            query_data = { 'email': email, 'first_name': first_name, 'last_name': last_name, 'password': pw_hash }
            mysql.query_db(insert_query, query_data)
            user_query = "SELECT * FROM users WHERE email = :email LIMIT 1"
            query_data = { 'email': email }
            user = mysql.query_db(user_query, query_data)
            session['userid'] = user[0]['id']
            return redirect('/success')
    else:
        return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    status = True
    if len(request.form['email']) < 1:
            flash("Email cannot be blank!")
            status = False
    if len(request.form['password']) < 1:
            flash("Password cannot be blank!")
            status = False
    if status == True:
         email = request.form['email']
         password = request.form['password']
         user_query = "SELECT * FROM users WHERE email = :email LIMIT 1"
         query_data = { 'email': email }
         user = mysql.query_db(user_query, query_data)
         if len(user) == 0:
             flash('You have not registered.')
             return redirect('/')
         if bcrypt.check_password_hash(user[0]['password'], password):
             session['userid'] = user[0]['id']
             return redirect('/success')
         else:
             flash('Your password is wrong.')
             return redirect('/')
    else:
        return redirect('/')

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('userid')
    return redirect('/')


@app.route('/users/<id>/delete', methods=['POST'])
def destroy(id):
    email_id = request.form['delete']
    query = "DELETE FROM users WHERE id = :id; ALTER TABLE users AUTO_INCREMENT = 1;"
    data = {'id': id}
    mysql.query_db(query, data)
    return redirect('/')

app.run(debug=True)
