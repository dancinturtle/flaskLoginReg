from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
import re
app = Flask(__name__)
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app,'LoginRegistration')
app.secret_key = 'validateEmail'


emailRegex = re.compile(r'^[a-zA-Z0-9\.\+_-]+@[a-zA-Z0-9\._-]+\.[a-zA-Z]*$')
passwordRegex =  re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).+$')

def invalid(email, first_name, lastname, password):
    errors= False
    if len(first_name) < 1 or len(lastname) <1:
        flash("Name too short!")
        errors = True
    if len(email) < 1:
        flash("Email too short!")
        errors = True
    if len(password) < 8:
        print "password 8 letter activated"
        flash ("password needs to be more than 8 characters")
        errors = True
    if request.form['confirm_password'] != request.form['password']:
        print "confirm password flash activated"
        flash("Make sure confirm password is same as password!")
        errors = True
    # Validation
    if not emailRegex.match(request.form['email']):
        print "email flash activated"
        flash("invalid email.")
        errors = True
    if not request.form['first_name'].isalpha():
        print "first name flash activated"
        flash("First Name can only be alphabets")
        errors = True
    if not request.form['lastname'].isalpha():
        print "last name flash activated"
        flash("Last Name can only be alphabets")
        errors = True
    if not passwordRegex.match(request.form['password']):
        print "password flash activated"
        flash("Password must contain atleast one captial letter")
        errors = True
    return errors

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/register', methods=['POST'])
def register():
    first_name = request.form["first_name"]
    lastname = request.form["lastname"]
    email = request.form["email"]
    password = request.form["password"]
    if password:
        pw_hash = bcrypt.generate_password_hash(password)
    else:
        pw_hash = ""
    confirm_password= request.form["confirm_password"]
    errors= False
    # Write query as a string. Notice how we have multiple values
    # we want to insert into our query.
    query = "INSERT INTO users(email, first_name, lastname, pw_hash, created_at, updated_at) VALUES (:email, :first_name, :lastname,:pw_hash, NOW(), NOW())"
    # We'll then create a dictionary of data from the POST data received.
    data = {
             'email': email,
             'first_name': first_name,
             'lastname':  lastname,
             'pw_hash': pw_hash,
             'confirm_password': confirm_password
           }
    errors = invalid(first_name, lastname, email, password)
    if errors:
        return redirect('/')
    if not errors:
        mysql.query_db(query, data)
    return redirect('/success')

@app.route('/login', methods= ['POST'])
def login():
    email = request.form["email"]
    password = request.form["password"]
    query = "SELECT * FROM users"
    user = mysql.query_db(query)
    if bcrypt.check_password_hash(user[0]['pw_hash'], password):
        session['user'] = user[0]['id']
        return redirect('/success')
    else:
        flash("incorrect email or password")
        return redirect('/')


@app.route('/success')
def success():
    return render_template("results.html")

app.run(debug=True) # run our server
