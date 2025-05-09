from flask import Flask, request, jsonify
import hashlib

app = Flask(__name__)

VERIFICATION_TOKEN = "v58RusaLjMPPUEbygX9VoEcXiXCBpLewAusgQz6vV7sOFW6Gdlhps27gqFlITq78"
ENDPOINT_URL = "https://ebay-mrae.onrender.com/ebay/account-deletion"  # Thay bằng URL thật của bạn

@app.route("/")
def home():
    return "Hello, Flask on Render!"

@app.route("/ebay/account-deletion", methods=["GET", "POST"])
def handle_account_deletion():
    if request.method == "GET":
        # Xác minh endpoint từ eBay
        challenge_code = request.args.get("challenge_code")
        if not challenge_code:
            return jsonify({"error": "Missing challenge_code"}), 400
        
        data = challenge_code + VERIFICATION_TOKEN + ENDPOINT_URL
        challenge_response = hashlib.sha256(data.encode("utf-8")).hexdigest()

        return jsonify({"challengeResponse": challenge_response}), 200

    elif request.method == "POST":
        # Nhận thông báo xóa tài khoản
        token = request.headers.get("X-eBay-Signature")
        if token != VERIFICATION_TOKEN:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()
        print("Received account deletion notice from eBay:", data)

        return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
