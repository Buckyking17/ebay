from flask import Flask, request, jsonify
import hashlib
import json

app = Flask(__name__)

# Mã xác minh (đảm bảo có độ dài từ 32 đến 80 ký tự và theo đúng định dạng yêu cầu)
VERIFICATION_TOKEN = "v58RusaLjMPPUEbygX9VoEcXiXCBpLewAusgQz6vV7sOFW6Gdlhps27gqFlITq78"

# URL endpoint nơi các thông báo sẽ được gửi đến
ENDPOINT_URL = "https://ebay-mrae.onrender.com/ebay/account-deletion"

@app.route("/")
def home():
    return "Chào mừng đến với dịch vụ thông báo eBay!", 200

@app.route("/ebay/account-deletion", methods=["GET", "POST"])
def handle_account_deletion():
    if request.method == "GET":
        # eBay gửi challenge_code trong tham số truy vấn để xác minh
        challenge_code = request.args.get("challenge_code")
        if not challenge_code:
            return jsonify({"error": "Thiếu challenge_code"}), 400
        
        # Tạo challenge response bằng cách nối challenge_code, verificationToken và endpoint URL
        data_to_hash = challenge_code + VERIFICATION_TOKEN + ENDPOINT_URL
        
        # Mã hóa chuỗi đã nối bằng SHA256
        challenge_response = hashlib.sha256(data_to_hash.encode("utf-8")).hexdigest()

        # Trả về challenge response dưới dạng JSON với đúng header content-type
        return jsonify({"challengeResponse": challenge_response}), 200

    elif request.method == "POST":
        # Xử lý yêu cầu POST thông báo xóa tài khoản từ eBay (không liên quan đến xác minh challenge)
        signature = request.headers.get("X-EBAY-SIGNATURE")
        if not signature:
            return jsonify({"error": "Thiếu X-EBAY-SIGNATURE"}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({"error": "Thiếu dữ liệu trong yêu cầu POST"}), 400
        
        # Trong trường hợp thực tế, ở đây bạn sẽ kiểm tra chữ ký của dữ liệu nhận được
        # Ví dụ này sẽ chỉ in ra dữ liệu
        print("Nhận được thông báo xóa tài khoản từ eBay:", data)

        return jsonify({"status": "received"}), 200


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
