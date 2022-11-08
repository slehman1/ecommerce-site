
from flask import *
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from products import plushies, posterz, apparels, all_items
from flask_bootstrap import Bootstrap

#trying to build something like this: https://store.waitbutwhy.com/products/mammoth-tee?variant=10794677377
#plush toys, posters, and tshirts

app = Flask(__name__)
app.config['SECRET_KEY'] = "SECRET_KEY1"
Bootstrap(app)

class CheckoutForm(FlaskForm):
    card_num = StringField('Card number', validators=[DataRequired()])
    card_name = StringField('Name on card', validators=[DataRequired()])
    expire = StringField('Expiry date', validators=[DataRequired()])
    security_code = StringField('Security code', validators=[DataRequired()])
    submit = SubmitField("Complete Purchase")

cart_items = {}

top_apperelz = dict(list(apparels.items())[:5])
top_posterz = dict(list(posterz.items())[:5])
top_plushiez = dict(list(plushies.items())[:5])

@app.route("/", methods=["GET", "POST"])
def index():
    return render_template("index.html")

@app.route("/store", methods=["GET", "POST"])
def store():
    return render_template("store.html", apparelz=top_apperelz, posterz=top_posterz, plushiez=top_plushiez)

@app.route("/blog")
def blog():
    return render_template("blog.html")

@app.route("/plush_toys", methods=["GET", "POST"])
def plush_toys():
    return render_template("plush_toys.html", plush_toyz=plushies)

@app.route("/posters", methods=["GET", "POST"])
def posters():
    return render_template("posters.html", posterz=posterz)

@app.route("/apparel", methods=["GET", "POST"])
def apparel():
    return render_template("apparel.html", apparels=apparels)

@app.route("/product", methods=["GET", "POST"])
def product():
    if request.method == "GET":
        product_id = request.args.get("product_id")
        product_dict = all_items[product_id]
        img_url = product_dict["img_url"]
        title = product_dict['product_title']
        price = product_dict['product_price']
        description = product_dict['description']
    if request.method == "POST":
        product_id2 = request.form.get("product_id")
        product_dict = all_items[product_id2]
        img_url = product_dict["img_url"]
        title = product_dict['product_title']
        price = product_dict['product_price']
        description = product_dict['description']

        quantity = int(request.form.get('quantity'))
        if quantity > 0:
            cart_items[product_id2] = all_items[product_id2]
            cart_items[product_id2]["quantity"] = quantity
        return redirect('store')
    return render_template("product.html", img_url=img_url, title=title, price=price, description=description, product_id=product_id)

@app.route("/cart", methods=["GET", "POST"])
def cart():
    subtotal = 0
    for cart_item in cart_items:
        print(cart_item)
        cost = float(cart_items[cart_item]["product_price"].split('$')[1])
        subtotal += cost * (cart_items[cart_item]["quantity"])

    return render_template("cart.html", cart=cart_items, subtotal=subtotal)

@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    my_checkout_form = CheckoutForm()
    if my_checkout_form.validate_on_submit():
        cart_items.clear()
        return render_template("index.html", order=True)
    return render_template("checkout.html", form=my_checkout_form)




if __name__ == "__main__":
    app.run(debug=True)