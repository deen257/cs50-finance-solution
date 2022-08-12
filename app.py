import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    #get current user_id 
    id = session["user_id"][0]["id"]
    cash = db.execute("SELECT cash FROM users WHERE id = ?", id)
    balance = cash[0]["cash"]
    balance = round(balance, 3)
    accounts = db.execute("SELECT * FROM accounts WHERE account_id = ? AND number_of_shares >= 1 ", id)

    #show index page
    return render_template("index.html", accounts=accounts, balance = balance)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        #get user info
        id = session["user_id"][0]["id"]
        shares = int(request.form.get("shares"))
        symbol = request.form.get("symbol")
        quotes= lookup(symbol)
        #cheking for errors
        try:
            cash = db.execute("SELECT cash FROM users WHERE id = ? ", id )
            cash = cash[0]["cash"]
            number_of_shares = db.execute("SELECT number_of_shares FROM accounts JOIN users ON users.id = accounts.account_id WHERE users.id = ? AND symbol = ? ", id, quotes["symbol"])
            cost = round(quotes["price"],3) * float(shares)
        except TypeError:
            return apology("Invalid symbol", 403)

        if float(cash) < cost:
            return apology("Can't Afford It ", 403)
        else:
            #checking if the number of shares is empty
            if number_of_shares == []:
                shares_balance = shares
                db.execute("INSERT INTO accounts (account_id,number_of_shares, price, symbol, name) VALUES (?,?,?,?,?)",id, shares_balance, round(quotes["price"],3), quotes["symbol"],quotes["name"] )
            else:
                shares_balance = int(number_of_shares[0]["number_of_shares"]) + shares
            
            #make changes to database
            balance = float(cash) - cost
            name_of_company = quotes["name"]
            db.execute("UPDATE users SET cash = ? WHERE id = ? ", balance, id )
            db.execute("UPDATE accounts SET number_of_shares = ? WHERE account_id = ? AND  symbol = ? ",shares_balance, id, quotes["symbol"]  )
            db.execute("UPDATE accounts SET price = ? WHERE symbol = ?", round(quotes["price"],3), quotes["symbol"])
            db.execute("INSERT INTO transactions (name_of_company,price ,symbol ,shares, type, user_id, transacted)  VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)",name_of_company,round(quotes["price"],3),quotes["symbol"],shares,"BUY", id)
            return redirect("/")


    else:
        return render_template("buy.html")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    #user info
    id = session["user_id"][0]["id"]
    accounts = db.execute("SELECT * FROM transactions WHERE user_id = ? ORDER BY transacted DESC", id)
    #rendering history page
    return render_template("history.html", accounts=accounts)



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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
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
    if request.method == "POST":
        symbol = request.form.get("symbol")
        quotes = lookup(symbol)
        #checking for user error
        try:
            #if the lookup function cant find the symbol
            qsymbol = quotes["symbol"]
        except TypeError:
            return apology("Invalid symbol", 403)
        if not quote:
                return apology("missing symbol", 403)
        #render quote if symbol is valid
        else:
            db.execute("UPDATE accounts SET price = ? WHERE symbol = ?",round(quotes["price"],3), quotes["symbol"])
            return render_template("quoted.html", quotes=quotes)
    else :
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    #if user sends a GET request show form
    if request.method == "GET":
        return render_template("register.html")
    # if user sends a POST request
    else :
    # get these information from the form
        username = request.form.get("username")
        password = request.form.get("password")
        password1 = request.form.get("password1")
        user_name = db.execute("SELECT username FROM users WHERE username = ? ", username )
        print(username)
        #checking for user error
        if not username :
            return apology("must provide username", 403)
        elif not password or not password1:
            return apology("must provide password", 403)
        elif password != password1:
            return apology("password doesn't match", 403)
        # if not user error generate password hash, insert user and set session id
        else:
            hash = generate_password_hash(password)
            try:
                #try an insert user except the user is already in the db
                db.execute("INSERT INTO users (username, hash ) VALUES (?,?)",username , hash)
                session["user_id"] = db.execute("SELECT id FROM users WHERE username = ?", username)
                # redirect to the quotes page
                return redirect("/quote")
            except ValueError:
                return apology("username already exists", 403)



@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    # geting user info
    id = session["user_id"][0]["id"]
    accounts = db.execute("SELECT * FROM accounts WHERE account_id = ? AND number_of_shares >= 1 ", id)
    """Sell shares of stock"""
    if request.method == "POST":
        #for post method get info
        symbol = request.form.get("symbol")
        shares = int(request.form.get("shares"))
        cash = db.execute("SELECT cash FROM users WHERE id = ? ", id )
        cash = cash[0]["cash"]
        quotes= lookup(symbol)

        #checking for user error
        if not shares:
            return apology("Missing shares", 403)
        try:
            number_of_shares = db.execute("SELECT number_of_shares FROM accounts JOIN users ON users.id = accounts.account_id WHERE users.id = ? AND symbol = ? ", id, quotes["symbol"])
        except TypeError:
            return apology("Missing symbol", 403)


        cost = round(quotes["price"],3) * shares
        if int(number_of_shares[0]["number_of_shares"]) < shares:
            return apology("You don't know enough shares", 400)
        else:
            #make changes to database
            present_shares = int(number_of_shares[0]["number_of_shares"]) - shares
            present_balance = float(cash) + cost
            name_of_company = quotes["name"]
            db.execute("UPDATE users SET cash = ? WHERE id = ? ", present_balance, id )
            db.execute("UPDATE accounts SET number_of_shares = ? WHERE account_id = ? AND  symbol = ? ",present_shares, id, quotes["symbol"]  )
            db.execute("UPDATE accounts SET price = ? WHERE symbol = ?", round(quotes["price"],3), quotes["symbol"])
            db.execute("INSERT INTO transactions (name_of_company,price ,symbol ,shares, type, user_id, transacted)  VALUES (?,?,?,?,?,?,CURRENT_TIMESTAMP)",name_of_company,round(quotes["price"],3),quotes["symbol"],shares,"SELL", id)
            return redirect("/")

    else:
        return render_template("sell.html", accounts=accounts)

