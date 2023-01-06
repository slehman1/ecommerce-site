
from flask import *
from flask_wtf import FlaskForm
# from wtforms import StringField, SubmitField
# from wtforms.validators import DataRequired
from products import all_items
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import datetime
import time

#trying to build something like this: https://store.waitbutwhy.com/products/mammoth-tee?variant=10794677377
#plush toys, posters, and tshirts

app = Flask(__name__)
app.config['SECRET_KEY'] = "SECRET_KEY1"
Bootstrap(app)

#connect to db
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

with app.app_context():
    class User(db.Model):
        __tablename__ = "users"
        id = db.Column(db.Integer, primary_key=True)
        username = db.Column(db.String(250), nullable=False, unique=True)
        password_hash = db.Column(db.String(250), nullable=False)
        cart = db.relationship('Cart', backref='user')

    class Item(db.Model):
        __tablename__ = "items"
        id = db.Column(db.Integer, primary_key=True)
        product_title = db.Column(db.String(100), nullable=False)
        product_price = db.Column(db.String(50), nullable=False)
        img_url = db.Column(db.String(500), nullable=False)
        description = db.Column(db.String(250), nullable=False)
        item_type = db.Column(db.String(250), nullable=False)
        cart = db.relationship('Cart', backref='item')


    class Cart(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        item_id = db.Column(db.Integer, db.ForeignKey(Item.id))
        quantity = db.Column(db.Integer, nullable=False)
        user_id = db.Column(db.Integer, db.ForeignKey(User.id))
        purchased = db.Column(db.Boolean, nullable=False)
        purchase_date_date = db.Column(db.String(50), nullable=True)
        purchase_date_num = db.Column(db.Integer, nullable=True)

    db.create_all()



def add_items():
    for v in all_items.values():
        print(v)
        new_item = Item(
            product_title=v["product_title"],
            product_price=v["product_price"],
            img_url=v["img_url"],
            description=v["description"],
        )
        db.session.add(new_item)
        db.session.commit()

# class CheckoutForm(FlaskForm):
#     card_num = StringField('Card number', validators=[DataRequired()])
#     card_name = StringField('Name on card', validators=[DataRequired()])
#     expire = StringField('Expiry date', validators=[DataRequired()])
#     security_code = StringField('Security code', validators=[DataRequired()])
#     submit = SubmitField("Complete Purchase")


@app.route("/", methods=["GET", "POST"])
def index():
    print(session["user_id"])
    return render_template("index.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users = User.query.filter_by(username=username).first()
        if not users:
            flash("Username not found!")
            return redirect("login")
        phash = User.query.filter_by(username=username).first().password_hash
        pword_good = check_password_hash(phash, password)
        if not pword_good:
            flash("Incorrect password!")
            return redirect("login")
        session["user_id"] = User.query.filter_by(username=username).first().id
        return redirect("/")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        users = User.query.filter_by(username=username).first()
        print(users)
        if not username or not password:
            flash("Please fill in all fields!")
            return redirect("register")
        if users:
            flash('Username already in use')
            return redirect("register")
        p_hash = generate_password_hash(password)
        new_user = User(
            username = username,
            password_hash = p_hash

        )
        db.session.add(new_user)
        db.session.commit()

        return redirect("login")
    return render_template("register.html")

@app.route("/orders")
def orders():
    user_id = session["user_id"]
    purchased_items = Cart.query.filter(Cart.user_id == user_id, Cart.purchased == True).order_by(Cart.purchase_date_num.desc()).all()
    return render_template("orders.html", orders=purchased_items)


@app.route("/store", methods=["GET", "POST"])
def store():
    top_plushiez = Item.query.filter_by(item_type="Plushy").limit(5).all()
    top_posterz = Item.query.filter_by(item_type="Poster").limit(5).all()
    top_apparelz = Item.query.filter_by(item_type="Apparel").limit(5).all()
    return render_template("store.html", apparelz=top_apparelz, posterz=top_posterz, plushiez=top_plushiez)

@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/billing")
def billing():
    return render_template("billing.html")

@app.route("/plush_toys", methods=["GET", "POST"])
def plush_toys():
    plushies = Item.query.filter_by(item_type="Plushy").all()
    return render_template("plush_toys.html", plush_toyz=plushies)

@app.route("/posters", methods=["GET", "POST"])
def posters():
    posterz = Item.query.filter_by(item_type="Poster").all()
    return render_template("posters.html", posterz=posterz)

@app.route("/apparel", methods=["GET", "POST"])
def apparel():
    apparels = Item.query.filter_by(item_type="Apparel").all()
    return render_template("apparel.html", apparels=apparels)

@app.route("/product", methods=["GET", "POST"])
def product():
    user_id = session["user_id"]
    if request.method == "POST":
        product_id_buying = request.form.get("product_id")
        quantity = int(request.form.get('quantity'))
        if quantity > 0:
            new_cart = Cart(
                item_id = product_id_buying,
                quantity = quantity,
                user_id = user_id,
                purchased = False,
            )
            db.session.add(new_cart)
            db.session.commit()

        return redirect('store')

    if request.method == "GET":
        product_id = request.args.get("product_id")
        this_product = Item.query.filter_by(id=product_id).first()
    return render_template("product.html", product=this_product)

@app.route("/cart", methods=["GET", "POST"])
def cart():
    user_id = session["user_id"]
    cart_items = Cart.query.filter(Cart.user_id == user_id, Cart.purchased == False).all()
    subtotal = 0
    for item in cart_items:
        cost = float(item.item.product_price.split("$")[1])
        quantity = item.quantity
        subtotal += cost * quantity
    print(subtotal)

    return render_template("cart.html", cart=cart_items, subtotal=subtotal)

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        user_id = session["user_id"]
        date_num = time.time()
        date_date = datetime.datetime.now().strftime("%Y-%m-%d")
        Cart.query.filter(Cart.user_id == user_id, Cart.purchased == False).update({'purchased': True, "purchase_date_date": date_date, "purchase_date_num": date_num})
        db.session.commit()

        #make all items purchased
        return render_template("index.html", order=True)
    return render_template("checkout.html")




if __name__ == "__main__":
    app.run(debug=True)