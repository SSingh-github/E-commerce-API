from functools import wraps
from flask import request, jsonify, g
import jwt
import os

def decode_token(token):
    """Helper function to decode a JWT token."""
    secret_key = os.getenv('SECRET_KEY')
    try:
        decoded_token = jwt.decode(token, str(secret_key), algorithms=["HS256"])
        return decoded_token
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def merchant_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ")[1]
        decoded_token = decode_token(token)

        if not decoded_token:
            return jsonify({"message": "Invalid or expired token"}), 401

        if decoded_token.get("user_type") != "merchant":
            return jsonify({"message": "Unauthorized: Merchant access required"}), 403

        # Attach the user ID to g for request context
        g.user_id = decoded_token.get("id")
        return f(*args, **kwargs)

    return decorated

def customer_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Missing or invalid Authorization header"}), 401

        token = auth_header.split(" ")[1]
        decoded_token = decode_token(token)

        if not decoded_token:
            return jsonify({"message": "Invalid or expired token"}), 401

        if decoded_token.get("user_type") != "customer":
            return jsonify({"message": "Unauthorized: Customer access required"}), 403

        # Attach the user ID to g for request context
        g.user_id = decoded_token.get("id")
        return f(*args, **kwargs)

    return decorated
