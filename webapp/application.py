import os

from flask import Flask, session, render_template, request, redirect, escape, url_for
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
    if 'username' in session:
        return redirect(url_for('search_page'))
    return render_template("home.html", message="You are not logged in")


@app.route("/register", methods=["POST"])
def register():

    #take user input and store in database
    username = request.form.get("username")
    email = request.form.get("email")
    password = request.form.get("password")

    if not username or not email or not password:
        return redirect(url_for('index'))

    db.execute("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)",
                { "username": username, "email": email, "password": password })
    db.commit()
    return "You have registered!"



@app.route("/login", methods=['POST', 'GET'])
def login():

    if request.method == 'POST':
        USERNAME = request.form.get("username")
        PASSWORD = request.form.get("password")

        # if user and pass doesn't exist
        if db.execute("SELECT * FROM users WHERE username = :USERNAME AND password = :PASSWORD",
            {"USERNAME": USERNAME, "PASSWORD": PASSWORD}).rowcount == 0:

            return redirect(url_for('error'))

        # if user and pass does exist
        session['username'] = USERNAME
        return redirect(url_for('search_page'))

    # if GET
    return redirect(url_for('index'))


@app.route("/search_page")
def search_page():
    return render_template("search_page.html", message=" %s Successfully Logged In" % session['username'])


@app.route("/logout", methods=['POST', 'GET'])
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route("/error")
def error():
    return render_template("error.html", message="Username or Password Incorrect")


@app.route("/search_results", methods=['POST', 'GET'])
def search_results():

    input = request.form.get("book_search")

    if input:
        query = "%" + request.form.get("book_search") + "%"

        rows = db.execute("SELECT isbn, title, author, year FROM books WHERE \
                            isbn ILIKE :query OR \
                            title ILIKE :query OR \
                            author ILIKE :query LIMIT 30",
                            {"query": query})
    else:
        return render_template("search_results.html", message="No Books Found")


    # if no search results found
    if not rows:
        print("no books found")
        return render_template("search_results.html", message="No Books Found")

    # show results
    print("books found")
    return render_template("search_results.html", books=rows)
