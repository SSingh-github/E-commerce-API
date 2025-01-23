from flask import request, jsonify
import jwt
import os

def token_required(f):
    def decorated(*args, **kwargs):
        token = request.headers.get('x-access-token')
        if not token:
            return jsonify({"message": "Token is missing"}), 401
        try:
            secret_key = os.getenv('SECRET_KEY')
            data = jwt.decode(token, secret_key, algorithms=["HS256"])
        except:
            return jsonify({"message": "Token is invalid"}), 401
        return f(*args, **kwargs)
    return decorated
