from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .model import User
from . import db
import jwt
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not all([name, email, password]):
        return jsonify({"message": "All fields are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 409

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = User(name=name, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    # Create JWT token
    secret_key = os.getenv('SECRET_KEY')
    token = jwt.encode(
        {"id": new_user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
        str(secret_key),
        algorithm="HS256"
    )

    return jsonify({"message": "User created successfully", "token": token}), 201

#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NCwiZXhwIjoxNzM3NzExODY0fQ.HsrAACsH0mLQsdjoxDD4BaZ0gmqRwxecqT4jVgSKOQI