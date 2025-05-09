from flask import Flask, request, jsonify
import hashlib
import requests
import jwt  # PyJWT
from jwt import InvalidTokenError

app = Flask(__name__)

# Thay đổi các biến này theo cấu hình của bạn
VERIFICATION_TOKEN = "v58RusaLjMPPUEbygX9VoEcXiXCBpLewAusgQz6vV7sOFW6Gdlhps27gqFlITq78"
ENDPOINT_URL = "https://ebay-mrae.onrender.com/ebay/account-deletion"
EBAY_JWKS_URL = "https://api.ebay.com/commerce/notification/v1/public_key"

@app.route("/")
def home():
    return "Hello from eBay webhook!"

@app.route("/ebay/account-deletion", methods=["GET", "POST"])
def handle_ebay_deletion():
    if request.method == "GET":
        # eBay xác minh endpoint lần đầu
        challenge_code = request.args.get("challenge_code")
        if not challenge_code:
            return jsonify({"error": "Missing challenge_code"}), 400

        data = challenge_code + VERIFICATION_TOKEN + ENDPOINT_URL
        response_hash = hashlib.sha256(data.encode("utf-8")).hexdigest()
        return jsonify({"challengeResponse": response_hash}), 200

    elif request.method == "POST":
        # Nhận thông báo xóa tài khoản
        signature_token = request.headers.get("X-eBay-Signature")
        if not signature_token:
            return jsonify({"error": "Missing signature"}), 401

        # Lấy public key từ eBay
        try:
            jwks = requests.get(EBAY_JWKS_URL).json()
            # eBay trả về một mảng key -> chọn key phù hợp
            for key in jwks:
                try:
                    decoded = jwt.decode(
                        signature_token,
                        key=jwt.algorithms.ECAlgorithm.from_jwk(key),
                        algorithms=["ES256"],
                        options={"verify_aud": False}
                    )
                    print("✅ Chữ ký hợp lệ từ eBay:", decoded)
                    break
                except InvalidTokenError:
                    continue
            else:
                print("❌ Không tìm được public key hợp lệ.")
                return jsonify({"error": "Unauthorized"}), 401
        except Exception as e:
            print("❌ Lỗi khi lấy hoặc xác minh chữ ký:", e)
            return jsonify({"error": "Signature validation failed"}), 500

        # Nếu chữ ký hợp lệ, xử lý payload
        data = request.get_json()
        print("📩 Thông báo từ eBay:", data)

        return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
