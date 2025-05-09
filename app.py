from flask import Flask, request, jsonify
import hashlib
import hmac

app = Flask(__name__)

# Thay chuỗi này bằng verification token thực của bạn (32-80 ký tự)
VERIFICATION_TOKEN = "v58RusaLjMPPUEbygX9VoEcXiXCBpLewAusgQz6vV7sOFW6Gdlhps27gqFlITq78"

# Đường dẫn endpoint đúng như đã đăng ký với eBay
ENDPOINT_URL = "https://ebay-mrae.onrender.com/ebay/account-deletion"

@app.route("/")
def home():
    return "Hello, Flask on Render!"

@app.route("/ebay/account-deletion", methods=["GET", "POST"])
def handle_account_deletion():
    if request.method == "GET":
        # Xử lý yêu cầu xác minh endpoint từ eBay
        challenge_code = request.args.get("challenge_code")
        if not challenge_code:
            return jsonify({"error": "Missing challenge_code"}), 400

        data = challenge_code + VERIFICATION_TOKEN + ENDPOINT_URL
        challenge_response = hashlib.sha256(data.encode("utf-8")).hexdigest()

        return jsonify({"challengeResponse": challenge_response}), 200

    elif request.method == "POST":
        # Nhận thông báo xóa tài khoản (eBay gửi POST với chữ ký HMAC)
        signature = request.headers.get("X-eBay-Signature")
        if not signature:
            return jsonify({"error": "Missing signature"}), 401

        # Lấy payload thô để tính HMAC SHA256
        payload = request.get_data()
        computed_signature = hmac.new(
            VERIFICATION_TOKEN.encode("utf-8"),
            payload,
            hashlib.sha256
        ).hexdigest()

        # So sánh chữ ký
        if signature.lower() != computed_signature.lower():
            print("Signature mismatch!")
            print("From eBay:", signature)
            print("Computed :", computed_signature)
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()
        print("Received account deletion notice from eBay:", data)

        return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
