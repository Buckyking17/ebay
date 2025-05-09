from flask import Flask, request, jsonify
import hashlib
import requests
import jwt
from jwt import InvalidTokenError
import json

app = Flask(__name__)

# Cấu hình
VERIFICATION_TOKEN = "v58RusaLjMPPUEbygX9VoEcXiXCBpLewAusgQz6vV7sOFW6Gdlhps27gqFlITq78"
ENDPOINT_URL = "https://ebay-mrae.onrender.com/ebay/account-deletion"
EBAY_JWKS_URL = "https://api.ebay.com/commerce/notification/v1/public_key"

@app.route("/")
def home():
    return "Hello from eBay webhook!"

@app.route("/ebay/account-deletion", methods=["GET", "POST"])
def handle_ebay_deletion():
    if request.method == "GET":
        # Xác minh endpoint từ eBay
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

        try:
            # Giải mã JWT để lấy kid
            unverified_header = jwt.get_unverified_header(signature_token)
            kid = unverified_header.get("kid")
            if not kid:
                return jsonify({"error": "Missing kid in JWT header"}), 400

            # Lấy public key từ eBay
            jwks = requests.get(EBAY_JWKS_URL).json()
            public_key = None
            for key in jwks:
                if key.get("kid") == kid:
                    public_key = jwt.algorithms.ECAlgorithm.from_jwk(json.dumps(key))
                    break

            if not public_key:
                return jsonify({"error": "Public key not found"}), 401

            # Xác minh chữ ký JWT
            decoded = jwt.decode(
                signature_token,
                key=public_key,
                algorithms=["ES256"],
                options={"verify_aud": False}
            )
            print("✅ Chữ ký hợp lệ từ eBay:", decoded)

        except InvalidTokenError as e:
            print("❌ Lỗi xác minh chữ ký:", e)
            return jsonify({"error": "Unauthorized"}), 401
        except Exception as e:
            print("❌ Lỗi xử lý:", e)
            return jsonify({"error": "Internal server error"}), 500

        # Xử lý payload
        data = request.get_json()
        print("📩 Thông báo từ eBay:", data)

        return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
