from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
connection_string = os.getenv("MONGODB_URI")
client = MongoClient(connection_string)
db = client["W4_Calendar"]

# 함수로 DB와 컬렉션 가져오기
def get_collection(collection_name="Calendar_Goals"):
    return db[collection_name]

 