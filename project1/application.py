import os

import requests

from flask import Flask, flash, redirect, render_template, request, session, jsonify
from flask_session import Session
from tempfile import mkdtemp
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash

from bs4 import BeautifulSoup

from helpers import login_required, apology

app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
if not os.getenv("GOODREADS_API_KEY"):
    raise RuntimeError("GOODREADS_API_KEY is not set")

GOODREADS_API_KEY = os.getenv("GOODREADS_API_KEY")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/")
@login_required
def index():
    return "Project 1: TODO"

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # forget any previous user_id
    session.clear()

    # user reached route via POST (submitting form via post)
    if request.method == "POST":

        # check username submitted
        if not request.form.get("username"):
            return redirect("/login")

        # check password was submitted
        if not request.form.get("password"):
            return redirect("/login")

        # query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          {"username":request.form.get("username")}).fetchall()

        # ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get('password')):
            return redirect("/login")

        # remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # redirect user to home page
        return redirect("/")

    # user reached route via GET
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # clear session just incase
    session.clear()

    # handle get get requests
    if request.method == 'GET':
        # send to registration page
        return render_template("register.html")

    # handle post requests
    elif request.method == 'POST':

        # return attributes of post method
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # get all users
        all_users_query = """SELECT username FROM users"""

        all_users_rows = db.execute(all_users_query)

        # use list comprehension to get actual usernames
        all_users = [i['username'] for i in all_users_rows]

        # check if username is blank
        if username.strip() == '':
            return apology("Bad Username")

        # check if username already exists
        elif username in all_users:
            return apology("Bad Username")

        # check if password is blank
        elif password.strip() == '':
            return apology("Bad Password")

        # check for password/confirmation mismatch
        elif password != confirmation:
            return apology("Bad Password")

        # else register a new account
        else:
            # generate password hash
            password_hash = generate_password_hash(password)
            insert_user_query = (
                "INSERT INTO users (username, hash) "
                "VALUES "
                "(:username, :password_hash)"
            )

            params = {
                'username': username,
                'password_hash': password_hash
            }

            db.execute(
                insert_user_query,
                params
            )

            db.commit()

            # Query database for username
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                              {"username":username}).fetchall()

            # Ensure username exists and password is correct
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
                return apology("invalid username and/or password", 403)

            # Remember which user has logged in
            session["user_id"] = rows[0]["id"]
            return redirect("/")

    return apology("Unable to Register")

@app.route("/api/<isbn>", methods=["GET"])
# @login_required
def api_isbn(isbn):
    try:
        res = requests.get(
            "https://www.goodreads.com/search/index.xml",
            params={
                "key": GOODREADS_API_KEY,
                "q": str(isbn)
            }
        )
        # turn response in beautiful soup object for xml parsing
        soup = BeautifulSoup(res.content)

        # parse xml for required elements
        title = soup.find('title').string
        author = soup.author.find('name').string
        year = soup.find('original_publication_year').string
        reviews_count = soup.find('text_reviews_count').string
        average_rating = soup.find('average_rating').string

        # json_dict
        json_dict = {
            'title': title,
            'author': author,
            'year': year,
            'isbn': isbn,
            'review_count': reviews_count,
            'average_rating': average_rating
        }
        if res.status_code == 200:
            return jsonify(json_dict)
        else:
            return apology("No results returned for ISBN {}".format(isbn))
    except:
        return apology("No results returned for ISBN {}".format(isbn))
