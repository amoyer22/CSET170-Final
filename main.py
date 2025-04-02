from flask import Flask, render_template, request, redirect
from sqlalchemy import create_engine, text

app = Flask(__name__)
conn_str = "mysql://root:cset155@localhost/bank"
engine = create_engine(conn_str)
conn = engine.connect()

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods = ["GET", "POST"])
def signup():
    message = None
    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        ssn = request.form.get("ssn")
        address = request.form.get("address")
        phone = request.form.get("phone")
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            conn.execute(text("INSERT INTO USERS (fname, lname, ssn, address, phone, username, password) VALUES (:fname, :lname, :ssn, :address, :phone, :username, :password)"),
                        {"fname": fname, "lname": lname, "ssn": ssn, "address": address, "phone": phone, "username": username, "password": password})
            conn.commit()
            message = "Sign up successful. Please wait for an admin's approval to log in."
        except:
            message = "ERROR: Sign up failed. Could not create user."
    return render_template("signup.html", message=message)

@app.route("/login", methods = ["GET", "POST"])
def login():
    message = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        try:
            login = conn.execute(text("SELECT * FROM users WHERE username = :username AND password = :password"),
                        {"username": username, "password": password})
            if login:
                return redirect('/home')
            else:
                message = "ERROR: Login failed."
        except:
            message = "ERROR: Login failed."
    return render_template("login.html", message=message)

@app.route("/home")
def user_home():
    message = None
    return render_template("user_home.html", message=message)


if __name__ == "__main__":
    app.run(debug=True)