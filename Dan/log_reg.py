from flask import Flask, render_template, request, redirect, session, flash, url_for
import re
import os
from mysqlconnection import MySQLConnector
from flask_bcrypt import Bcrypt

NAME_REGEX = re.compile(r'^[a-zA-Z]*$')
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
PASSWORD_REGEX = re.compile(r'^[a-zA-Z0-9]{8,}$')

app = Flask(__name__)
mysql = MySQLConnector(app, 'authentication_db')
bcrypt = Bcrypt(app)
# app.secret_key = "Setting-it-randomly-at-the-bottom"

def validate():
    errors = 0

    # Store form input values in respective variables below
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # Check for first_name
    if len(first_name) < 1:
        flash("First name cannot be blank!")
        errors += 1
    elif not NAME_REGEX.match(first_name) and len(first_name) < 2:
        flash("First name should be letters, provide atleast 2!")
        errors += 1
    else:
        session['first_name'] = first_name

    # Check for last_name
    if len(last_name) < 1:
        flash("Last name cannot be blank!")
        errors += 1
    elif not NAME_REGEX.match(last_name) and len(last_name) < 2:
        flash("Last name should be letters, provide atleast 2!")
        errors += 1
    else:
        session['last_name'] = last_name

    # Check for email
    if len(email) < 1:
        flash("Email cannot be blank!")
        errors += 1
    elif not EMAIL_REGEX.match(email):
        flash("Invalid email. Please provide correct email!")
        errors += 1
    else:
        session['email'] = email

    # Check for password
    if len(password) < 1:
        flash("Password cannot be blank!")
        errors += 1
    elif not PASSWORD_REGEX.match(password):
        flash("Please provide a strong password, atleast 8!")
        errors += 1
    else:
        session['password'] = password

    # Confirm password
    if len(confirm_password) < 1:
        flash("Password cannot be blank!")
        errors += 1
    elif not PASSWORD_REGEX.match(confirm_password) and (password != confirm_password):
        flash("Confirm password should match original password")
        errors += 1
    else:
        session['password'] = confirm_password

     #Check for errors
    if errors > 0:
        session['password'] = ''
        session['confirmPassword'] = ''
        return False
    else:
        return True

def create_user_in_db():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    email = request.form['email']
    password = request.form['password']

    # run validations and if they are successful we can create the password hash with bcrypt
    pw_hash = bcrypt.generate_password_hash(password)
    # now we insert the new user into the database
    insert_query = "INSERT INTO users(first_name, last_name, email, pw_hash, created_at, updated_at)\
    VALUES (:first_name, :last_name, :email, :pw_hash, NOW(), NOW())"
    query_data = { 'first_name': first_name, 'last_name': last_name, 'email': email, 'pw_hash': pw_hash }
    mysql.query_db(insert_query, query_data)
    # redirect to success page

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template("register.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    # if form.validate_on_submit():
    # if request.form[""] == "POST":
        if validate() == False:
            return redirect("/")
        else:
            flash('Thanks for registration ')
            create_user_in_db()
        return redirect('/success')

@app.route('/success')
def success():
    print "Successfully Registerd!! Now log in"
    return render_template('login.html')

@app.route('/login', methods=["GET",'POST'])
def login():
    email = request.form['email']
    password = request.form['password']
    user_query = "SELECT * FROM users WHERE email = :email LIMIT 1"
    query_data = { 'email': email }
    user = mysql.query_db(user_query, query_data) # user will be returned in a list
    if bcrypt.check_password_hash(user[0]['pw_hash'], password):
        session['logged_in'] = True
        # login user
        print "Success!! To the wall!!"
        return redirect('/wall')
    else:
        # set flash error message and redirect to login page
        flash("Incorrect username and password")
        return redirect("/login")

@app.route('/wall', methods=['GET','POST'])
def show():
    return "YOU'VE SUCCESSFULLY SIGNED IN! WELCOME TO THE WALL!"


if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run(debug=True)
