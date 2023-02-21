import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


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
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def getQuote(quote):
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }

def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return getQuote(quote)
    except (KeyError, TypeError, ValueError):
        return None


def lookups(symbolsList):

    print(f"symbolsList:    {symbolsList}")
    if len(symbolsList) == 0:
        return {}

    s = ""
    for i in range(len(symbolsList)-1):
        s = s + symbolsList[i] + ","

    s = s + symbolsList[len(symbolsList)-1]

    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://cloud.iexapis.com/v1/stock/market/batch?&types=quote&symbols={s}&token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        symbolsQuotes = response.json()
        quotesDict = {}

        for symbol in symbolsList:
            quotesDict[symbol] = getQuote(symbolsQuotes[symbol]["quote"])

        #print(f"quotesDict: \n{quotesDict}")
        return quotesDict
    except (KeyError, TypeError, ValueError):
        return None


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"


