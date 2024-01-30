from flask import Blueprint, request, jsonify
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user
from models.product import Product
from models.user import User

api = Blueprint("api", __name__)

login_manager = LoginManager()
login_manager.init_app(api)
login_manager.login_view = "login"

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(int(user_id))

@api.route("/")
def hello_world():
    return jsonify({ "hello": "World" })

@api.route("/login", methods=["POST"])
def login():
    data = request.json
    user = User.query.filter_by(username=data.get("username")).first()
    if user and data.get("password") == user.password:
        login_user(user)
        return jsonify({ "ok": True, "message": "Logged in successfully" })

    return jsonify({ "ok": False, "message": "Unauthorized! Invalid credentials" }), 401

@api.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()

    return jsonify({ "ok": True, "message": "Logout successfully" })

@api.route("/api/products/add", methods=["POST"])
@login_required
def add_product():
    data = request.json
    if "name" in data and "price" in data:
        product = Product(name=data["name"], price=data["price"], description=data["description"])
        db.session.add(product)
        db.session.commit()
        return jsonify({ "ok": True, "message": "Product add successfully" })

    return jsonify({ "ok": False, "message": "Invalid product data" }), 400

@api.route("/api/products/delete/<int:product_id>", methods=["DELETE"])
@login_required
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        return jsonify({ "ok": True, "message": "Product deleted successfully" })

    return jsonify({ "ok": False, "message": "Product not found" }), 404

@api.route("/api/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    if not products:
        return jsonify({ "ok": False, "message": "No products were found" }), 404

    product_list = []
    for product in products:
        product_data = {
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
        product_list.append(product_data)

    return jsonify(product_list)

@api.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id,
            "name": product.name,
            "price": product.price,
            "description": product.description
        })

    return jsonify({ "ok": False, "message": "Product not found" }), 404

@api.route("/api/products/<int:product_id>", methods=["PUT"])
@login_required
def update_product(product_id):
    product = Product.query.get(product_id)
    if not product:
        return jsonify({ "ok": False, "message": "Product not found" }), 404

    data = request.json
    if "name" in data:
        product.name = data['name']
    if "price" in data:
        product.price = data['price']
    if "description" in data:
        product.description = data['description']
    db.session.commit()

    return jsonify({ "ok": True, "message": "Product updated successfully" })
