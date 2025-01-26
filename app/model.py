from . import db

class Customer(db.Model):
    __tablename__ = 'customers'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Customer {self.email}>"

class Merchant(db.Model):
    __tablename__ = 'merchants'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    business_name = db.Column(db.String(200), nullable=False)
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f"<Merchant {self.name}>"

class Product(db.Model):
    __tablename__ = 'Product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    image = db.Column(db.String(300), nullable=True) 
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Integer, nullable=False)
    merchant_id = db.Column(db.Integer, db.ForeignKey('merchants.id'), nullable=False)
    description = db.Column(db.Text, nullable=True)

    merchant = db.relationship('Merchant', backref=db.backref('products', lazy=True))

    def __repr__(self):
        return f"<Product {self.name}>"
    

class Cart(db.Model):
    __tablename__ = 'carts'

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'), nullable=False)
    product_ids = db.Column(db.String(500), nullable=True) 
    total_price = db.Column(db.Integer, nullable=False, default=0)

    customer = db.relationship('Customer', backref=db.backref('carts', lazy=True))

    def __repr__(self):
        return f"<Cart id={self.id} customer_id={self.customer_id} total_price={self.total_price} product_ids={self.product_ids}>"
