from flask import Flask, jsonify, request

app = Flask(__name__)

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
    return "Welcome to TPT E-commerce API!"



@app.route("/api/products", methods=["GET"])
def get_products():
    return jsonify(products)



@app.route("/api/products/<int:product_id>", methods=["GET"])
def get_product(product_id):
    for product in products:
        if product["id"] == product_id:
            return jsonify(product)

    return jsonify({"message": "Product not found"}), 404


@app.route("/api/cart", methods=["POST"])
def add_to_cart():
    data = request.get_json()

    if not data or "product_id" not in data:
        return jsonify({"message": "product_id is required"}), 400

    product_id = data["product_id"]
    quantity = data.get("quantity", 1)

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


@app.route("/api/cart/<int:product_id>", methods=["PUT","DELETE"])
def update_cart(product_id):
    if request.method == "DELETE":
        for item in cart:
            if item["product_id"] == product_id:
                cart.remove(item)

                return jsonify({
                    "message": "Product removed from cart successfully",
                    "cart": cart
                })

        return jsonify({"message": "Product not found in cart"}), 404
    data = request.get_json()

    if not data or "quantity" not in data:
        return jsonify({"message": "quantity is required"}), 400

    quantity = data["quantity"]

    for item in cart:
        if item["product_id"] == product_id:
            item["quantity"] = quantity

            return jsonify({
                "message": "Cart quantity updated successfully",
                "cart": cart
            })

    return jsonify({"message": "Product not found in cart"}), 404


@app.route("/api/products", methods=["POST"])
def add_product():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data provided"}), 400

    if "name" not in data or "price" not in data or "category" not in data:
        return jsonify({
            "message": "Name, price and category are required"
        }), 400

    new_id = max(product["id"] for product in products) + 1

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

            if "name" in data:
                product["name"] = data["name"]

            if "price" in data:
                product["price"] = data["price"]

            if "category" in data:
                product["category"] = data["category"]

            return jsonify({
                "message": "Product updated successfully",
                "product": product
            })

    return jsonify({"message": "Product not found"}), 404

if __name__ == "__main__":
    app.run(debug=False)
