from flask import Flask, render_template, request, redirect
from sqlalchemy import create_engine, text
import random

app = Flask(__name__)
conn_str = "mysql://root:cset155@localhost/bank"
engine = create_engine(conn_str)
conn = engine.connect()

def account_num_rng():
    return str(random.randint(1000000000, 9999999999))

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
        username = request.form["username"]
        password = request.form["password"]
        try:
            login = conn.execute(text("SELECT * FROM users WHERE username = :username AND password = :password"),
                        {"username": username, "password": password}).first()
            if login:
                approved = login[8]
                admin = login[9]
                if admin == "Yes":
                    return redirect('/admin/home')
                elif admin == "No":
                    if approved == "Yes":
                        return redirect(f'/user/home?username={username}')
                    elif approved == "No":
                        message = "Your account has not been approved. Please wait for admin approval."
                    else:
                        message = "ERROR: Login failed."
                else:
                    message = "ERROR: Login failed."
            else:
                message = "ERROR: Incorrect credentials."
        except:
            message = "ERROR: Login function failed."
    return render_template("login.html", message=message)

@app.route("/user/home")
def home_user():
    username = request.args.get("username")
    if not username:
        return redirect("/login")
    try:
        balance = conn.execute(text("SELECT balance FROM users WHERE username = :username"),
                              {"username": username}).first()
        if balance:
            balance = balance[0]
        else:
            balance = 0.00
    except:
        balance = 0.00
    return render_template("user_home.html", username=username, balance=balance)

@app.route("/user/my-account")
def my_account_user():
    username = request.args.get("username")
    if not username:
        return redirect("/login")
    try:
        account = conn.execute(text("SELECT fname, lname, ssn, address, phone, username, account_number, balance FROM users WHERE username = :username"),
                              {"username": username}).first()
        if account:
            account = {
                "fname": account[0],
                "lname": account[1],
                "ssn": account[2],
                "address": account[3],
                "phone": account[4],
                "username": account[5],
                "account_number": account[6],
                "balance": account[7]
            }
        else:
            account = None
    except:
        account = None
    return render_template("user_my_account.html", account=account)

@app.route("/user/add-funds", methods=["GET", "POST"])
def add_funds_user():
    message = None
    if request.method == "GET":
        username = request.args.get("username")
        if not username:
            return redirect("/login")
        return render_template("user_add_funds.html", username=username)
    elif request.method == "POST":
        username = request.form.get("username")
        amount = request.form.get("amount")
        try:
            amount = float(amount)
            if amount <= 0:
                message = "Amount must be greater than 0."
        except:
            message = "ERROR: Invalid amount."
        try:
            conn.execute(text("UPDATE users SET balance = balance + :amount WHERE username = :username"),
                        {"amount": amount, "username": username})
            conn.commit()
            return redirect(f"/user/home?username={username}")
        except:
            message = "ERROR: Funds could not be added."
            return render_template("user_add_funds.html", message=message, username=username)

@app.route("/admin/home", methods = ["GET", "POST"])
def home_admin():
    message = None
    unapproveds = []
    approveds = []
    if request.method == "POST":
        unapproveds = conn.execute(text("SELECT * FROM users WHERE approved = 'No' AND admin != 'Yes'")).all()
        approveds = conn.execute(text("SELECT * FROM users WHERE approved = 'Yes' AND admin != 'Yes'")).all()
        if request.form.get("approve"):
            try:
                user_id = request.form.get("approve")
                account_number = account_num_rng()
                conn.execute(text("UPDATE users SET approved = 'Yes', account_number = :account_number, balance = 0.00 WHERE id = :user_id"),
                            {"user_id": user_id, "account_number": account_number})
                conn.commit()
                message = "User approved successfully."
            except:
                message = "ERROR: User approval failed."
    else:
        unapproveds = conn.execute(text("SELECT * FROM users WHERE approved = 'No' AND admin != 'Yes'")).all()
        approveds = conn.execute(text("SELECT * FROM users WHERE approved = 'Yes' AND admin != 'Yes'")).all()
    return render_template("admin_home.html", message=message, unapproveds=unapproveds, approveds=approveds)

@app.route("/admin/view/<username>")
def account_view_admin(username):
    try:
        account = conn.execute(text("SELECT fname, lname, ssn, address, phone, username, account_number, balance FROM users WHERE username = :username"),
                              {"username": username}).first()
        if account:
            account = {
                "fname": account[0],
                "lname": account[1],
                "ssn": account[2],
                "address": account[3],
                "phone": account[4],
                "username": account[5],
                "account_number": account[6],
                "balance": account[7]
            }
            print(account)
        else:
            account = None
    except:
        account = None
    return render_template("admin_account_view.html", account=account)

if __name__ == "__main__":
    app.run(debug=True)