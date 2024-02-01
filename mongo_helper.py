import os
import pymongo
from dotenv import load_dotenv

load_dotenv()

def conectar_mongo():
    mongodb_host = os.getenv("MONGODB_HOST", "mongodb")
    mongodb_port = os.getenv("MONGODB_PORT", "27017")
    mongodb_user = os.getenv("MONGODB_USER", "mongodb")
    mongodb_password = os.getenv("MONGODB_PASSWORD", "pass1234")
    mongodb_database = os.getenv("MONGODB_DATABASE", "event_find_db")

    if mongodb_port:
        mongodb_uri = f"mongodb://{mongodb_user}:{mongodb_password}@{mongodb_host}:{mongodb_port}/{mongodb_database}"
    else:
        mongodb_uri = f"mongodb+srv://{mongodb_user}:{mongodb_password}@{mongodb_host}/{mongodb_database}?retryWrites=true&w=majority"

    mongodb_uri = f"mongodb+srv://{mongodb_user}:{mongodb_password}@{mongodb_host}/admin?retryWrites=true&w=majority"

    cliente = pymongo.MongoClient(mongodb_uri)
    db = cliente[mongodb_database]
    return db

