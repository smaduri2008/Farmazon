
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
from bson.objectid import ObjectId
from bson import json_util

uri = "mongodb+srv://ajaydavasi:Hack2024@farmers.i0secqd.mongodb.net/?retryWrites=true&w=majority&appName=farmers"
database_name = "farmer-app"

# Create a new client and connect to the server
client = MongoClient(uri, server_api=ServerApi('1'))
database = client[database_name]

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)

def add_document(collection_name, document):
    collection = database[collection_name]
    collection.insert_one(document)

def get_document(collection_name, query):
    collection = database[collection_name]
    return collection.find_one(query)

def get_documents(collection_name, query):
    collection = database[collection_name]
    return collection.find(query)

def find_user_by_username(username):
    return get_document("users", {"username": username})

def login_successful(username, password):
    return get_document("users", {"username": username, "password": password}) is not None

def get_freq(sentence):
    word_freq = {}
    words = sentence.lower().split(" ")
    for word in words:
        if word not in word_freq:
            word_freq[word] = 1
        else:
            word_freq[word] += 1
    return word_freq
def get_produce_by_id(id):
    try:
        id = ObjectId(id)
    except Exception as e:
        print(e)

    query = {"_id": id}
    document = get_document("produce", query)
    return document
    
def search_produce(query):
    documents = get_documents("produce","")
    freq = []
    for doc in documents:
        word_freq = get_freq(doc["title"])
        data = {
            "title": doc["title"],
            "_id": doc["_id"],
            "word_freq":word_freq
        }
        freq.append(data)
    query_freq = get_freq(query)
    scores = []
    for doc in freq:
        score = 0
        for word in query_freq:
            if word in doc["word_freq"]:
                score += doc["word_freq"][word] * query_freq[word]
        if score == 0:
            continue
        scores.append({"score": score, "document_id": str(doc["_id"])})
    if len(scores) == 0:
        return list()        
    
    df = pd.DataFrame.from_dict(scores)
    df = df.sort_values(by=["score"], ascending=False)
    return df['document_id'].tolist()
