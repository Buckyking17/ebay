from flask import Flask, request, jsonify
import hashlib
import json

app = Flask(__name__)

VERIFICATION_TOKEN = "v58RusaLjMPPUEbygX9VoEcXiXCBpLewAusgQz6vV7sOFW6Gdlhps27gqFlITq78"
ENDPOINT_URL = "https://ebay-mrae.onrender.com/ebay/account-deletion"  # URL của bạn

@app.route("/")
def home():
    return "Welcome to the eBay Notification Service!", 200

def calculate_signature(data):
    # Chữ ký sẽ được tính toán từ dữ liệu JSON nhận được từ eBay.
    return hashlib.sha256(json.dumps(data).encode('utf-8')).hexdigest()

@app.route("/ebay/account-deletion", methods=["GET", "POST"])
def handle_account_deletion():
    if request.method == "GET":
        # Xử lý yêu cầu challenge từ eBay
        challenge_code = request.args.get("challenge_code")
        if not challenge_code:
            return jsonify({"error": "Missing challenge_code"}), 400
        
        # Tạo challenge response
        data = challenge_code + VERIFICATION_TOKEN + ENDPOINT_URL
        challenge_response = hashlib.sha256(data.encode("utf-8")).hexdigest()

        return jsonify({"challengeResponse": challenge_response}), 200

    elif request.method == "POST":
        # Kiểm tra chữ ký trong header X-EBAY-SIGNATURE
        signature = request.headers.get("X-EBAY-SIGNATURE")
        if not signature:
            return jsonify({"error": "Missing X-EBAY-SIGNATURE"}), 401
        
        # Lấy dữ liệu từ yêu cầu
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing data in POST request"}), 400
        
        # Tính toán chữ ký từ dữ liệu và so sánh với chữ ký nhận được
        calculated_signature = calculate_signature(data)
        
        # In ra để debug chữ ký nhận được và chữ ký tính toán
        print(f"Received signature: {signature}")
        print(f"Calculated signature: {calculated_signature}")
        
        if signature != calculated_signature:
            return jsonify({"error": "Invalid signature"}), 401
        
        # Xử lý dữ liệu thông báo xóa tài khoản từ eBay
        print("Received account deletion notice from eBay:", data)

        # Trả về phản hồi cho eBay
        return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
