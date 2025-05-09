from flask import Flask, request, jsonify
import hashlib
import jwt  # PyJWT
import json

app = Flask(__name__)

# Thay bằng token thật bạn đã đăng ký trên eBay Developer Portal
VERIFICATION_TOKEN = "v^1.1#i^1#I^3#r^0#f^0#p^1#t^H4sIAAAAAAAA/+VYe4hUVRif2Zes6yhWaK5ms1cLMWfm3HneuTgjsw/dzX2MzrhuK2L3cca57n15z7m7O1KwrmUEaoSGGRVCiLSihogakVSSkv0RSWESYaGpWcsulFhg2bkz6zq7iZo70ELDwHC/853v/H6/7/vOOXNBT1n5/M31m6877BOKdveAniK7na4A5WWlT00uLqostYE8B/vunrk9Jb3FVxYiTpF1djlEuqYi6OxWZBWxWWOEMg2V1TgkIVblFIhYLLCJWFMj63UDVjc0rAmaTDkbaiMUwwkBPw19AS/DBbwAEKt6K2ZSi1ChIMMxgp+nAR8UOD5IxhEyYYOKMKfiCOUF3oALkG84STMsYFiadtNMsJ1ytkIDSZpKXNyAimbhstm5Rh7Wu0PlEIIGJkGoaENscaIl1lBb15xc6MmLFR3SIYE5bKKRTzWaCJ2tnGzCuy+Dst5swhQEiBDlieZWGBmUjd0C8wDws1L7gwLvSwXCAhDFcIjnCiLlYs1QOHx3HJZFEl2prCsLVSzhzL0UJWrw66CAh56aSYiGWqf1s8zkZCklQSNC1VXHnonF41S0XoJmk6SmXZyJNc0QoSu+vNbFcKRkwgGv3xXivTQdTvmHFspFG5J51Eo1mipKlmjI2azhakhQw5HahNhAnjbEqUVtMWIpbCHK8/OCWxoGmXYrqbksmjitWnmFChHCmX28dwaGZ2NsSLyJ4XCE0QNZiSIUp+uSSI0ezNbiUPl0owiVxlhnPZ6uri53l8+tGWs9pANpT1tTY0JIQ4VUSLdi9XrOX7r3BJeUpSJAMhNJLM7oBEs3qVUCQF1LRQPekNcHhnQfCSs62voPQx5nz8iOKFSHMMGgPygGQShEp8KBUEE2m+hQkXosHJDnMi6FMzog1mVOgC6B1JmpQEMSWV8g5fUxKegSg+GUyx9OpVx8QAy66BSEAEKeF8LM/6lR7rfUE1AwIC5IrReszpc0Ap1Jre+oZppWGhrSNyxr22DiZGOifqmeDMs1bYtbw7rpR81Ai9xvN9yRfI0sEWWSZP1CCGD1euFEqNcQhuKY6CUETYdxTZaEzPhKsM8Q45yBMwkoy8QwJpIxXW8ozF5duNT9u23iwXgX7oz6j86nO7JCVsmOL1bWfEQCcLrktk4gt6ApHqvXNZLetGVek0U9Jt4SubmOK9aEZI6tJOaunO4sXTfqFNwGRJppkNu2u8W6gSW1DqiS8wwbmixDo5Uecz8riok5XobjrbELUOASN84OWzrkDzK0H4THljYhe5SuGW9bUiG24pIlD3it9oz8kx+1ZT90r/0T0Gs/XmS3g4XgCXoOqCorXlFSPKkSSRi6JS7lRtJalfx3NaC7A2Z0TjKKHrZ9MblR3FjfeK2HN4+u/G0RY3PkvWPYvRo8OvyWobyYrsh75QBm3R4ppadMd3gDIEDSzQCGptvBnNujJfS0kkf+euiXywt2oq8GOp+2L7h6c+/ZGzuWAsewk91eaivptdtmnjn3+q+z5j95flBYWt4/YwrI2EvxN33X+NXJ91fuE8ODs7ZPVCbEL99U6770733353d2Vl49VTO9qXbbFvPSG/x77ZEPz6htB5VTnZvaH/vWce3qwIHjlxybbwz2PR5b/uz3zOH1N4SX+o88Py3+8Y6Tld2fn9y0qvOF/i0X91zY2z0v/faZqovaWad0YduU+OE9ZUcO3Vx1+qeDaod/4OiLE7mXPuho2vXHR39en11XMTD1u9fOv7p1a+3UBW2ysu6K45X9Jwbn7fp0Y+eBvq/Tsy9Bh+0z5Ok7NmPR/mPb59L7tu8/ueVg9db+c79feOsH/Uq6PbNp5qSq535UVhw6PQFNi5+YiSpefrNqei6XfwOhTFbD/REAAA=="

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
    
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
