from flask import Flask, request, jsonify
import jwt
import requests
import hashlib

app = Flask(__name__)

VERIFICATION_TOKEN = "v58RusaLjMPPUEbygX9VoEcXiXCBpLewAusgQz6vV7sOFW6Gdlhps27gqFlITq78"
ENDPOINT_URL = "https://ebay-mrae.onrender.com/ebay/account-deletion"

@app.route("/")
def home():
    return "Webhook is live."

@app.route("/ebay/account-deletion", methods=["GET", "POST"])
def handle_account_deletion():
    if request.method == "GET":
        # Verify endpoint setup
        challenge_code = request.args.get("challenge_code")
        if not challenge_code:
            return jsonify({"error": "Missing challenge_code"}), 400

        data = challenge_code + VERIFICATION_TOKEN + ENDPOINT_URL
        challenge_response = hashlib.sha256(data.encode("utf-8")).hexdigest()
        return jsonify({"challengeResponse": challenge_response}), 200

    elif request.method == "POST":
        signature = request.headers.get("X-eBay-Signature")
        if not signature:
            return jsonify({"error": "Missing signature"}), 401

        try:
            # Decode JWT header to extract 'kid'
            header = jwt.get_unverified_header(signature)
            kid = header.get("kid")

            # Fetch public keys from eBay
            keys_url = "https://api.ebay.com/commerce/notification/v1/public_key"
            response = requests.get(keys_url)
            public_keys = response.json().get("keys", [])

            # Find correct key
            key_obj = next((k for k in public_keys if k["kid"] == kid), None)
            if not key_obj:
                return jsonify({"error": "Public key not found"}), 401

            # Build public key
            from cryptography.hazmat.primitives.asymmetric import ec
            from cryptography.hazmat.primitives.serialization import load_pem_public_key
            import base64

            def b64url_decode(val):
                val += '=' * (-len(val) % 4)
                return base64.urlsafe_b64decode(val)

            x = int.from_bytes(b64url_decode(key_obj["x"]), "big")
            y = int.from_bytes(b64url_decode(key_obj["y"]), "big")

            public_key = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1()).public_key()

            # Verify JWT
            payload = jwt.decode(
                signature,
                public_key,
                algorithms=["ES256"],
                audience=None,
                options={"verify_aud": False}
            )

            print("Verified eBay payload:", payload)
            return jsonify({"status": "received"}), 200

        except Exception as e:
            print("Signature verification error:", e)
            return jsonify({"error": "Signature verification failed"}), 401

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
