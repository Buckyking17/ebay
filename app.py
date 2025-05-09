import hashlib
import hmac
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

# Kiểm tra lại token xác thực và endpoint
VERIFICATION_TOKEN = "v58RusaLjMPPUEbygX9VoEcXiXCBpLewAusgQz6vV7sOFW6Gdlhps27gqFlITq78"
ENDPOINT_URL = "https://ebay-mrae.onrender.com/ebay/account-deletion"  # Đảm bảo URL này chính xác

# Function to validate the signature
def validate_signature(request_body, signature):
    # Tạo string để so sánh chữ ký
    secret_key = VERIFICATION_TOKEN.encode('utf-8')  # Sử dụng token của bạn làm key
    message = request_body.encode('utf-8')  # Body của yêu cầu POST từ eBay

    # Tính toán HMAC-SHA256
    calculated_signature = hmac.new(secret_key, message, hashlib.sha256).hexdigest()
    return calculated_signature == signature

@app.route("/ebay/account-deletion", methods=["POST"])
def handle_account_deletion():
    # Lấy giá trị của header X-eBay-Signature
    signature = request.headers.get("X-eBay-Signature")
    if not signature:
        return jsonify({"error": "Missing X-eBay-Signature header"}), 400

    # Lấy body của yêu cầu
    request_body = request.get_data(as_text=True)

    # Xác minh chữ ký
    if not validate_signature(request_body, signature):
        return jsonify({"error": "Unauthorized, signature mismatch"}), 401

    # Nhận dữ liệu thông báo
    data = request.get_json()
    print("Received account deletion notice from eBay:", data)

    return jsonify({"status": "received"}), 200

@app.route("/")
def home():
    return "Hello, Flask on Render!"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
