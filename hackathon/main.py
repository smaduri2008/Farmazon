from flask import Flask,request, jsonify, make_response, render_template, send_from_directory
from flask.templating import render_template
from werkzeug.utils import secure_filename
import db_handler
import jwt
import datetime
import json
import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from bson.objectid import ObjectId
from bson import json_util
from flask_cors import CORS, cross_origin

UPLOAD_FOLDER = "./thumbnails"

app = Flask(__name__)
cors = CORS(app) 
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = "kdfjld"

@app.route("/login")
def hello_world():
    return render_template('index.html')

@app.route("/")
def main_file():
    return render_template('main.html')

@app.route("/addProduct")
def add_prod_page():
    return render_template('addProduct.html')

@app.route("/api/createUser", methods=["POST"])
def createUser():
    data = request.get_json()
    if not data or 'username' not in data or 'password' not in data or len(data['username']) == 0 or len(data["password"]) == 0:
        return jsonify({"message": "Missing username or password"}), 400
    print(len(data["username"]))
    username = data["username"]
    password = data["password"]

    if db_handler.find_user_by_username(username):
        return jsonify({"message": "User already exists"}), 401

    db_handler.add_document("users", {"username": username, "password": password})
    return jsonify({"message": "User created successfully"}), 201
    
    

@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"message": "Missing username or password"}), 401

    username = data["username"]
    password = data["password"]

    if not data or not db_handler.login_successful(username, password):
        return jsonify({"message": "Invalid username or password"}), 401

    data = {
        "username": username,
        "expiration": str(datetime.datetime.now() + datetime.timedelta(hours=24))
    }
    token = jwt.encode(data, str(app.config["SECRET_KEY"]), algorithm="HS256")

    # Set the JWT token as a cookie
    response = make_response(jsonify({"message": "Login Successful"}), 200)
    expiration_time = datetime.datetime.now() + datetime.timedelta(days=1)
    expires_formatted = expiration_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
    response.set_cookie("JWT_TOKEN", token, httponly=True, secure=True, samesite="Strict", max_age=24 * 60 * 60, expires=expires_formatted)

    return response


@app.route("/api/addProduce", methods = ["POST"])
def addProduce():
    
    data = request.form.get("data")
    jwt_cookie = str(request.cookies.get("JWT_TOKEN"))

    if jwt_cookie is None:
        return jsonify({"message": "unauthorized user"}), 401
    decoded_data = jwt.decode(jwt=jwt_cookie,
      key= app.config["SECRET_KEY"],
     algorithms=["HS256"])
    
    username = decoded_data["username"]
    data = json.loads(data)
    title = data["title"]
    address = data["address"]
    price = data["price"]
    
    
    if 'image' not in request.files:
        return jsonify({"message": "No Image Provided"}), 400
    file = request.files['image']
    if file.filename == '':
        return jsonify({"message": "No Image Provided"}), 400
    current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = username + "_" + title + "_" + current_time + "_" + file.filename
    filename = filename.replace(" ", "_")
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename)))
    
    product_data = {"title": title, "address": address, "image": filename, "username": username, "price": price}
    db_handler.add_document("produce", product_data)
   
    return jsonify({"message": "Successfully Added Product"}), 200

@app.route("/api/searchProduce", methods = ["POST"])
def searchProduce():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({"message": "Missing query parameter"}), 400
    query = data["query"]
    documents = db_handler.search_produce(query)
    products = [db_handler.get_produce_by_id(doc_id) for doc_id in documents]
    products = json.loads(json_util.dumps(products))
    return jsonify({"products": products}), 200

@app.route("/api/getProduceByID", methods=["GET"])
def searchProduceByID():
    data = request.get_json()
    if not data or 'id' not in data:
        return jsonify({"message": "Missing id parameter"}), 400
        
    document = db_handler.get_produce_by_id(data["id"])

    if not document:
        return jsonify({"message": "No document found"}), 404

    return jsonify({"produce": json.loads(json_util.dumps(document))}), 200

@app.route("/api/getNewestProduce", methods=["GET"])
def getNewestProduce():
    documents = db_handler.get_documents("produce", {})
    products = [db_handler.get_produce_by_id(doc["_id"]) for doc in documents]
    products = json.loads(json_util.dumps(products))
    products = products[::-1]
    return jsonify({"products": products}), 200

@app.route('/thumbnails/<filename>')
def serve_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)
    
if __name__ == "__main__":
    app.run(debug=True)