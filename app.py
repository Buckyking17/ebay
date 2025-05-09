from flask import Flask, request, jsonify
import hashlib
import jwt  # PyJWT
import json

app = Flask(__name__)

# Thay bằng token thật bạn đã đăng ký trên eBay Developer Portal
VERIFICATION_TOKEN = "v58RusaLjMPPUEbygX9VoEcXiXCBpLewAusgQz6vV7sOFW6Gdlhps27gqFlITq78"

# Đường dẫn endpoint mà bạn đã đăng ký trên eBay
ENDPOINT_URL = "https://ebay-mrae.onrender.com/ebay/account-deletion"

@app.route("/")
def home():
    return "eBay Account Deletion Endpoint is live."

@app.route("/ebay/account-deletion", methods=["GET", "POST"])
def handle_account_deletion():
    if request.method == "GET":
        # eBay gửi challenge_code để xác minh endpoint
        challenge_code = request.args.get("challenge_code")
        if not challenge_code:
            return jsonify({"error": "Missing challenge_code"}), 400

        # Tạo challengeResponse theo tài liệu của eBay
        data = challenge_code + VERIFICATION_TOKEN + ENDPOINT_URL
        challenge_response = hashlib.sha256(data.encode("utf-8")).hexdigest()

        return jsonify({"challengeResponse": challenge_response}), 200

    elif request.method == "POST":
        # eBay gửi thông báo xoá tài khoản qua POST, cần xác thực chữ ký
        signature = request.headers.get("X-eBay-Signature")
        body = request.get_data(as_text=True)

        if not signature:
            return jsonify({"error": "Missing X-eBay-Signature"}), 401

        try:
            decoded = jwt.decode(
                signature,
                algorithms=["ES256"],
                options={"verify_signature": False},  # không verify để debug thôi
            )
            print("Decoded JWT (not verified):", decoded)
        except Exception as e:
            print("JWT Decode failed:", e)
            return jsonify({"error": "Invalid JWT"}), 401

        # Bạn có thể log hoặc xử lý dữ liệu xóa tài khoản tại đây
        try:
            data = json.loads(body)
            print("eBay deletion request received:", data)
        except Exception as e:
            print("Invalid JSON body:", e)
            return jsonify({"error": "Invalid request body"}), 400

        return jsonify({"status": "received"}), 200

    return jsonify({"error": "Invalid method"}), 405
