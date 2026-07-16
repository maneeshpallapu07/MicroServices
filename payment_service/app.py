from flask import Flask, jsonify, request
import json
import os
import random

app = Flask(__name__)

DATA_FILE = "payments.json"


def load_payments():
    if not os.path.exists(DATA_FILE):
        return []

    with open(DATA_FILE, "r") as f:
        return json.load(f)


def save_payments(payments):
    with open(DATA_FILE, "w") as f:
        json.dump(payments, f, indent=4)


@app.route("/health")
def health():
    return jsonify({"status":"UP"})


@app.route("/payments", methods=["GET"])
def get_payments():
    return jsonify(load_payments())


@app.route("/pay", methods=["POST"])
def pay():

    payments = load_payments()

    data = request.json

    payment = {

        "paymentId": len(payments)+1,
        "orderId": data["orderId"],
        "amount": data["amount"],
        "status": "SUCCESS",
        "transactionId": random.randint(100000,999999)

    }

    payments.append(payment)

    save_payments(payments)

    return jsonify(payment),201


if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5004)
