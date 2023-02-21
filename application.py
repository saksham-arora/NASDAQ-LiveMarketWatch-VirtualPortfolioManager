import os

import sys
sys.stdout = sys.stderr
from cs50 import SQL
import datetime
from flask import Flask, flash, jsonify, redirect, render_template, request, session, json
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import csv


from helpers import apology, login_required, lookup, usd, getQuote, lookups

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")
symbolsDict = {}
historyDict = {}
quotes = []

with open('nasdaq.csv', 'r',) as file:
    reader = csv.reader(file, delimiter = ',')
    for row in reader:
        quotes.append(row[0])

#print(quotes)

symbolsRows = db.execute("select uid, symbol from stocks")
for symbol in symbolsRows:
    if not symbol["uid"] in symbolsDict:
        symbolsDict[symbol["uid"]] = [symbol["symbol"]]
    elif not symbol["symbol"] in symbolsDict[symbol["uid"]]:
        symbolsDict[symbol["uid"]].append(symbol["symbol"])

historyRows = db.execute("select * from history")
for h in historyRows:
    if not h["uid"] in historyDict:
        historyDict[h["uid"]] = [{"symbol": h["symbol"],
            "shares": h["shares"],
            "price": usd(h["price"]),
            "transacted": h["transcation_time"]
        }]
    else:
        historyDict[h["uid"]].append({"symbol": h["symbol"],
            "shares": h["shares"],
            "price": usd(h["price"]),
            "transacted": h["transcation_time"]
        })

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


buyPriceDictCurrentUser = {}
@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    rows = db.execute("select cash from users where id=:id", id=session["user_id"])

    if len(rows) != 1:
        return apology("Internal Error")

    cash = rows[0]["cash"]
    total = cash

    history = db.execute("select symbol, price from history where uid=:uid", uid=session["user_id"])
    for h in history:
        buyPriceDictCurrentUser[h["symbol"]] = h["price"]

    stocksList = db.execute("select symbol, name, shares from stocks where uid=:uid", uid=session["user_id"])

    stocksListWithPrice = stocksList
    symbolsList = []
    for i in range(len(stocksList)):
        symbolsList.append(stocksList[i]["symbol"])

    if len(symbolsList) != 0:
        quotesDict = lookups(symbolsList)

        for i in range(len(stocksList)):
       

            stocksListWithPrice[i]["buyPrice"] = usd(buyPriceDictCurrentUser[stocksList[i]["symbol"]])
            price = 0.00
            quote = quotesDict[stocksList[i]["symbol"]]

            if not quote:
                print(f"quote is empty for symbol:   {symbol}")
            else:
                price = quote["price"]
                price = round(price,2)

            stocksListWithPrice[i]["price"] = usd(price)
            stocksListWithPrice[i]["total"] = price*stocksList[i]["shares"]
            total = total + stocksListWithPrice[i]["total"]
            stocksListWithPrice[i]["total"] = usd(round(stocksListWithPrice[i]["total"],2))

    total = round(total,2)

    return render_template("index.html", cash=usd(cash), total=usd(total), stocksListWithPrice=stocksListWithPrice)



@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html",quotes=quotes)
    else:
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("Missing Symbol")

        if not shares:
            return apology("Missing Shares")

        shares = int(shares)

        quote = lookup(symbol)
        if not quote:
            return apology("Invalid Symbol")

        name = quote["name"]
        price = quote["price"]
        symbol = quote["symbol"]

        rows = db.execute("select cash from users where id = :uid", uid=session["user_id"])

        if len(rows) != 1:
            return apology("Internal Error")

        cash = rows[0]["cash"]
        price = round(price,2)
        value = price*shares
        value = round(value,2)
        if cash < value:
            return apology("Can't Afford")

        db.execute("UPDATE users set cash = cash - :value where id = :uid",value=value, uid=session["user_id"])

        count = db.execute("select count(*) from stocks where uid = :uid and symbol = :symbol",
        uid=session["user_id"], symbol=symbol)

        if count[0]["count(*)"] == 0:
            #print(f"inserting new stock {symbol} : {shares}")
            db.execute("insert into stocks VALUES(:uid, :symbol, :name, :shares)",
                uid=session["user_id"], symbol=symbol, name=name, shares=shares)
        else:
            #print(f"updating old stock {symbol} : {shares}")
            db.execute("update stocks set shares = shares + :shares where uid=:uid and symbol=:symbol",
                shares=shares, uid=session["user_id"], symbol=symbol)

        db.execute("insert into history('uid', 'symbol', 'shares', 'price') VALUES(:uid, :symbol, :shares, :price)",
                    uid=session["user_id"], symbol=symbol, shares=shares, price=price)

        if not symbol in symbolsDict[session["user_id"]]:
            symbolsDict[session["user_id"]].append(symbol)

        historyDict[session["user_id"]].append({"symbol":symbol,
                                                "shares":shares,
                                                "price":usd(price),
                                                "transacted":datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")})

        message = str(shares) + " shares of symbol " + str(symbol) + " are bought"
        if shares == 1:
            message = str(shares) + " share of symbol " + str(symbol) + " is bought"
        flash(message,"buy")
        return redirect("/")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    uid = session["user_id"]
    return render_template("history.html",historyList=historyDict[uid])

@app.route("/symbolsPrice")
def symbolsPrice():
    print("Call from AJAX for price")
    symbolDict = {}
    rows = db.execute("select symbol from stocks where uid = :uid", uid=session["user_id"])

    symbolsList = []
    for row in rows:
        symbolsList.append(row["symbol"])

    quotesDict = lookups(symbolsList)

    for symbol in symbolsList:
        symbolDict[symbol] = usd(round(quotesDict[symbol]["price"],2))

    return json.dumps(symbolDict)

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]
        if not session["user_id"] in historyDict:
            historyDict[session["user_id"]] = []

        if not session["user_id"] in symbolsDict:
            symbolsDict[session["user_id"]] = []

        # Redirect user to home page
        user = request.form.get("username")
        print(f"User: {user} is logged in so redirecting to home")

        flash("You are successfully Logged In","login")
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "GET":
        return render_template("quote.html",quotes=quotes)
    else:
        symbol = request.form.get("symbol")
        if not symbol:
            return apology("You must type a symbol")

        quote = lookup(symbol)

        if not quote:
            return apology("INVALID SYMBOL")

        return render_template("quoted.html", quote=quote)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    #return apology("TODO")
    if request.method == "GET":
        return render_template("register.html")
    else:
        username = request.form.get("username")
        if not username:
            return apology("You must provide a username")
        password = request.form.get("password")
        if not password:
            return apology("You must provide a password")
        passwordAgain = request.form.get("passwordAgain")
        if not passwordAgain:
            return apology("You must re-enter the password")

        rows = db.execute("select * from users where username = :username", username=username)

        if len(rows) != 0:
            return apology("Username is already taken. Please select some other username")

        db.execute("INSERT into users (username,hash) VALUES (:username,:hashpass)",
        username=username,hashpass=generate_password_hash(password))

        return redirect("/")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":
        return render_template("sell.html", symbolsList=symbolsDict[session["user_id"]])
    else:
        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        if not symbol:
            return apology("Missing Symbol")

        if not shares:
            return apology("Missing Shares")

        shares = int(shares)

        sharesList = db.execute("select shares from stocks where uid=:uid and symbol=:symbol",
                                uid=session["user_id"], symbol=symbol)

        if ( len(sharesList) == 1 and shares > sharesList[0]["shares"]):
            return apology("Exceeding Shares limit")

        quote = lookup(symbol)
        if not quote:
            return apology("Invalid Symbol")

        price = quote["price"]

        value = price*shares
        db.execute("UPDATE users set cash = cash + :value where id = :uid",value=value, uid=session["user_id"])

        print(f"updating old stock due to sell:  {symbol} : {shares}")
        db.execute("update stocks set shares = shares - :shares where uid=:uid and symbol=:symbol",
                    shares=shares, uid=session["user_id"], symbol=symbol)

        db.execute("insert into history('uid', 'symbol', 'shares', 'price') VALUES(:uid, :symbol, :shares, :price)",
                    uid=session["user_id"], symbol=symbol, shares=0-shares, price=price)

        countList = db.execute("select * from stocks where symbol = :symbol and uid = :uid",
                    symbol=symbol, uid=session["user_id"])

        if countList[0]["shares"] <= 0:
            symbolsDict[session["user_id"]].remove(symbol)
            db.execute("delete from stocks where symbol = :symbol and uid = :uid",
                        symbol=symbol, uid=session["user_id"])

        historyDict[session["user_id"]].append({"symbol":symbol,
                                                "shares":(0-shares),
                                                "price":usd(price),
                                                "transacted":datetime.datetime.now().strftime("%b %d %Y %H:%M:%S")})

        message = str(shares) + " shares of symbol " + str(symbol) + " are sold"
        if shares == 1:
            message = str(shares) + " share of symbol " + str(symbol) + " is sold"
        flash(message,"sell")
        return redirect("/")



def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
