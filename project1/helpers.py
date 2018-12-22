"""Helpers"""
import csv
import os
import urllib.request

from flask import redirect, render_template, request, session
from functools import wraps
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
if not os.getenv("GOODREADS_API_KEY"):
    raise RuntimeError("GOODREADS_API_KEY is not set")

GOODREADS_API_KEY = os.getenv("GOODREADS_API_KEY")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

def login_required(f):
    """
    Decorate routes to require login
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

def fetch_books(search_param):
    """
    Fetch books from Database
    Args:
        search_param(str): search parameter
    Returns:
        book
    """

    query = """
        SELECT
            isbn,
            title,
            author,
            year,
            id
        FROM books
        WHERE
            lower(isbn) like lower('%{search_param}%')
            or lower(title) like lower('%{search_param}%')
            or lower(author) like lower('%{search_param}%')
        """.format(
            search_param=search_param
        )

    rows = db.execute(query)

    return rows.fetchall(), rows.keys()
