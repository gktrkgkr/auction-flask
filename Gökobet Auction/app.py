import os
import datetime
from flask import Flask, render_template, request, flash, session, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config["SECRET_KEY"] = "yoursecretkey"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:karadeniz@34.121.66.9/auction'

db = SQLAlchemy(app)


class users(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Unicode)
    name = db.Column(db.Unicode)
    surname = db.Column(db.Unicode)
    email = db.Column(db.Unicode)
    password = db.Column(db.Unicode)

    def init(self, username, name, surname, email, password):
        self.username = username
        self.name = name
        self.surname = surname
        self.email = email
        self.password = password


class Bids(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    bid_value = db.Column(db.Integer)
    bidder_ID = db.Column(db.Integer)
    item_ID = db.Column(db.Integer)

    def init(self, bid_value, bidder_ID, item_ID):
        self.bid_value = bid_value
        self.bidder_ID = bidder_ID
        self.item_ID = item_ID


class Items(db.Model):
    ID = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.Unicode)
    start_price = db.Column(db.Float)
    current_price = db.Column(db.Float)
    sold = db.Column(db.Boolean)
    date = db.Column(db.Date)
    date_sold = db.Column(db.Date)
    seller_ID = db.Column(db.Integer)
    due_date = db.Column(db.Date)
    top_bidder_ID = db.Column(db.Integer)

    def init(self, item_name, start_price, current_price, sold, date, date_sold, seller_ID, due_date, top_bidder_ID):
        self.item_name = item_name
        self.start_price = start_price
        self.current_price = current_price
        self.sold = sold
        self.date = date
        self.date_sold = date_sold
        self.seller_ID = seller_ID
        self.due_date = due_date
        self.top_bidder_ID = top_bidder_ID

logged_in = False
usersname = ""

@app.route("/items")
def items():
    item_check = Items.query.all()
    if "username" in session:
        global usersname
        usersname = session["username"]
    for i in item_check:
        if i.due_date < datetime.datetime.now():
            i.sold = True
            db.session.commit()
    itemses = Items.query.all()
    return render_template("items.html", itemses=itemses, logged_in=logged_in, usersname=usersname)


@app.route("/bid/<Item_id>", methods=["POST", "GET"])
def bid(Item_id):
    if request.method == "POST":
        if "userID" in session:
            bid_value = request.form["bid_value"]
            bidder_ID = session["userID"]
            this_item = Items.query.filter_by(ID=Item_id).first()
            current_price = this_item.current_price
            if float(bid_value) > current_price:
                newbid = Bids(bid_value=bid_value, bidder_ID=bidder_ID, item_ID=Item_id)
                db.session.add(newbid)
                this_item.top_bidder_ID = bidder_ID
                this_item.current_price = float(bid_value)
                db.session.commit()
                flash("Bid successful!", "info")
            else:
                flash("You can't bid below the current price!", "error")
            return redirect(url_for("items"))


@app.route("/")
def index():
    if "userID" in session:
        redirect(url_for("items"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session.permanent = True
        username = request.form["username"]
        password = request.form["password"]
        found_user = users.query.filter_by(username=username).first()
        if found_user.username == username and found_user.password == password:
            session["userID"] = found_user.ID
            session["username"] = username
            global logged_in
            global usersname
            usersname = "username"
            logged_in = True
            flash("Login Successful!", "info")
            return redirect(url_for("items"))
        else:
            flash("Incorrect username or password", "error")
            return redirect(url_for("login"))
    else:
        if "userID" in session:
            flash("Already logged in!", "info")
            return redirect(url_for("items"))
        else:
            return render_template("login.html")


@app.route("/logout")
def logout():
    if "userID" in session:
        session.pop("userID", None)
        session.pop("username", None)
        global logged_in
        logged_in = False
        flash("You have been logged out!", "info")
        return redirect(url_for("login"))


@app.route("/signup")
def signup():
    if "userID" in session:
        flash("You are already logged in!", "info")
        return redirect(url_for("items"))
    return render_template("signup.html")


@app.route("/create")
def create():
    return render_template("create.html", username=usersname, logged_in=logged_in)


@app.route("/created", methods=["POST"])
def created():
    if "userID" in session:
        item_name = request.form["item_name"]
        start = int(request.form["start"])
        due_date = request.form["due_date"]
        seller_ID = session["userID"]

        if not item_name:
            flash("Please fill every field!", "error")
        elif not start:
            flash("Please fill every field!", "error")
        elif not due_date:
            flash("Please fill every field!", "error")
        else:
            newitem = Items(item_name=item_name, start_price=start, current_price=start, sold=0, seller_ID=seller_ID, due_date=due_date, date=datetime.date.today())
            db.session.add(newitem)
            db.session.commit()
            return redirect(url_for("items"))
    else:
        flash("You must be logged in to do that!", "error")
        return redirect(url_for("login"))


@app.route("/success", methods=["POST"])
def successs():
    username = request.form["username"]
    name = request.form["name"]
    surname = request.form["surname"]
    email = request.form["email"]
    password = request.form["password"]
    check = users.query.filter_by(email=email).first()

    if check is not None:
        return redirect(url_for("signup"))
    if not username:
        flash("Please fill every field!", "error")
    elif not name:
        flash("Please fill every field!", "error")
    elif not surname:
        flash("Please fill every field!", "error")
    elif not email:
        flash("Please fill every field!", "error")
    elif not password:
        flash("Please fill every field!", "error")
    else:
        newlog = users(username=username, name=name, surname=surname, email=email, password=password)
        db.session.add(newlog)
        db.session.commit()
        return render_template("login.html")
    return render_template("signup.html")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5000)))