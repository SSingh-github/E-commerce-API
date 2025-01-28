# E-Commerce Platform

An e-commerce application that supports two types of users: **Merchants** and **Customers**, with Stripe integration for payment processing.

---

## Features Overview

### **Authentication Module**
- **Authentication using JWT** for secure sessions.
- **Sign up**:
  - Supports both **Merchants** and **Customers**.
- **Login**:
  - Separate login for both user types.
- **Logout**:
  - Secure logout for both user types.
- **Account Management**:
  - Users can delete their accounts.

---

### **Merchant Module**
- Merchants can:
  - **Create products**.
  - **Fetch products** they have created.
  - Perform **CRUD operations** on their products.

---

### **Customer Module**
- Customers can:
  - **Fetch all products**.
  - **View product details**.
  - **Add products to the cart**.
  - **Remove products from the cart**.

---

### **Stripe Integration**
This project integrates Stripe for payment processing. All payments go to a **single bank account**.

#### **Stripe Payment Options**
1. **Stripe Checkout**:
   - Ideal for simple e-commerce platforms needing quick, secure payment solutions.
   - Minimal customization required.
   - Stripe handles the compliance and UI.

2. **Stripe Elements**:
   - Suitable for highly customized payment experiences.
   - Ideal for applications with complex user interfaces where the payment form must blend seamlessly.

#### **Stripe Keys Used**
- **Publishable Key**: Used on the client side for securely interacting with Stripe.
- **Secret Key**: Used on the server side for creating payments and managing customer sessions.
- **Webhook Secret Key**: Used for verifying webhook events sent by Stripe.

---

## How Payments Work
1. Customers can purchase products added to their cart.
2. The application supports:
   - **Stripe Checkout** for simple and secure payments.
   - **Stripe Elements** for customized payment flows.
3. Webhooks are used to handle post-payment processes:
   - Update the database (e.g., reduce product quantities, clear cart).
   - Store payment details securely.

---

