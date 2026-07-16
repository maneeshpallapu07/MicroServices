from flask import Flask, render_template, request
import requests
import os
app = Flask(__name__)

ORDER_SERVICE = os.getenv(
    "ORDER_SERVICE_URL",
    "http://order-service:5003"
)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/place-order", methods=["POST"])
def place_order():

    user_id = request.form["userId"]
    product_id = request.form["productId"]
    quantity = request.form["quantity"]

    response = requests.post(

        f"{ORDER_SERVICE}/order",

        json={
            "userId": int(user_id),
            "productId": int(product_id),
            "quantity": int(quantity)
        }

    )

    result = response.json()

    return render_template(
        "index.html",
        result=result
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
