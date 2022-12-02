# ---------------------------------------------Import Modules----------------------------------------------------------#
from flask import Flask, render_template, redirect, url_for, flash, abort
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_login import UserMixin, login_user, LoginManager, current_user, logout_user
from functools import wraps
from werkzeug.security import generate_password_hash, check_password_hash
from flask_gravatar import Gravatar
from flask_ckeditor import CKEditor
from forms import RegisterForm, LoginForm, AddProductForm
import stripe

# ------------------------------------------CONSTANTS & Variables------------------------------------------------------#
stripe.api_key = "YOUR STRIPE SECRET KEY"
DOMAIN = "http://localhost:4242"

# ------------------------------------------Create app object from Flask Class-----------------------------------------#
app = Flask(__name__)
# Configure the app object with a secret key. It can be whatever you want.
app.config['SECRET_KEY'] = 'THISISYOURSECRETKEYCOMEUPWITHSOMETHINGGREAT'
# Create object from CKEditor.
ckeditor = CKEditor(app)
# Specify that Bootstrap shall be utilized with app object
Bootstrap(app)
# Create gravatar object
gravatar = Gravatar(
    app,
    size=100,
    rating="g",
    default="retro",
    force_default=False,
    force_lower=False,
    use_ssl=False,
    base_url=None,
)

# ---------------------------------------Create databases from SQLAlchemy----------------------------------------------#
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"  # Configure the app to connect to store database
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Turn modification tracking off on app object
db = SQLAlchemy(app)

# ----------------------------------------------Set up Login Manager---------------------------------------------------#
login_manager = LoginManager()  # Create a loging manage object from the Class
login_manager.init_app(app)  # Use method to create a login manager for the app


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------------Create tables within the store database---------------------------------------------#
class Products(db.Model):
    __tablename__ = "products"  # Specifies a table within the database
    # Set columns of the SQL database
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.String(26), unique=True, nullable=False)
    product_name = db.Column(db.String(250), unique=True, nullable=False)
    product_price = db.Column(db.Float, unique=False, nullable=False)
    wholesale_price = db.Column(db.Float, unique=False, nullable=False)
    quantity = db.Column(db.Float, unique=False, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)
    description = db.Column(db.String(500), nullable=False)


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(100))


# ------------------------------------------------Initiate the database------------------------------------------------#
# Comment out once the database has been initially created
# with app.app_context():
#     db.create_all()


# ------------------------------------------Create decorator for admin only--------------------------------------------#
def admin_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function


# -----------------------------------------Create Routes to the web pages----------------------------------------------#
# Set home page routing
@app.route("/")
def home():
    products = Products.query.all()
    return render_template("index.html", all_products=products, current_user=current_user)


@app.route("/create-checkout_session/<int:product_number>", methods=["GET", "POST"])
def create_checkout_session(product_number):
    product = Products.query.get(product_number)
    if not product.quantity:
        in_stock = False
    else:
        in_stock = True
    stripe.Product.create(
        name=product.product_name,
        description=product.description,
        default_price_data=product.product_price,
        active=in_stock,
    )
    try:
        checkout_session = stripe.checkout.Session.create(
            success_url=DOMAIN + "/success.html",
            cancel_url=DOMAIN + "/cancel.html",
            line_items=[{"price": product.product_price, "quantity": product.quantity}],
            mode="payment"
        )
    except Exception as e:
        return str(e)
    return redirect(checkout_session.url, code=303)


# Login routing
@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        user = User.query.filter_by(email=email).first()
        if not user:
            flash(message="Incorrect")
            return redirect(url_for("login"))
        elif not check_password_hash(pwhash=user.password, password=password):
            flash(message="Incorrect")
            return redirect(url_for("login"))
        else:
            login_user(user)
            return redirect(url_for("home"))
    return render_template("login.html", form=form, current_user=current_user)


# Logout routing
@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


# New Account routing
@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(email=form.email.data).first():
            flash(message="That email address has already been used. Try again.")
            return redirect(url_for("register"))
        hash_salted_pw = generate_password_hash(
            form.password.data,
            method="pbkdf2:sha256",
            salt_length=8,
        )
        new_user = User(
            email=form.email.data,
            name=form.name.data,
            password=hash_salted_pw,
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for("home"))
    return render_template("register.html", form=form, current_user=current_user)


# Adding new items routing
@app.route("/stock", methods=["GET", "POST"])
@admin_only
def add_stock():
    form = AddProductForm()
    if form.validate_on_submit():
        new_product = Products(
            product_id=form.product_id.data,
            product_name=form.product_name.data,
            product_price=form.product_price.data,
            wholesale_price=form.wholesale_price.data,
            quantity=form.quantity.data,
            img_url=form.img_url.data,
            description=form.description.data,
        )
        db.session.add(new_product)
        db.session.commit()
        return redirect(url_for("add_stock"))
    return render_template("stock.html", form=form, current_user=current_user)


@app.route("/stock/<int:product_number>", methods=["GET", "POST"])
def show_product(product_number):
    requested_product = Products.query.get(product_number)

    return render_template("product.html", product=requested_product, current_user=current_user)


# Edit stock route
@app.route("/edit-stock/<int:product_number>", methods=["GET", "POST"])
@admin_only
def edit_stock(product_number):
    product = Products.query.get(product_number)
    edit_form = AddProductForm(
        product_id=product.product_id,
        product_name=product.product_name,
        product_price=product.product_price,
        wholesale_price=product.wholesale_price,
        quantity=product.quantity,
        img_url=product.img_url,
        description=product.description,
    )
    if edit_form.validate_on_submit():
        product.product_id = edit_form.product_id.data
        product.product_name = edit_form.product_name.data
        product.product_price = edit_form.product_price.data
        product.wholesale_price = edit_form.wholesale_price.data
        product.quantity = edit_form.quantity.data
        product.img_url = edit_form.img_url.data
        product.description = edit_form.description.data
        db.session.commit()
        return redirect(url_for("home", product_number=product.id))
    return render_template("stock.html", form=edit_form, is_edit=True, current_user=current_user)


@app.route("/delete/<int:product_number>")
@admin_only
def delete_product(product_number):
    product_to_delete = Products.query.get(product_number)
    db.session.delete(product_to_delete)
    db.session.commit()
    return redirect(url_for("home"))


# Initiate the script and start a development server
if __name__ == "__main__":
    app.run(debug=True)
