from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFICATION_TOKEN = "my-ebay-deletion-token-123"

@app.route("/")
def home():
    return "Hello, Flask on Render!"

@app.route("/ebay/account-deletion", methods=["POST"])
def handle_account_deletion():
    token = request.headers.get("X-eBay-Signature")

    if token != VERIFICATION_TOKEN:
        return jsonify({"error": "Unauthorized"}), 401

    data = request.get_json()
    print("Received account deletion notice from eBay:", data)

    return jsonify({"status": "received"}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
