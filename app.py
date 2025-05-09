from flask import Flask, request, jsonify
import hashlib
import requests
import jwt
import json

app = Flask(__name__)

VERIFICATION_TOKEN = "v58RusaLjMPPUEbygX9VoEcXiXCBpLewAusgQz6vV7sOFW6Gdlhps27gqFlITq78"
ENDPOINT_URL = "https://ebay-mrae.onrender.com/ebay/account-deletion"
EBAY_JWKS_URL = "https://api.ebay.com/commerce/notification/v1/public_key"

@app.route("/")
def home():
    return "eBay Deletion Webhook is live!"

@app.route("/ebay/account-deletion", methods=["GET", "POST"])
def handle_account_deletion():
    if request.method == "GET":
        challenge_code = request.args.get("challenge_code")
        if not challenge_code:
            return jsonify({"error": "Missing challenge_code"}), 400

        data = challenge_code + VERIFICATION_TOKEN + ENDPOINT_URL
        response_hash = hashlib.sha256(data.encode("utf-8")).hexdigest()
        return jsonify({"challengeResponse": response_hash}), 200

    elif request.method == "POST":
        signature_token = request.headers.get("X-eBay-Signature")
        if not signature_token:
            return jsonify({"error": "Missing X-eBay-Signature"}), 401

        try:
            # Lấy header từ JWT
            header = jwt.get_unverified_header(signature_token)
            kid = header.get("kid")
            if not kid:
                return jsonify({"error": "Missing 'kid'"}), 400

            # Tải public keys từ eBay
            res = requests.get(EBAY_JWKS_URL)
            res.raise_for_status()
            keys = res.json()

            public_key = None
            for key in keys:
                if key.get("kid") == kid:
                    public_key = jwt.algorithms.ECAlgorithm.from_jwk(json.dumps(key))
                    break

            if not public_key:
                return jsonify({"error": "Public key not found"}), 401

            # Xác minh JWT
            jwt.decode(
                signature_token,
                key=public_key,
                algorithms=["ES256"],
                options={"verify_aud": False}
            )

        except jwt.InvalidTokenError as e:
            print("JWT Invalid:", e)
            return jsonify({"error": "Unauthorized"}), 401
        except Exception as e:
            print("Server Error:", e)
            return jsonify({"error": "Internal Server Error"}), 500

        payload = request.get_json()
        print("✅ Account Deletion Event:", payload)
        return jsonify({"status": "received"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
