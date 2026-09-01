# it has to have a route.
# it has to have a method(POST/GET/PUT).
# It has to have a status code(200, 201, 403).
# It has to return data as JSON(key:value pairs).

from flask import Flask, request, jsonify
import json
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import Base, Product, User, Purchase, Payments, Sales, SalesDetails  

app =Flask(__name__)

#creating a connection to the database
engine = create_engine("sqlite:///./flask_duka_api.db", echo=True)

#create tables into sqlalchemy
Base.metadata.create_all(engine)

#create a session to do sql transactions
session = Session(engine)

user = {"id":"1",
    "full_name":"marto",
        "email":"marto@gmail.com",
        "password":"1234",
        "phone_number":"0723456789"}

@app.before_request
def before_request():
    try:
        print("A request is coming in!")
        new_user = User(user)
        session.add(new_user)
        session.commit()

        return jsonify({"Message":"User added successfully"}), 201
    except:
        print("Error found")

@app.route("/")
def home():
    if request.method == 'GET':
        data = {"Flask API" : "Version 1"}
        return jsonify(data), 200
    else:
        error = {"Error" : "Method not allowed"}
        return jsonify(error), 403

@app.route("/products", methods=["POST", "GET"])
def products():
    if request.method=="GET":
       #fetch data from the database
        query = select(Product)
        products = session.scalars(query)

        results = []
        for prod in products:
            p = {"id":prod.id, 
                "product_name":prod.product_name,
                  "buying_price":prod.buying_price, 
                  "selling_price":prod.selling_price}
            results.append(p)
              
        return jsonify(results), 200   
                                   
    elif request.method=="POST":
        data = request.get_json()
        if data["product_name"] == "" or data["buying_price"] =="" or data["selling_price"] == "":
            error = {"Error": "Ensure all fields are set"}
            return jsonify(error),403
        else:
            #store in the database
            new_product = Product(
                user_id = user["id"],
                product_name = data["product_name"],
                buying_price = float(data["buying_price"]),
                selling_price = float(data["selling_price"])
            )
            session.add(new_product)
            session.commit()
            return jsonify({"message":"product added successfully"})
    else:
        error = {"Error":"Method not allowed"}
        return jsonify(error),405


@app.route("/purchases", methods=["POST", "GET"])
def purchases():

    if request.method == "GET":
        # fetch purchases from the database
        query = select(Purchase)
        purchases = session.scalars(query)

        results = []

        for purchase in purchases:
            p = {
                "id": purchase.id,
                "product_id": purchase.product_id,
                "quantity": purchase.quantity,
                "buying_price": purchase.buying_price,
                "total_price": purchase.total_price
            }

            results.append(p)

        return jsonify(results), 200

    elif request.method == "POST":
        data = request.get_json()

        # check if all fields are provided
        if (
            data["product_id"] == ""
            or data["quantity"] == ""
            or data["buying_price"] == ""
        ):
            error = {
                "Error": "Ensure all fields are set"
            }

            return jsonify(error), 403

        else:
            # calculate total price
            total_price = (
                float(data["quantity"]) *
                float(data["buying_price"])
            )

            # store purchase in the database
            new_purchase = Purchase(
                user_id=user["id"],
                product_id=data["product_id"],
                quantity=int(data["quantity"]),
                buying_price=float(data["buying_price"]),
                total_price=total_price
            )

            session.add(new_purchase)
            session.commit()

            return jsonify({
                "message": "Purchase added successfully"
            }), 201

    else:
        error = {
            "Error": "Method not allowed"
        }

        return jsonify(error), 405

    
app.run(debug=True)    