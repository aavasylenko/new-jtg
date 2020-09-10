import os
from flask import (
    Flask, flash, render_template, redirect,
    request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)

@app.route("/", methods = ["GET", "POST"])
def index():
    return render_template('index.html')

@app.route("/shop", methods = ["GET", "POST"])
def shop():
    products = list(mongo.db.products.find())
    return render_template('shop.html', products=products)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        #check if username already exists in db
        existing_user = mongo.db.users.find_one(
            {"email": request.form.get("email").lower()})
        
        if existing_user:
            #check hashed password matches user input
            if check_password_hash(
                existing_user["password"], request.form.get("password")):
                    session["user"] = "admin"
                    flash("Admin View")
                    return redirect(url_for('index'))
            else:
                #invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login"))
        
        else:
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login"))

    return render_template('login.html')

@app.route('/logout')
def logout():
    #remove user from session cookies
    flash("You've been logged out")
    session.pop("user")
    return redirect(url_for('login'))

    
@app.route('/change_pass', methods=["GET", "POST"])
def change_pass():
    if session["user"] == "admin":
        if request.method == "POST":
            existing_user = mongo.db.users.find_one({"email": "jenningstacticalguns@yahoo.com"})
            
            if existing_user:
                if check_password_hash(
                    existing_user["password"], request.form.get("old_password")):
                    if request.form.get("new_password") == request.form.get("confirm_new_password"):
                        mongo.db.users.update(
                            {"username": "admin"}, {"password": generate_password_hash(request.form.get("new_password")), "username": "admin", "email": "jenningstacticalguns@yahoo.com"})
                        flash("Password changed successfully")
                        return redirect('/index')
                    else:
                        flash("Passwords don't match")
                        return redirect('/change_pass')
                else:
                    flash("Incorrect current password")
                    return redirect('/change_pass')
        return render_template('change_pass.html')
    else:
        return redirect('/index')

if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)