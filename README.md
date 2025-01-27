
# Auth module
## Authentication using jwt
## sign up both the user types: merchants and customers
## login both the types of users
## logout both types
## delete account 

# Merchant
## merchant can create product
## merchant can fetch the product he has created
## merchant can do CRUD on its products

# Customer module
## customer can fetch all the products
## customer can fetch product details
## customer can add the product to cart
## customer can remove the products from the cart

# Stripe integration
### we assume that in this project, all the payments will go to a single bank account.
## customer can purchase the product from cart
### stripe can be integrated in 2 ways: stripe checkout and stripe elements
## use stripe checkout if: 
### 1. Ideal for simple e-commerce sites or platforms where you need a quick and secure payment solution without worrying about design or compliance.
### 2.Perfect for businesses that don't require a highly customized payment flow.

## use stripe elements if:
### 1. Suitable for businesses that need a highly customized payment experience.
### 2. Ideal for applications with complex user interfaces where the payment form must blend seamlessly.

### 3 types of keys: publishable key, secret key, webhook secret key
