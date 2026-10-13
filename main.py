from flask import Flask, request, jsonify
import sentry_sdk

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from models import Base, Product, User, Purchase, Payment, Sales, SalesDetails
from mpesa import make_stk_push

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
            "origins": [
                "*"
            ],
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

    data = request.get_json()

    print("Registration data:", data)

    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 403

    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")

    if not full_name or not email or not password:

        return jsonify({
            "error": "Full name, email and password are required"
        }), 403

    query = select(User).where(
        User.email == email
    )

    existing_user = session.scalar(query)

    if existing_user:

        return jsonify({
            "error": "Email already exists"
        }), 403

    hashed_password = bcrypt.generate_password_hash(
        password
    ).decode("utf-8")

    new_user = User(
        full_name=full_name,
        email=email,
        password=hashed_password
    )

    session.add(new_user)

    session.commit()

    token = create_access_token(
        identity=email
    )

    return jsonify({
        "message": "User created successfully",
        "token": token
    }), 201


# =====================================================
# LOGIN
# =====================================================

@app.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 403

    email = data.get("email")
    password = data.get("password")

    if not email or not password:

        return jsonify({
            "error": "Email and password are required"
        }), 403

    query = select(User).where(
        User.email == email
    )

    user = session.scalar(query)

    if not user:

        return jsonify({
            "error": "Invalid email or password"
        }), 401

    if not bcrypt.check_password_hash(
        user.password,
        password
    ):

        return jsonify({
            "error": "Invalid email or password"
        }), 401

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

    # -----------------------------------------------
    # GET LOGGED-IN USER
    # -----------------------------------------------

    email = get_jwt_identity()

    user = session.scalar(
        select(User).where(
            User.email == email
        )
    )

    if not user:

        return jsonify({
            "error": "User not found"
        }), 404

    #if request.method == "OPTIONS":

       # return = ""
    # =================================================
    # GET PRODUCTS
    # =================================================

    if request.method == "GET":

        query = select(Product).where(
            Product.user_id == user.id
        )

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
                    product.selling_price,    

            })

        return jsonify(results), 200

    
    # -----------------------------------------------
    # CREATE PRODUCT
    # -----------------------------------------------

    data = request.get_json()
    new_product = Product(

        product_name=data["product_name"],

        selling_price=float(data["selling_price"]),

        buying_price=float(data["buying_price"]),


    )
    session.add(new_product)

    session.commit()

    session.refresh(new_product)


    return jsonify({

        "message":
            "Product added successfully",

        "product": {

            "id":
                new_product.id,

            "product_name":
                new_product.product_name,

            "buying_price":
                new_product.buying_price,

            "selling_price":
                new_product.selling_price,
                


        }

    }), 201


# =====================================================
# UPDATE PRODUCT
# =====================================================

@app.route(
    "/products/<int:product_id>",
    methods=["PUT"]
)
@jwt_required()
def update_product(product_id):

    # -----------------------------------------------
    # GET LOGGED-IN USER
    # -----------------------------------------------

    email = get_jwt_identity()

    user = session.scalar(
        select(User).where(
            User.email == email
        )
    )

    if not user:

        return jsonify({
            "error": "User not found"
        }), 404


    # -----------------------------------------------
    # FIND PRODUCT
    # -----------------------------------------------

    product = session.scalar(

        select(Product).where(

            Product.id == product_id,

            Product.user_id == user.id

        )

    )


    if not product:

        return jsonify({
            "error": "Product not found"
        }), 404


    # -----------------------------------------------
    # GET JSON
    # -----------------------------------------------

    data = request.get_json()

    if not data:

        return jsonify({
            "error": "Request body is required"
        }), 400


    product_name = data.get("product_name")

    amount = data.get("amount")


    # -----------------------------------------------
    # VALIDATE
    # -----------------------------------------------

    if not product_name or amount is None:

        return jsonify({
            "error":
                "Product name and amount are required"
        }), 400


    try:

        amount = float(amount)

    except (ValueError, TypeError):

        return jsonify({
            "error":
                "Amount must be a number"
        }), 400


    if amount < 0:

        return jsonify({
            "error":
                "Amount cannot be negative"
        }), 400


    # -----------------------------------------------
    # UPDATE PRODUCT
    # -----------------------------------------------

    product.product_name = product_name

    product.selling_price = amount


    session.commit()

    session.refresh(product)


    # -----------------------------------------------
    # RETURN UPDATED PRODUCT
    # -----------------------------------------------

    return jsonify({

        "message":
            "Product updated successfully",

        "product": {

            "id":
                product.id,

            "product_name":
                product.product_name,

            "amount":
                product.selling_price,

            

        }

    }), 200

@app.route("/stk_push", methods = ["POST"])
def stk_push(payload):

    try:
        print(payload)
        response = make_stk_push(payload)
        new_payment = Payment(sale_id=payload["sale_id"],
                              amount_paid=payload["amount_paid"],
                              phone_number=payload["phone_number"],
                              mrid=response.get("MerchantRequestID",),
                              crid=response.get("CheckoutRequestID"),
                              status="pending")
        session.add(new_payment)
        session.commit()
        return {"stk push initiated"}

    except Exception as e:
        print("stk push error")
        return {"stk_push error", e}


# =====================================================
# RUN APPLICATION
# =====================================================

if __name__ == "__main__":

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )