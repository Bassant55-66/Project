from flask import Flask, jsonify

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


if __name__ == "__main__":
    app.run(debug=True)
