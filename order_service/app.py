from flask import Flask, jsonify, request
import json
import os
import requests

app = Flask(__name__)

DATA_FILE = "orders.json"

USER_SERVICE = os.getenv(
    "USER_SERVICE_URL",
    "http://user-service:5001"
)

PRODUCT_SERVICE = os.getenv(
    "PRODUCT_SERVICE_URL",
    "http://product-service:5002"
)

PAYMENT_SERVICE = os.getenv(
    "PAYMENT_SERVICE_URL",
    "http://payment-service:5004"
)

# ------------------------------------
# Utility Functions
# ------------------------------------

def load_orders():

    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_orders(orders):

    with open(DATA_FILE, "w") as f:
        json.dump(orders, f, indent=4)


# ------------------------------------
# Health Check
# ------------------------------------

@app.route("/health")
def health():

    return jsonify({
        "status":"UP"
    })


# ------------------------------------
# Get All Orders
# ------------------------------------

@app.route("/orders", methods=["GET"])
def get_orders():

    return jsonify(load_orders())


# ------------------------------------
# Get Order By ID
# ------------------------------------

@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):

    orders = load_orders()

    for order in orders:

        if order["orderId"] == order_id:
            return jsonify(order)

    return jsonify({
        "message":"Order Not Found"
    }),404


# ------------------------------------
# Create Order
# ------------------------------------

@app.route("/order", methods=["POST"])
def create_order():

    data = request.json

    user_id = data["userId"]
    product_id = data["productId"]
    quantity = data["quantity"]

    orders = load_orders()

    # -----------------------------
    # Validate User
    # -----------------------------

    user_response = requests.get(
        f"{USER_SERVICE}/users/{user_id}"
    )

    if user_response.status_code != 200:

        return jsonify({
            "message":"User Not Found"
        }),404

    user = user_response.json()

    # -----------------------------
    # Validate Product
    # -----------------------------

    product_response = requests.get(
        f"{PRODUCT_SERVICE}/products/{product_id}"
    )

    if product_response.status_code != 200:

        return jsonify({
            "message":"Product Not Found"
        }),404

    product = product_response.json()

    # -----------------------------
    # Check Stock
    # -----------------------------

    if product["stock"] < quantity:

        return jsonify({
            "message":"Insufficient Stock"
        }),400

    total_amount = quantity * product["price"]

    # -----------------------------
    # Call Payment Service
    # -----------------------------

    payment_response = requests.post(

        f"{PAYMENT_SERVICE}/pay",

        json={
            "orderId": len(orders)+1,
            "amount": total_amount
        }

    )

    if payment_response.status_code != 201:

        return jsonify({
            "message":"Payment Failed"
        }),500

    payment = payment_response.json()

    # -----------------------------
    # Reduce Product Stock
    # -----------------------------

    stock_response = requests.put(

        f"{PRODUCT_SERVICE}/products/{product_id}/reduce-stock",

        json={
            "quantity":quantity
        }

    )

    if stock_response.status_code != 200:

        return jsonify({
            "message":"Unable To Reduce Stock"
        }),500

    updated_product = stock_response.json()["product"]
    # -----------------------------
    # Save Order
    # -----------------------------

    new_order = {

        "orderId": len(orders) + 1,

        "user": user,

        "product": {
            "id": updated_product["id"],
            "name": updated_product["name"],
            "price": updated_product["price"]
        },

        "quantity": quantity,

        "totalAmount": total_amount,

        "payment": payment

    }

    orders.append(new_order)

    save_orders(orders)

    return jsonify({

        "message": "Order Placed Successfully",

        "order": new_order

    }),201


# ------------------------------------
# Delete Order
# ------------------------------------

@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):

    orders = load_orders()

    for order in orders:

        if order["orderId"] == order_id:

            orders.remove(order)

            save_orders(orders)

            return jsonify({
                "message":"Order Deleted"
            })

    return jsonify({
        "message":"Order Not Found"
    }),404


if __name__ == "__main__":

    app.run(host="0.0.0.0", port=5003)
