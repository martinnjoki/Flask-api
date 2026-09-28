from flask import Flask, request, jsonify
import sentry_sdk

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import Base, Product, User, Purchase, Payments, Sales, SalesDetails

from flask_bcrypt import Bcrypt

from flask_jwt_extended import (
    JWTManager,
    jwt_required,
    create_access_token,
    get_jwt_identity
)

from flask_cors import CORS


# =====================================================
# SENTRY
# =====================================================

sentry_sdk.init(
    dsn="https://3648ed24f28f85f3c1e9ff11a7ba8893@o4512046005223424.ingest.de.sentry.io/4512046187348048",
    send_default_pii=True
)


# =====================================================
# FLASK APPLICATION
# =====================================================

app = Flask(__name__)


# =====================================================
# CORS
# =====================================================

CORS(
    app,
    resources={
        r"/*": {
            "origins": "http://127.0.0.1:5500",
            "allow_headers": [
                "Content-Type",
                "Authorization"
            ]
        }
    }
)


# =====================================================
# JWT
# =====================================================

app.config["JWT_SECRET_KEY"] = "marto1234"

jwt = JWTManager(app)


# =====================================================
# BCRYPT
# =====================================================

bcrypt = Bcrypt(app)


# =====================================================
# DATABASE
# =====================================================

engine = create_engine(
    "sqlite:///./flask_duka_api.db",
    echo=True
)

Base.metadata.create_all(engine)

session = Session(engine)


# =====================================================
# HOME
# =====================================================

@app.route("/", methods=["GET"])
def home():

    return jsonify({
        "Flask API": "Version 1"
    }), 200


# =====================================================
# REGISTER
# =====================================================

@app.route("/register", methods=["POST"])
def register():

    # Get JSON data
    data = request.get_json()

    print("Registration data:", data)

    # Check whether data was sent
    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 403


    # Get values
    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")


    # Check required fields
    if not full_name or not email or not password:

        return jsonify({
            "error": "Full name, email and password are required"
        }), 403


    # Check whether email already exists
    query = select(User).where(
        User.email == email
    )

    existing_user = session.scalar(query)


    if existing_user:

        return jsonify({
            "error": "Email already exists"
        }), 403


    # Hash password
    hashed_password = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")


    # Create new user
    new_user = User(
        full_name=full_name,
        email=email,
        password=hashed_password
    )


    # Save user
    session.add(new_user)
    session.commit()


    # Create JWT token
    token = create_access_token(
        identity=email
    )


    # Return response
    return jsonify({
        "message": "User created successfully",
        "token": token
    }), 201


# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["POST"])
def login():

    # Get JSON data
    data = request.get_json()


    # Check data
    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 403


    # Get values
    email = data.get("email")
    password = data.get("password")


    # Check fields
    if not email or not password:

        return jsonify({
            "error": "Email and password are required"
        }), 403


    # Find user
    query = select(User).where(
        User.email == email
    )

    user = session.scalar(query)


    # Check user
    if not user:

        return jsonify({
            "error": "Invalid email or password"
        }), 401


    # Check password
    if not bcrypt.check_password_hash(
        user.password,
        password
    ):

        return jsonify({
            "error": "Invalid email or password"
        }), 401


    # Create token
    token = create_access_token(
        identity=email
    )


    return jsonify({
        "message": "Logged in successfully",
        "token": token
    }), 200


# =====================================================
# PRODUCTS
# =====================================================

@app.route("/products", methods=["GET", "POST"])
@jwt_required()
def products():

    # Get logged-in user's email
    email = get_jwt_identity()


    # Find logged-in user
    user = session.scalar(
        select(User).where(
            User.email == email
        )
    )


    # =================================================
    # GET PRODUCTS
    # =================================================

    if request.method == "GET":

        query = select(Product)

        products_list = session.scalars(query)

        results = []


        for product in products_list:

            results.append({

                "id": product.id,

                "product_name":
                    product.product_name,

                "buying_price":
                    product.buying_price,

                "selling_price":
                    product.selling_price

            })


        return jsonify(results), 200


    # =================================================
    # ADD PRODUCT
    # =================================================

    data = request.get_json()


    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 403


    product_name = data.get("product_name")
    buying_price = data.get("buying_price")
    selling_price = data.get("selling_price")


    if not product_name or not buying_price or not selling_price:

        return jsonify({
            "error": "Ensure all fields are set"
        }), 403


    new_product = Product(

        user_id=user.id,

        product_name=product_name,

        buying_price=float(
            buying_price
        ),

        selling_price=float(
            selling_price
        )
    )


    session.add(new_product)

    session.commit()


    return jsonify({
        "message": "Product added successfully"
    }), 201


# =====================================================
# PURCHASES
# =====================================================

@app.route("/purchases", methods=["GET", "POST"])
@jwt_required()
def purchases():

    # Get logged-in user's email
    email = get_jwt_identity()


    # Find logged-in user
    user = session.scalar(
        select(User).where(
            User.email == email
        )
    )


    # =================================================
    # GET PURCHASES
    # =================================================

    if request.method == "GET":

        query = select(Purchase)

        purchases_list = session.scalars(query)

        results = []


        for purchase in purchases_list:

            results.append({

                "id": purchase.id,

                "product_id":
                    purchase.product_id,

                "quantity":
                    purchase.quantity,

                "buying_price":
                    purchase.buying_price,

                "total_price":
                    purchase.total_price

            })


        return jsonify(results), 200


    # =================================================
    # ADD PURCHASE
    # =================================================

    data = request.get_json()


    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 403


    product_id = data.get("product_id")
    quantity = data.get("quantity")
    buying_price = data.get("buying_price")


    if not product_id or not quantity or not buying_price:

        return jsonify({
            "error": "Ensure all fields are set"
        }), 403


    # Calculate total
    total_price = (
        float(quantity)
        *
        float(buying_price)
    )


    # Create purchase
    new_purchase = Purchase(

        user_id=user.id,

        product_id=product_id,

        quantity=int(quantity),

        buying_price=float(
            buying_price
        ),

        total_price=total_price
    )


    session.add(new_purchase)

    session.commit()


    return jsonify({
        "message": "Purchase added successfully"
    }), 201


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )