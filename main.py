from flask import Flask, render_template, request
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
            message = "Sign up successful."
        except:
            message = "ERROR: Sign up failed. Could not create user."
    return render_template("signup.html", message=message)

@app.route("/login")
def login():
    message = None
    return render_template("login.html", message=message)

if __name__ == "__main__":
    app.run(debug=True)