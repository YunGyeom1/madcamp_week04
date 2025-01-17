from pymongo import MongoClient
import os
from dotenv import load_dotenv
load_dotenv()


connection_string = os.getenv("MONGODB_URI")
client = MongoClient(connection_string)
db = client["W4_Calendar"]
collection = db["Test"]

goal_schema = {
    "title": "목표 제목",
    "description": "목표 설명",
    "children": [],  # 하위 목표의 ID 리스트
    "parent": None,
    "task": [0, 0, 0],
    "tag": "목표 태그",
    "height": 0,
    "due_date": "2025-01-30T10:00:00Z",  # Leaf Node만 해당
    
}

collection.insert_one(goal_schema)