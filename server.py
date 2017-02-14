from flask import Flask, render_template, redirect, request, flash, session
from flask.ext.bcrypt import Bcrypt
from mysqlconnection import MySQLConnector
import re
app = Flask(__name__)
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app,'loginreg')
app.secret_key = "IsItASecretYet"
EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
	if request.form['button'] == "Sign In":
		if len(request.form['first_name']) < 1 or len(request.form['last_name']) < 1:
			flash("Incorrect input")
			return redirect('/')
		else:
			first_name = request.form['first_name']
			last_name = request.form['last_name']
			pw = request.form['pw']
			user_query = "SELECT * FROM users WHERE users.first_name = :first_name"
			query_data = {
				'first_name': first_name,
				'last_name': last_name
			}
			user = mysql.query_db(user_query, query_data)
			if bcrypt.check_password_hash(user[0]['password'], pw):
				return render_template('success.html')
			else:
				flash('Incorrect password')
				return redirect('/')
			return render_template('success.html')
	if request.form['button'] == "Register":
		if len(request.form['firstname']) < 1 or len(request.form['lastname']) < 1:
			flash("Incorrect stuff")
			return render_template('register.html')
		elif request.form['password'] != request.form['confirm']:
			flash("Password and confirmation different")
			return render_template('register.html')
		else:
			firstname = request.form['firstname']
			lastname = request.form['lastname']
			email = request.form['email']
			password = bcrypt.generate_password_hash(request.form['password'])
			data = {
				'firstname': firstname,
				'lastname': lastname,
				'email': email,
				'password': password
			}
			insert_query = "INSERT INTO users (first_name, last_name, email, password, created_at, updated_at) VALUES (:firstname, :lastname, :email, :password, NOW(), NOW())"
			mysql.query_db(insert_query, data)
			return render_template('success.html')

@app.route('/register')
def reg():
	return render_template('register.html')

app.run(debug=True)