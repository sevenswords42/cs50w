import os
import requests

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
#from models import *

app = Flask(__name__)

app.debug = True
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["DATABASE_URL"] = "postgres://eiygclktdujiic:ffcaec2104984ff8ef86538b24fa557cca7b6964868aef6a9575d7cbb7ce9eed@ec2-54-75-244-161.eu-west-1.compute.amazonaws.com:5432/d59l8bg571b5gv"

Session(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def frontpage():
    if session.get("usernames") is None:
        session["usernames"] = []
        return render_template("frontpage.html", message="Please Log In or Register.")
    if session.get("usernames") is not None:
        if session.get("usernames") != []:
            return render_template("homepage.html", usernames=session["usernames"])
    return render_template("frontpage.html", message="Please Log In or Register.")

@app.route("/login")
def login():
    if session.get("usernames") is None:
        session["usernames"] = []
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/loginpage", methods=["POST"])
def loginpage():
    if session.get("usernames") is None:
        session["usernames"] = []
    if request.method == "POST":
        users = db.execute("SELECT * FROM users").fetchall()
        """Search Username in the Database."""
        try:
            username = request.form.get("username")
            password = request.form.get("password")
        except ValueError:
            return render_template("error.html", message="Invalid Username or Password.")

        # Make sure user exists.
        if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).rowcount == 0:
            return render_template("error.html", message="Wrong Username or Password.")

        elif db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username,"password": password}).rowcount == 1:
            # Configure session to use filesystem
            session["usernames"].append(username)
            return render_template("homepage.html", usernames=session["usernames"])
    else:
        if session.get("usernames") is None:
            session["usernames"] = []
            return render_template("login.html")
        else:
            return render_template("homepage.html", usernames=session["usernames"])

@app.route("/registerpage", methods=["POST"])
def registerpage():
    if session.get("usernames") is None:
        session["usernames"] = []
    if request.method == "POST":
        users = db.execute("SELECT * FROM users").fetchall()
        """Search Username in the Database."""
        try:
            username = request.form.get("username")
            password = request.form.get("password")
        except ValueError:
            return render_template("error.html", message="Invalid Username or Password.")

        # Make sure user exists.
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount == 0:
            db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                        {"username": username, "password": password}) # substitute values from input forms into SQL command
            db.commit() # transactions are assumed, so close the transaction finished
            print(f"Registered user {username} successfully.")
            session["usernames"].append(username)
            return render_template("homepage.html", usernames=session["usernames"])

        elif db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).rowcount >= 1:
            # Configure session to use filesystem
            return render_template("register.html", message="Username ist already taken.")

@app.route("/result", methods=["POST"])
def result():
    if session.get("results") is None:
        session["results"] = []
    if request.method == "POST":
        books = db.execute("SELECT * FROM books").fetchall()

        """Search Book in the Database."""
        try:
            isbn = request.form.get("isbn")
            title = request.form.get("title")
            author = request.form.get("author")
            year = request.form.get("year")
        except ValueError:
            return render_template("error.html", message="Invalid Input.")

        # Make sure book exists.
        if db.execute("SELECT * FROM books WHERE isbn = :isbn OR title = :title OR author = :author OR year = :year",\
        {"isbn": isbn, "title": title, "author": author, "year": year}).rowcount == 0:
            return render_template("error.html", message="No book found.")

        else:
            results = db.execute("SELECT * FROM books WHERE isbn = :isbn OR title = :title OR author = :author OR year = :year",\
            {"isbn": isbn, "title": title, "author": author, "year": year}).fetchall()
            # Configure session to use filesystem
            for result in results:
                session["results"].append(result)

            return render_template("homepage.html", usernames=session["usernames"], results = session["results"])

@app.route("/logout")
def logout():
    del session["usernames"]
    return render_template("frontpage.html", message="Logged Out. You can Log In or Register")

@app.route("/index")
def index():
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "VV7lwfoxGUDEu41SlNnJA", "isbns": "9781632168146"})
    return res.json()
