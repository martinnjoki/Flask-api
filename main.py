# it has to have a route.
# it has to have a method(POST/GET/PUT).
# It has to have a status code(200, 201, 403).
# It has to return data as JSON(key:value pairs).

from flask import Flask, request, jsonify
import json
from sqlalchemy import create_engine
from models import Base

app =Flask(__name__)

#creating a connection to the database
engine = create_engine("sqlite:///./flask_duka_api.db", echo=True)

#create tables into sqlalchemy
Base.metadata.create_all(engine)

@app.route("/")
def home():
    if request.method == 'GET':
        data = {"Flask API" : "Version 1"}
        return jsonify(data), 200
    else:
        error = {"Error" : "Method not allowed"}
        return jsonify(error), 403

app.run(debug=True)    