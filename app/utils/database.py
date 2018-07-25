from pymongo import MongoClient
from utils.config import mongo as config
from urllib.parse import quote_plus

# username and password must be percent encoded
username = quote_plus(config['username'])
password = quote_plus(config['password'])
address = config['address']
database = config['database']

db_uri = f'mongodb://{username}:{password}@{address}/{database}'

def get_collection(name):
    # always returns a new MongoClient to ensure threadsafe
    return MongoClient(db_uri)[database][name]

def insert_document(document, collection_name):
    collection = get_collection(collection_name)
    collection.insert_one(document)
    collection.close()

def find_and_update_document(search, update, collection_name):
    collection = get_collection(collection_name)
    collection.find_one_and_update(search, update)
    collection.close()

