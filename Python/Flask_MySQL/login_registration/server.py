import re
from flask import Flask, request, redirect, render_template, session, flash
from mysqlconnection import MySQLConnector

from flask.ext.bcrypt import Bcrypt
app = Flask(__name__)
app.secret_key = "dubslocker"
bcrypt = Bcrypt(app)
mysql = MySQLConnector(app, 'login')
@app.route("/")
def index():
    if "id" not in session:
        return render_template("index.html")
    else:
        return redirect("/success")
@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/register_validation", methods=["POST"])
def register_validation():
    first = request.form["first_name"]
    last = request.form["last_name"]
    email = request.form["email"]
    password = request.form["password"]
    pw_confirm = request.form["pw_confirm"]
    email_regex= r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    name_regex= r"(^[a-zA-Z]{2,}$)"
    password_regex= r"(^[a-zA-Z0-9_.+-]{8,}$)"
    if re.match(email_regex, email) and re.match(name_regex, first)\
     and re.match(name_regex, last) and re.match(password_regex, password) and password == pw_confirm:
        print "valid"
        pw_hash = bcrypt.generate_password_hash(password)
        query = "INSERT INTO users(first_name, last_name, email, created_at, updated_at, pw_hash)\
        VALUES(:first, :last, :email, NOW(), NOW(),:pw_hash)"
        data = {
        "first": request.form["first_name"],
        "last": request.form["last_name"],
        "email": request.form["email"],
        "pw_hash": pw_hash
        }
        mysql.query_db(query, data)
        flash("Successfully registered, please log in")
        return redirect("/")
    else:
        print "invalid"
        flash ("Invalid submission")
        return redirect("/register")

@app.route("/login_validation", methods=["POST"])
def login():
    query = "SELECT pw_hash, id FROM users WHERE users.email = \"{}\"".format(request.form["username"])
    pw_check= mysql.query_db(query)
    print pw_check
    if bcrypt.check_password_hash(pw_check[0]["pw_hash"], request.form["password"]):
        print "logged in"
        session["id"] = pw_check[0]["id"]
        return redirect("/success")
    else:
        flash("Incorrect login")
        return redirect("/")

@app.route("/success")
def success():
    query = "SELECT * from users where id = {}".format(session["id"])
    result = mysql.query_db(query)
    return render_template("success.html", result = result)

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")






app.run(debug=True)
