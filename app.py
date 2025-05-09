import hashlib
import json
from flask import Flask, request, jsonify

app = Flask(__name__)

VERIFICATION_TOKEN = "v58RusaLjMPPUEbygX9VoEcXiXCBpLewAusgQz6vV7sOFW6Gdlhps27gqFlITq78"
ENDPOINT_URL = "https://ebay-mrae.onrender.com/ebay/account-deletion"  # URL của bạn

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
        # Cách tính toán chữ ký có thể thay đổi, tùy thuộc vào yêu cầu cụ thể từ eBay
        calculated_signature = hashlib.sha256(json.dumps(data).encode('utf-8')).hexdigest()
        
        if signature != calculated_signature:
            return jsonify({"error": "Invalid signature"}), 401
        
        # Xử lý dữ liệu thông báo xóa tài khoản từ eBay
        print("Received account deletion notice from eBay:", data)

        # Trả về phản hồi cho eBay
        return jsonify({"status": "received"}), 200

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
