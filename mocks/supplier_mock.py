from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/supplier/product/<int:product_id>", methods=["GET"])
def supplier_product(product_id):
    products = {
        1: {
            "supplier": "SecureCart Local Supplier",
            "product": "Laptop",
            "availability": "available"
        },
        2: {
            "supplier": "SecureCart Local Supplier",
            "product": "Wireless Mouse",
            "availability": "available"
        },
        3: {
            "supplier": "SecureCart Local Supplier",
            "product": "Keyboard",
            "availability": "limited"
        }
    }

    product = products.get(product_id)

    if product is None:
        return jsonify({
            "error": "Supplier product not found"
        }), 404

    return jsonify(product), 200


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5001,
        debug=True
    )
    