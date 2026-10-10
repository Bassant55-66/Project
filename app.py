from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_bcrypt import Bcrypt
from models import db, User, Order

app = Flask(__name__)
CORS(app)
bcrypt = Bcrypt(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

with app.app_context():
    db.create_all()


# --------------------
# Products (in memory)
# --------------------

products = [
    {
        "id": 1,
        "name": "Laptop",
        "price": 25000,
        "category": "Electronics"
    },
    {
        "id": 2,
        "name": "Headphones",
        "price": 1500,
        "category": "Electronics"
    },
    {
        "id": 3,
        "name": "T-Shirt",
        "price": 500,
        "category": "Clothes"
    }
]

cart = []


@app.route("/")
def home():
    return jsonify({
        "message": "Welcome to TPT E-commerce API!"
    })


# --------------------
# Products APIs
# --------------------

@app.route("/api/products", methods=["GET"])
def get_products():
    return jsonify(products)


@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    for product in products:
        if product["id"] == product_id:
            return jsonify(product)

    return jsonify({"message": "Product not found"}), 404


@app.route("/api/products", methods=["POST"])
def add_product():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data provided"}), 400

    if not all(key in data for key in ("name", "price", "category")):
        return jsonify({
            "message": "Name, price and category are required"
        }), 400

    new_id = max(
        (product["id"] for product in products),
        default=0
    ) + 1

    new_product = {
        "id": new_id,
        "name": data["name"],
        "price": data["price"],
        "category": data["category"]
    }

    products.append(new_product)

    return jsonify({
        "message": "Product added successfully",
        "product": new_product
    }), 201


@app.route("/api/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    for product in products:
        if product["id"] == product_id:
            products.remove(product)
            return jsonify({
                "message": "Product deleted successfully"
            })

    return jsonify({"message": "Product not found"}), 404


@app.route("/api/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data provided"}), 400

    for product in products:
        if product["id"] == product_id:
            for key in ("name", "price", "category"):
                if key in data:
                    product[key] = data[key]

            return jsonify({
                "message": "Product updated successfully",
                "product": product
            })

    return jsonify({"message": "Product not found"}), 404


# --------------------
# Cart APIs
# --------------------

@app.route("/api/cart", methods=["POST"])
def add_to_cart():
    data = request.get_json()

    if not data or "product_id" not in data:
        return jsonify({"message": "product_id is required"}), 400

    product_id = data["product_id"]
    quantity = data.get("quantity", 1)

    if (
        not isinstance(product_id, int)
        or isinstance(product_id, bool)
        or not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity < 1
    ):
        return jsonify({
            "message": "product_id and quantity must be valid integers; quantity must be at least 1"
        }), 400

    for product in products:
        if product["id"] == product_id:
            for item in cart:
                if item["product_id"] == product_id:
                    item["quantity"] += quantity
                    return jsonify({
                        "message": "Product quantity updated",
                        "cart": cart
                    }), 200

            cart.append({
                "product_id": product_id,
                "name": product["name"],
                "price": product["price"],
                "quantity": quantity
            })

            return jsonify({
                "message": "Product added to cart",
                "cart": cart
            }), 201

    return jsonify({"message": "Product not found"}), 404


@app.route("/api/cart", methods=["GET"])
def get_cart():
    return jsonify(cart)


@app.route("/api/cart/<int:product_id>", methods=["PUT", "DELETE"])
def update_cart(product_id):
    if request.method == "DELETE":
        for item in cart:
            if item["product_id"] == product_id:
                cart.remove(item)
                return jsonify({
                    "message": "Product removed from cart successfully",
                    "cart": cart
                })

        return jsonify({
            "message": "Product not found in cart"
        }), 404

    data = request.get_json()

    if not data or "quantity" not in data:
        return jsonify({"message": "quantity is required"}), 400

    quantity = data["quantity"]

    if (
        not isinstance(quantity, int)
        or isinstance(quantity, bool)
        or quantity < 1
    ):
        return jsonify({
            "message": "quantity must be a positive integer"
        }), 400

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] = quantity
            return jsonify({
                "message": "Cart quantity updated successfully",
                "cart": cart
            })

    return jsonify({
        "message": "Product not found in cart"
    }), 404


# --------------------
# User Registration API
# --------------------

@app.route("/api/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"message": "JSON data is required"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not all(
        isinstance(value, str) and value.strip()
        for value in (username, email, password)
    ):
        return jsonify({
            "message": "Username, email and password are required"
        }), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    hashed_password = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    new_user = User(
        username=username,
        email=email,
        password_hash=hashed_password
    )

    db.session.add(new_user)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user_id": new_user.id
    }), 201


# --------------------
# User Login API
# --------------------

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data:
        return jsonify({"message": "JSON data is required"}), 400

    email = data.get("email")
    password = data.get("password")

    if not isinstance(email, str) or not isinstance(password, str):
        return jsonify({
            "message": "Email and password are required"
        }), 400

    user = User.query.filter_by(email=email).first()

    if user and bcrypt.check_password_hash(
        user.password_hash, password
    ):
        return jsonify({
            "message": "Login successful",
            "user_id": user.id,
            "username": user.username
        }), 200

    return jsonify({
        "message": "Invalid email or password"
    }), 401


# --------------------
# Orders APIs
# --------------------

@app.route("/api/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    if not data:
        return jsonify({"message": "JSON data is required"}), 400

    user_id = data.get("user_id")
    total_price = data.get("total_price")

    if (
        not isinstance(user_id, int)
        or isinstance(user_id, bool)
        or not isinstance(total_price, (int, float))
        or isinstance(total_price, bool)
        or total_price < 0
    ):
        return jsonify({
            "message": "A valid user_id and non-negative total_price are required"
        }), 400

    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    new_order = Order(
        user_id=user_id,
        total_price=total_price,
        status="Pending"
    )

    db.session.add(new_order)
    db.session.commit()

    return jsonify({
        "message": "Order created successfully",
        "order_id": new_order.id
    }), 201


@app.route("/api/orders/<int:user_id>", methods=["GET"])
def get_user_orders(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"message": "User not found"}), 404

    orders = Order.query.filter_by(user_id=user_id).all()

    orders_list = [
        {
            "id": order.id,
            "total_price": order.total_price,
            "status": order.status,
            "created_at": order.created_at.strftime(
                "%Y-%m-%d %H:%M:%S"
            )
        }
        for order in orders
    ]

    return jsonify({"orders": orders_list}), 200


if __name__ == "__main__":
    app.run(debug=False)