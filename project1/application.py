import os
import requests

from flask import Flask, session, render_template, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

app.config["DATABASE_URL"] = "postgres://eiygclktdujiic:ffcaec2104984ff8ef86538b24fa557cca7b6964868aef6a9575d7cbb7ce9eed@ec2-54-75-244-161.eu-west-1.compute.amazonaws.com:5432/d59l8bg571b5gv"

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
def frontpage():
    return render_template("frontpage.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

@app.route("/loginpage", methods=["POST"])
def loginpage():
    users = db.execute("SELECT * FROM users").fetchall()

    """Search Username in the Database."""
    try:
        username = request.form.get("username")
        password = request.form.get("password")
    except ValueError:
        return render_template("error.html", message="Invalid Username or Password.")

    # Make sure flight exists.
    if db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username, "password": password}).rowcount == 0:
        return render_template("error.html", message="Wrong Username or Password.")

    elif db.execute("SELECT * FROM users WHERE username = :username AND password = :password", {"username": username,"password": password}).rowcount == 1:
        return render_template("homepage.html", username=username)

@app.route("/index")
def index():
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "VV7lwfoxGUDEu41SlNnJA", "isbns": "9781632168146"})
    return res.json()
