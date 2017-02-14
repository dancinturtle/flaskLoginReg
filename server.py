from flask import Flask, request, render_template, flash, redirect, session
from mysqlconnection import MySQLConnector
from flask.ext.bcrypt import Bcrypt
app = Flask(__name__)
bcrypt = Bcrypt(app)
app.secret_key = 'cookiecookiecookie'
mysql = MySQLConnector(app, 'loginReg')

@app.route('/')
def index():
 return render_template('index.html')

# generate_password_hash
@app.route('/create_user', methods=['POST'])
def create_user():
 first_name = request.form['first_name']
 last_name = request.form['last_name']
 email = request.form['email']
 password = request.form['password']
 pw_hash = bcrypt.generate_password_hash(password)
 insert_query = "INSERT INTO users (email, first_name, last_name, pw_hash, created_at) VALUES (:email, :first_name, :last_name, :pw_hash, NOW())"
 query_data = { 'email': email, 'first_name': first_name, 'last_name': last_name, 'pw_hash': pw_hash }
 mysql.query_db(insert_query, query_data)
 session['email'] = request.form['email']
 return redirect("/dashboard")

# login page
@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/pw_check', methods=['POST'])
def logic():
    email = request.form['email']
    password = request.form['password']
    user_query = "SELECT * FROM users WHERE email = :email LIMIT 1"
    query_data = { 'email': email }
    user = mysql.query_db(user_query, query_data) # user will be returned in a list
    if bcrypt.check_password_hash(user[0]['pw_hash'], password):
        session['email'] = request.form['email']
        return redirect('/dashboard')
    else:
        # flash error message and redirect to login page
        flash("Please try again")
        return redirect ('/login')

@app.route('/dashboard')
def dashboard():
    flash ("Let's start a conversation")
    return render_template('dashboard.html')

app.run(debug = True)
