# Simple E-commerce API

![Badge](https://img.shields.io/badge/python-3.8%2B-blue)
![Badge](https://img.shields.io/badge/flask-2.0%2B-green)
![Badge](https://img.shields.io/badge/mysql-database-orange)
![Badge](https://img.shields.io/badge/stripe-payment%20gateway-purple)

A Flask-based e-commerce API that handles user authentication, product management, shopping cart functionality, and payment gateway integration using Stripe. This project demonstrates complex backend logic, including JWT authentication, database interactions, and external service integration.

---

## About the Project

### Problem Solved
Building a scalable and secure e-commerce platform requires handling multiple responsibilities, such as user authentication, product management, shopping cart logic, and payment processing. This project solves these challenges by:
1. **User Authentication**: Using JWT (JSON Web Tokens) to securely manage user sessions.
2. **Product Management**: Allowing admins to create, update, and list products.
3. **Shopping Cart Logic**: Enabling users to add/remove products and manage their carts.
4. **Payment Integration**: Integrating with Stripe for seamless payment processing.

---

## Features
- **JWT Authentication**: Secure user login and session management.
- **Product Management**: Create, update, and list products in the database.
- **Shopping Cart**: Add/remove products and manage cart items.
- **Payment Gateway**: Integrate with Stripe for secure payment processing.
- **RESTful API**: Provides endpoints for all e-commerce functionalities.

---

## Technologies and Skills Used
- **Backend Framework**: Flask (Python)
- **Database**: MySQL (with SQLAlchemy for ORM)
- **Authentication**: JWT (JSON Web Tokens)
- **Payment Gateway**: Stripe (Checkout API)
- **Other Tools**: Git, Docker (optional for containerization)

---

## How It Works
1. **User Authentication**: Users register/login to receive a JWT for accessing protected endpoints.
2. **Product Management**: Admins can create, update, and list products stored in a MySQL database.
3. **Shopping Cart**: Users can add/remove products to/from their cart, which is stored in the database.
4. **Payment Processing**: Users can checkout their cart, and the API integrates with Stripe to handle payments.

---

## Steps to Clone and Run the Project

### Prerequisites
- Python 3.8+
- MySQL server (locally or via Docker)
- Stripe API key (sign up [here](https://stripe.com))

### Step 1: Clone the Repository
```bash
git clone https://github.com/yourusername/simple-ecommerce-api.git
cd simple-ecommerce-api
```
