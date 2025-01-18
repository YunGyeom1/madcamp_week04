from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
load_dotenv()

connection_string = os.getenv("MONGODB_URI")
client = MongoClient(connection_string)
db = client["W4_Calendar"]
collection = db["Test"]



def MakeNode(title: str, description: str = "", parent = None, tag: str = "", location: str = ""):
    goal_schema = {
        "title": title,
        "description": description,
        "children": [],  # 하위 목표의 ID 리스트
        "parent": None,
        "task": [0, 0, 0],
        "tag": tag,
        "height": 1,
        "width": 0,
        "isOpen": True,
        "location": location,
        "due_date": "2025-01-30T10:00:00Z",  # Leaf Node만 해당
        "start_time": None,
        "end_time": None
    }
    collection.insert_one(goal_schema)


def add_child(parent_id, child_id):
    """자식 노드 추가 및 부모 관계 설정."""
    collection.update_one({"_id": parent_id}, {"$push": {"children": child_id}})
    result = collection.update_one({"_id": child_id}, {"$set": {"parent": parent_id}})
    print(f"Update result for parent: {result.modified_count}")
    update_height(parent_id)


def update_height(node):
    """부모 및 조상 노드의 높이와 너비를 갱신."""
    data = collection.find_one({"_id": ObjectId(node)})
    maxheight = 1
    for childid in data["children"]:
        child = collection.find_one({"_id": ObjectId(childid)})
        if child["height"]+1 > maxheight:
            maxheight = child["height"]+1
    data["height"] = maxheight

    width = 1
    for childid in data["children"]:
        child = collection.find_one({"_id": ObjectId(childid)})
        width += child["width"]
    data["width"] = width

    if data["parent"]!=None:
        update_height(data["parent"])
    

def is_leaf(node):
    """리프 노드 여부 확인."""
    data = collection.find_one({"_id": ObjectId(node)})
    return len(data["children"]) == 0