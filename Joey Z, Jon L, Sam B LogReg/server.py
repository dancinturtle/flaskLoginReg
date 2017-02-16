from flask import Flask, session, render_template, request, redirect, flash
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
import re
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app,'login')
app.secret_key = "SuperSecret"

@app.route('/')
def index():
    all_users = mysql.query_db("SELECT * FROM users")
    return render_template("index.html", all_users = all_users)

@app.route('/login', methods=['post'])
def login():
    all_users = mysql.query_db("SELECT * FROM users")
    for i in all_users:
        if i['email'] == request.form['email']:
            print "email match"
            if bcrypt.check_password_hash(i['password'], request.form['password']):
                print "password match"
                session['id'] = i['id']
                return redirect('/success')
    flash("Your user info does not match our database.  Please try again.")
    return redirect('/')

@app.route('/success')
def success():
    if "id" in session:
        return render_template("success.html")
    else:
        flash("Please log in to continue.")
        return redirect('/')

@app.route('/log_out')
def log_out():
    session.pop('id')
    flash("You have now logged out.  Have a great day!")
    return redirect('/')

@app.route('/registration')
def registration():
    return render_template("registration.html")

@app.route("/process", methods=['post'])
def create_user():
   print "created user"
   error = 0

   def hasNumbers(inputString):
      return any(char.isdigit() for char in inputString)
      #The above function is a helper function

   if len(request.form["email"]) == 0:
      flash("Please insert a valid email address.")
      error = 1
   elif not EMAIL_REGEX.match(request.form['email']):
      flash("That email address is invalid.  Please try again.")
      error = 1
   else:
      all_users = mysql.query_db("SELECT * FROM users")
      for i in all_users:
          if i['email'] == request.form['email']:
              flash("That email address is already taken.  Please choose a unique email address.")
              error = 1

   if len(request.form["first_name"]) < 2:
      flash("Please insert your first name.")
      error = 1
   elif hasNumbers(request.form["first_name"]) == True:
      flash("Please remove all numbers from your first name.")
      error = 1

   if len(request.form["last_name"]) < 2:
      flash("Please insert your last name.")
      error = 1
   elif hasNumbers(request.form["last_name"]) == True:
      flash("Please remove all numbers from your last name.")
      error = 1

   if len(request.form["password"]) == 0:
      flash("Please create a password.")
      error = 1
   elif len(request.form["password"]) < 8:
      flash("Please create a password with 8 or more characters.")
      error = 1
   elif (request.form["password"]) != (request.form["confirm"]):
      flash("Please verify that both password fields match.")
      error = 1

   if error == 0:
      insert_query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:first_name, :last_name, :email, :password, NOW(), NOW())"
      data = {
        "first_name":request.form["first_name"],
        "last_name":request.form["last_name"],
        "email":request.form["email"],
        "password":bcrypt.generate_password_hash(request.form["password"])
      }
      mysql.query_db(insert_query, data)
      session['id'] = i['id']
      return redirect("/success")

   print "finished /process"
   return redirect("/registration")

app.run (debug=True)
