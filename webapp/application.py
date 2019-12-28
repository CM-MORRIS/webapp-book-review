import os

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# for API
import requests
res = requests.get("https://www.goodreads.com/book/review_counts.json", params=
                    {"key": "jRfUDJaEjyhztHw2UghHw", "isbns": "9781632168146"})
print(res.json())


app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/register", methods=["POST"])
def register():

    #take user input and store in database
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if not username or not email or not password:
        return render_template("home.html")

    db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)",
                { "username": username, "email": email, "password": password })
    db.commit()
    return "You have registered!"



@app.route("/login", methods=["POST"])
def login():
    USERNAME = request.form.get("username")
    PASSWORD = request.form.get("password")

    # if user and pass doesn't exist
    if db.execute("SELECT * FROM users WHERE username = :USERNAME AND password = :PASSWORD",
                    {"USERNAME": USERNAME, "PASSWORD": PASSWORD}).rowcount == 0:
        return render_template("error.html", message="Username or Password Incorrect")

    # if does exist
    else:
        return render_template("loggedin.html", message="Successfully Logged In")


@app.route("/loggedin")
def loggedin():
    return render_template("loggedin.html")

@app.route("/error")
def error():
    return render_template("error.html")