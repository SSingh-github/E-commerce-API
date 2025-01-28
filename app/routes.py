from flask import Blueprint, request, jsonify, g, redirect, render_template
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from .model import Customer, Merchant, Product, Cart
from .utils import customer_required, merchant_required
from . import db
import jwt
import datetime
import os
from dotenv import load_dotenv
import stripe

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')

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
    products = Product.query.all()
    result = [{
        "id": product.id,
        "name": product.name,
        "image": product.image,
        "quantity": product.quantity,
        "price": product.price,
        "description": product.description
    } for product in products]
    return jsonify(result), 200

@auth_blueprint.route('/customer/add_to_cart', methods=['POST'])
@customer_required
def add_product_to_cart():
    data = request.get_json()
    product_id = data.get('product_id')
    quantity = data.get('quantity', 1)

    if not product_id:
        return jsonify({"message": "Product ID is required"}), 400

    cart = Cart.query.filter_by(customer_id=g.user_id).first()
    if not cart:
        cart = Cart(customer_id=g.user_id, product_ids='', total_price=0)
        db.session.add(cart)

    if cart.product_ids and str(product_id) in cart.product_ids.split(','):
        return jsonify({"message": "Product already in cart"}), 400

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"message": "Product not found"}), 404

    if cart.product_ids:
        cart.product_ids += f",{product_id}:{quantity}"
    else:
        cart.product_ids = f"{product_id}:{quantity}"

    cart.total_price += product.price * quantity
    db.session.commit()

    return jsonify({"message": "Product added to cart", "cart": {
        "id": cart.id,
        "product_ids": cart.product_ids,
        "total_price": cart.total_price
    }}), 200


@auth_blueprint.route('/customer/list_cart_products', methods=['GET'])
@customer_required
def fetch_cart():
    cart = Cart.query.filter_by(customer_id=g.user_id).first()
    if not cart:
        return jsonify({"message": "Cart not found"}), 404

    product_details = []
    for item in cart.product_ids.split(','):
        parts_of_item = item.split(':')
        if len(parts_of_item) > 1:
            product_id = parts_of_item[0]
            quantity = parts_of_item[1]
            product = Product.query.get(product_id)
            if product:
                product_details.append({
                    "id": product.id,
                    "name": product.name,
                    "image": product.image,
                    "quantity": int(quantity),
                    "price": product.price,
                    "description": product.description
                })

    return jsonify({
        "cart": {
            "id": cart.id,
            "product_ids": cart.product_ids,
            "total_price": cart.total_price,
            "products": product_details
        }
    }), 200


@auth_blueprint.route('/customer/delete_product_cart/<int:product_id>', methods=['DELETE'])
@customer_required
def delete_cart_product(product_id):
    cart = Cart.query.filter_by(customer_id=g.user_id).first()
    if not cart:
        return jsonify({"message": "Cart not found"}), 404

    product_to_remove = None
    product_price = 0
    product_ids = cart.product_ids.split(',')
    updated_product_ids = []
    for item in product_ids:
        pid, quantity = item.split(':')
        if int(pid) == product_id:
            product_to_remove = item
            product_price = Product.query.get(pid).price
        else:
            updated_product_ids.append(item)

    if not product_to_remove:
        return jsonify({"message": "Product not found in cart"}), 404

    cart.product_ids = ','.join(updated_product_ids)
    cart.total_price -= product_price * int(quantity)
    db.session.commit()

    return jsonify({"message": "Product removed from cart", "cart": {
        "id": cart.id,
        "product_ids": cart.product_ids,
        "total_price": cart.total_price
    }}), 200


@auth_blueprint.route('/create-checkout-session', methods=['POST'])
@customer_required
def create_checkout_session():
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        checkout_cart = data.get('checkout_whole_cart')

        line_items = []

        if checkout_cart:
            cart = Cart.query.filter_by(customer_id=g.user_id).first()
            if not cart:
                return jsonify({"error": "Cart not found"}), 404

            for item in cart.product_ids.split(','):
                parts_of_item = item.split(':')
                if len(parts_of_item) > 1:
                    product_id = parts_of_item[0]
                    quantity = int(parts_of_item[1])
                    product = Product.query.get(product_id)
                    if not product:
                        return jsonify({"error": f"Product with ID {product_id} not found"}), 404
                    if product.quantity < quantity:
                        return jsonify({"error": f"Not enough stock for product {product.name}"}), 400

                    line_items.append({
                        'price_data': {
                            'currency': 'usd',
                            'product_data': {
                                'name': product.name,
                                #'images': [product.image] if product.image else [],
                            },
                            'unit_amount': int(product.price * 100),
                        },
                        'quantity': quantity,
                    })
        else:
            if not product_id or not quantity:
                return jsonify({"error": "Product ID and quantity are required"}), 400

            product = Product.query.get(product_id)
            if not product:
                return jsonify({"error": f"Product with ID {product_id} not found"}), 404
            if product.quantity < quantity:
                return jsonify({"error": f"Not enough stock for product {product.name}"}), 400

            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': product.name,
                        #'images': [product.image] if product.image else [],
                    },
                    'unit_amount': int(product.price * 100),
                },
                'quantity': quantity,
            })

        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url='https://2156-38-183-44-137.ngrok-free.app/success',
            cancel_url='https://2156-38-183-44-137.ngrok-free.app/cancel',
            metadata={
                'customer_id': g.user_id  
        }
)


        return jsonify({"url": checkout_session.url}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@auth_blueprint.route('/success')
def success():
    return render_template('success.html')

@auth_blueprint.route('/cancel')
def cancel():
    return render_template('cancel.html')

    # implement webhooks
    # in the success case, we will first get the user id, then we will check the product ids which the user purchased and in
    # what quantity. We will update the quantity of those products in the products table. We will store the payment in the
    # payment table. We will clear the cart for that user. Because we assume that, the user can only purchase what is in its cart.

endpoint_secret = os.getenv('STRIPE_WEBHOOK_SECRET_KEY')
@auth_blueprint.route('/webhook', methods=['POST'])
def stripe_webhook():
    event = None
    payload = request.get_data(as_text=True)

    if endpoint_secret:
        # Only verify the event if there is an endpoint secret defined
        # Otherwise use the basic event deserialized with json
        sig_header = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except stripe.error.SignatureVerificationError as e:
            print('⚠️  Webhook signature verification failed.' + str(e))
            return jsonify(success=False)

    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']  # contains a stripe checkout session
        print(f"Payment was successful for session {session['id']}")
        print("################################\n#########################\n##################")

        # Do something with the session (like updating the order status)
    elif event and event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']  # contains a stripe.PaymentIntent
        print('Payment for {} succeeded'.format(payment_intent['amount']))
        # Then define and call a method to handle the successful payment intent.
        # handle_payment_intent_succeeded(payment_intent)
    elif event['type'] == 'payment_method.attached':
        payment_method = event['data']['object']  # contains a stripe.PaymentMethod
        # Then define and call a method to handle the successful attachment of a PaymentMethod.
        # handle_payment_method_attached(payment_method)
    else:
        # Unexpected event type
        print('Unhandled event type {}'.format(event['type']))

    return jsonify(success=True)

