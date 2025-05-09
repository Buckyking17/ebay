from flask import Flask, request, jsonify
import hashlib
import jwt  # PyJWT
from jwt import algorithms

app = Flask(__name__)

VERIFICATION_TOKEN = "v58RusaLjMPPUEbygX9VoEcXiXCBpLewAusgQz6vV7sOFW6Gdlhps27gqFlITq78"
ENDPOINT_URL = "https://ebay-mrae.onrender.com/ebay/account-deletion"

# Public key của eBay - dạng PEM
EBAY_PUBLIC_KEY = """
-----BEGIN PUBLIC KEY-----
MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEQGZH1L7AjD7ztxzVONxvPOCjK1gFvXld
kxRU9N60u1XyP8S5fMDaMwHhRpSGV6YtWZnHeVUVnxAKzSv6tfgMYF+Tr8b/7F3V
5NRuyC+/fEo3Osu+kqTtbP79BszpkQAl
-----END PUBLIC KEY-----
"""

@app.route("/")
def home():
    return "Hello, Flask on Render!"

@app.route("/ebay/account-deletion", methods=["GET", "POST"])
def handle_account_deletion():
    if request.method == "GET":
        challenge_code = request.args.get("challenge_code")
        if not challenge_code:
            return jsonify({"error": "Missing challenge_code"}), 400

        data = challenge_code + VERIFICATION_TOKEN + ENDPOINT_URL
        challenge_response = hashlib.sha256(data.encode("utf-8")).hexdigest()
        return jsonify({"challengeResponse": challenge_response}), 200

    elif request.method == "POST":
        jwt_token = request.headers.get("X-eBay-Signature")
        if not jwt_token:
            return jsonify({"error": "Missing signature"}), 401

        try:
            decoded = jwt.decode(
                jwt_token,
                EBAY_PUBLIC_KEY,
                algorithms=["ES256"],
                options={"verify_aud": False}
            )
            print("✅ JWT verified:", decoded)
        except Exception as e:
            print("❌ JWT verification failed:", str(e))
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()
        print("📩 Received account deletion notice:", data)
        return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
