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
    return render_template('shop.html')

app.run(host=os.getenv('IP', '0.0.0.0'), port=int(os.getenv('PORT', "5000")), debug=True)