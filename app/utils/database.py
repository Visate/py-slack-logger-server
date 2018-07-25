from pymongo import MongoClient, Collection
from utils.config import mongo as config
from urllib.parse import quote_plus

# username and password must be percent encoded
username = quote_plus(config['username'])
password = quote_plus(config['password'])
address = config['address']
database = config['database']

db_uri = f'mongodb://{username}:{password}@{address}/{database}'

def close_connection(connection):
    if isinstance(connection, Collection):
        connection = connection.database
    connection.client.close()

def get_collection(name):
    # always returns a new MongoClient to ensure threadsafe
    return MongoClient(db_uri)[database][name]

def insert_document(document, collection_name):
    collection = get_collection(collection_name)
    collection.insert_one(document)
    close_connection(collection)

def find_document(search, collection_name):
    collection = get_collection(collection_name)
    result = collection.find_one(search)
    close_connection(collection)
    return result

def update_document(search, update, collection_name):
    collection = get_collection(collection_name)
    collection.update_one(search, update)
    close_connection(collection)

def find_and_update_document(search, update, collection_name):
    collection = get_collection(collection_name)
    result = collection.find_one_and_update(search, update)
    close_connection(collection)
    return result

