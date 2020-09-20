import os
from flask import (
    Flask, flash, render_template, redirect,
    request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
if os.path.exists("env.py"):
    import env

app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")


mongo = PyMongo(app)


@app.route('/', methods=["GET", "POST"])
def index():
    return render_template('index.html')


@app.route("/shop_ammo", methods = ["GET", "POST"])
def shop_ammo():
    products = list(mongo.db.products.find({"category": "ammo"}))
    return render_template('shop.html', products=products)


@app.route("/shop_parts", methods = ["GET", "POST"])
def shop_parts():
    products = list(mongo.db.products.find({"category": "parts"}))
    return render_template('shop.html', products=products)


@app.route('/404')
def fourofour():
    return render_template("404.html")


@app.route('/search', methods=["GET", "POST"])
def search():
    query = request.form.get("query")
    products = list(mongo.db.products.find({"$text": {"$search": query}}))
    return render_template("shop.html", products=products)    





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
                if check_password_hash(existing_user["password"], request.form.get("old_password")):
                    if request.form.get("new_password") == request.form.get("confirm_new_password"):
                        mongo.db.users.update(
                            {"username": "admin"}, {"password": generate_password_hash(request.form.get("new_password")), "username": "admin", "email": "jenningstacticalguns@yahoo.com"})
                        flash("Password changed successfully")
                        return redirect(url_for('index'))
                    else:
                        flash("Passwords don't match")
                        return redirect(url_for('change_pass'))
                else:
                    flash("Incorrect current password")
                    return redirect(url_for('change_pass'))
        return render_template('change_pass.html')
    else:
        return redirect(url_for('index'))



@app.route('/add_products', methods=["GET", "POST"])
def add_products():
    if session["user"] == "admin":
        if request.method == "POST":
            is_available = "on" if request.form.get("is_available") else "off"
            if 'image' in request.files:
                image = request.files['image']
                if mongo.db.products.find_one({"img_src": image.filename}):
                    image.filename = uuid.uuid4().hex[:6].upper()
                mongo.save_file(image.filename, image)
                product = {
                    "name": request.form.get("product_name"),
                    "price": request.form.get("price"),
                    "is_available": is_available,
                    "category": request.form.get("category"),
                    "img_src": image.filename
                }
                mongo.db.products.insert_one(product)
                flash("Product Successfully Added")
                return redirect(url_for('index'))
        categories = mongo.db.categories.find()
        return render_template('add_products.html', categories=categories)
    else:
        return redirect(url_for('index'))


@app.route('/file/<filename>')
def file(filename):
    return mongo.send_file(filename)


@app.route('/delete_product/<product_id>')
def delete_product(product_id):
    if session["user"] == "admin":
        mongo.db.products.remove({"_id": ObjectId(product_id)})
        flash("Product Successfully Deleted")
        return redirect(url_for("shop"))
    else:
        return redirect(url_for("fourofour"))

#############################################################################################


@app.route('/edit_product/<product_id>', methods=["GET", "POST"])
def edit_product(product_id):
    if session["user"] == "admin":
        if request.method == "POST":
            is_available = "on" if request.form.get("is_available") else "off"
            submit = {
                "name": request.form.get("product_name"),
                "price": request.form.get("price"),
                "is_available": is_available,
                "category": request.form.get("category"),
                "img_src": request.form.get("img_src")
            }
            mongo.db.products.update({"_id": ObjectId(product_id)}, submit)
            flash("Product Successfully Updated")
            return redirect(url_for('index'))

        categories = mongo.db.categories.find()
        product = mongo.db.products.find_one({"_id": ObjectId(product_id)})
        return render_template('edit_product.html', product=product, categories=categories)
    else:
        return redirect(url_for("fourofour"))


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)