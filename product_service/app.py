from flask import Flask, jsonify, request
import json
import os

app = Flask(__name__)

DATA_FILE = "products.json"


# -----------------------------
# Utility Functions
# -----------------------------

def load_products():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_products(products):
    with open(DATA_FILE, "w") as f:
        json.dump(products, f, indent=4)


# -----------------------------
# Health Check
# -----------------------------

@app.route("/health")
def health():
    return jsonify({"status": "UP"})


# -----------------------------
# Get All Products
# -----------------------------

@app.route("/products", methods=["GET"])
def get_products():
    return jsonify(load_products())


# -----------------------------
# Get Product By ID
# -----------------------------

@app.route("/products/<int:product_id>", methods=["GET"])
def get_product(product_id):

    products = load_products()

    for product in products:
        if product["id"] == product_id:
            return jsonify(product)

    return jsonify({"message": "Product Not Found"}), 404


# -----------------------------
# Add Product
# -----------------------------

@app.route("/products", methods=["POST"])
def add_product():

    products = load_products()

    data = request.json

    new_product = {
        "id": len(products) + 1,
        "name": data["name"],
        "price": data["price"],
        "stock": data["stock"]
    }

    products.append(new_product)

    save_products(products)

    return jsonify({
        "message": "Product Added",
        "product": new_product
    }), 201


# -----------------------------
# Update Product
# -----------------------------

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):

    products = load_products()

    data = request.json

    for product in products:

        if product["id"] == product_id:

            product["name"] = data["name"]
            product["price"] = data["price"]
            product["stock"] = data["stock"]

            save_products(products)

            return jsonify(product)

    return jsonify({"message": "Product Not Found"}), 404


# -----------------------------
# Delete Product
# -----------------------------

@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):

    products = load_products()

    for product in products:

        if product["id"] == product_id:

            products.remove(product)

            save_products(products)

            return jsonify({"message": "Product Deleted"})

    return jsonify({"message": "Product Not Found"}), 404


# -----------------------------
# Reduce Stock
# -----------------------------

@app.route("/products/<int:product_id>/reduce-stock", methods=["PUT"])
def reduce_stock(product_id):

    products = load_products()

    data = request.json

    quantity = data["quantity"]

    for product in products:

        if product["id"] == product_id:

            if product["stock"] < quantity:
                return jsonify({
                    "message": "Insufficient Stock"
                }), 400

            product["stock"] -= quantity

            save_products(products)

            return jsonify({
                "message": "Stock Updated",
                "product": product
            })

    return jsonify({
        "message": "Product Not Found"
    }), 404


# -----------------------------
# Increase Stock (Optional)
# -----------------------------

@app.route("/products/<int:product_id>/add-stock", methods=["PUT"])
def add_stock(product_id):

    products = load_products()

    data = request.json

    quantity = data["quantity"]

    for product in products:

        if product["id"] == product_id:

            product["stock"] += quantity

            save_products(products)

            return jsonify({
                "message": "Stock Increased",
                "product": product
            })

    return jsonify({
        "message": "Product Not Found"
    }), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
