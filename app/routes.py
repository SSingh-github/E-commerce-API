from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from .model import Customer, Merchant
from . import db
import jwt
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/customer/signup', methods=['POST'])
def signup():
    data = request.get_json()

    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not all([name, email, password]):
        return jsonify({"message": "All fields are required"}), 400

    if Customer.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 409

    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_user = Customer(name=name, email=email, password=hashed_password)

    db.session.add(new_user)
    db.session.commit()

    # Create JWT token
    secret_key = os.getenv('SECRET_KEY')
    token = jwt.encode(
        {"id": new_user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24)},
        str(secret_key),
        algorithm="HS256"
    )

    return jsonify({"message": "Customer created successfully", "token": token}), 201

#eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6NCwiZXhwIjoxNzM3NzExODY0fQ.HsrAACsH0mLQsdjoxDD4BaZ0gmqRwxecqT4jVgSKOQI



@auth_blueprint.route('/merchant/signup', methods=['POST'])
def merchant_signup():
    data = request.get_json()

    # Ensure all required fields are provided
    if not all(field in data for field in ['name', 'email', 'business_name', 'password']):
        return jsonify({"message": "Missing required fields"}), 400

    # Check if the email is already taken
    existing_merchant = Merchant.query.filter_by(email=data['email']).first()
    if existing_merchant:
        return jsonify({"message": "Email is already registered"}), 400

    # Hash the password for storage
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

    # Create a new Merchant object
    new_merchant = Merchant(
        name=data['name'],
        email=data['email'],
        business_name=data['business_name'],
        password=hashed_password
    )

    # Add the merchant to the database
    db.session.add(new_merchant)
    db.session.commit()
    
    secret_key = os.getenv('SECRET_KEY')

    # Create JWT token
    token = jwt.encode({
        'id': new_merchant.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }, str(secret_key), algorithm='HS256')

    return jsonify({
        'message': 'Merchant registered successfully',
        'token': token
    }), 201