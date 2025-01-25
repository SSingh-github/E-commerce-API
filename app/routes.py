from flask import Blueprint, request, jsonify, g
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from .model import Customer, Merchant, Product
from .utils import customer_required, merchant_required
from . import db
import jwt
import datetime
import os
from dotenv import load_dotenv

load_dotenv()

auth_blueprint = Blueprint('auth', __name__)
ASSETS_FOLDER = 'assets'
os.makedirs(ASSETS_FOLDER, exist_ok=True)

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

    secret_key = os.getenv('SECRET_KEY')
    token = jwt.encode(
        {"id": new_user.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24), "user_type": "customer"},
        str(secret_key),
        algorithm="HS256"
    )

    return jsonify({"message": "Customer created successfully", "token": token}), 201




@auth_blueprint.route('/merchant/signup', methods=['POST'])
def merchant_signup():
    data = request.get_json()

    if not all(field in data for field in ['name', 'email', 'business_name', 'password']):
        return jsonify({"message": "Missing required fields"}), 400

    existing_merchant = Merchant.query.filter_by(email=data['email']).first()
    if existing_merchant:
        return jsonify({"message": "Email is already registered"}), 400

    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')

    new_merchant = Merchant(
        name=data['name'],
        email=data['email'],
        business_name=data['business_name'],
        password=hashed_password
    )

    db.session.add(new_merchant)
    db.session.commit()
    
    secret_key = os.getenv('SECRET_KEY')

    token = jwt.encode({
        'id': new_merchant.id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    , "user_type": "merchant"}, str(secret_key), algorithm='HS256')

    return jsonify({
        'message': 'Merchant registered successfully',
        'token': token
    }), 201


@auth_blueprint.route('/customer/login', methods=['POST'])
def customer_login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({"message": "Email and password are required"}), 400

    customer = Customer.query.filter_by(email=email).first()
    if not customer or not check_password_hash(customer.password, password):
        return jsonify({"message": "Invalid email or password"}), 401

    secret_key = os.getenv('SECRET_KEY')
    token = jwt.encode(
        {"id": customer.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24),"user_type": "customer"},
        str(secret_key),
        algorithm="HS256"
    )

    return jsonify({"message": "Login successful", "token": token}), 200


@auth_blueprint.route('/merchant/login', methods=['POST'])
def merchant_login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    if not all([email, password]):
        return jsonify({"message": "Email and password are required"}), 400

    merchant = Merchant.query.filter_by(email=email).first()
    if not merchant or not check_password_hash(merchant.password, password):
        return jsonify({"message": "Invalid email or password"}), 401

    secret_key = os.getenv('SECRET_KEY')
    token = jwt.encode(
        {"id": merchant.id, "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=24), "user_type": "merchant"},
        str(secret_key),
        algorithm="HS256"
    )

    return jsonify({"message": "Login successful", "token": token}), 200


@auth_blueprint.route('/customer/delete', methods=['DELETE'])
@customer_required
def delete_customer_account():
    customer = Customer.query.get(g.user_id)

    if not customer:
        return jsonify({"message": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": "Customer account deleted successfully"}), 200


@auth_blueprint.route('/merchant/delete', methods=['DELETE'])
@merchant_required
def delete_merchant_account():
    merchant = Merchant.query.get(g.user_id)

    if not merchant:
        return jsonify({"message": "Merchant not found"}), 404

    db.session.delete(merchant)
    db.session.commit()

    return jsonify({"message": "Merchant account deleted successfully"}), 200



@auth_blueprint.route('/merchant/add_product', methods=['POST'])
@merchant_required
def add_product():
    data = request.form
    file = request.files.get('image')

    name = data.get('name')
    description = data.get('description')
    quantity = data.get('quantity')
    price = data.get('price')

    if not all([name, description, quantity, file, price]):
        return jsonify({"message": "All fields are required, including an image."}), 400

    try:
        quantity = int(quantity)
    except ValueError:
        return jsonify({"message": "Quantity must be an integer."}), 400
    
    try:
        price = int(price)
    except ValueError:
        return jsonify({"message": "Price must be an integer."}), 400

    filename = secure_filename(file.filename)
    file_path = os.path.join(ASSETS_FOLDER, filename)
    file.save(file_path)

    product = Product(
        name=name,
        description=description,
        quantity=quantity,
        image=file_path,
        merchant_id=g.user_id,
        price=price
    )
    db.session.add(product)
    db.session.commit()

    return jsonify({"message": "Product added successfully", "product": {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "quantity": product.quantity,
        "image": product.image,
        "price":price
    }}), 201



@auth_blueprint.route('/merchant/list_products', methods=['GET'])
@merchant_required
def get_products():
    merchant_id = g.user_id
    products = Product.query.filter_by(merchant_id=merchant_id).all()

    product_list = [{
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "quantity": product.quantity,
        "image": product.image,
        "price":product.price
    } for product in products]

    return jsonify({"products": product_list}), 200



@auth_blueprint.route('/merchant/update_product/<int:id>', methods=['PUT'])
@merchant_required
def update_product(id):
    data = request.form
    file = request.files.get('image')

    product = Product.query.filter_by(id=id, merchant_id=g.user_id).first()
    if not product:
        return jsonify({"message": "Product not found or you do not have permission to edit it."}), 404

    name = data.get('name')
    description = data.get('description')
    quantity = data.get('quantity')
    price = data.get('price')

    if name:
        product.name = name
    if description:
        product.description = description
    if quantity:
        try:
            product.quantity = int(quantity)
        except ValueError:
            return jsonify({"message": "Quantity must be an integer."}), 400
    if price:
        try:
            product.price = int(price)
        except ValueError:
            return jsonify({"message": "Price must be an integer."}), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(ASSETS_FOLDER, filename)
        file.save(file_path)
        product.image = file_path

    db.session.commit()

    return jsonify({"message": "Product updated successfully", "product": {
        "id": product.id,
        "name": product.name,
        "description": product.description,
        "quantity": product.quantity,
        "image": product.image,
        "price": product.price
    }}), 200



@auth_blueprint.route('/merchant/delete_product/<int:id>', methods=['DELETE'])
@merchant_required
def delete_product(id):
    product = Product.query.filter_by(id=id, merchant_id=g.user_id).first()
    if not product:
        return jsonify({"message": "Product not found or you do not have permission to delete it."}), 404

    db.session.delete(product)
    db.session.commit()

    return jsonify({"message": "Product deleted successfully"}), 200


@auth_blueprint.route('/customer/list_products', methods=['GET'])
@customer_required
def fetch_products():
    """
    fetch all the products in the product table
    """
    pass


