from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
load_dotenv()

connection_string = os.getenv("MONGODB_URI")
client = MongoClient(connection_string)
db = client["W4_Calendar"]
collection = db["Test"]



def MakeNode(title: str, parent: ObjectId = None, description: str = "", tag: str = "", location: str = ""):
    goal_schema = {
        "title": title,
        "description": description,
        "children": [],
        "parent": parent,
        "task": [0, 0, 0],
        "tag": tag,
        "height": 1,
        "width": 0,
        "isOpen": True,
        "location": location,
        "due_date": "2025-01-30T10:00:00Z",
        "start_time": None,
        "end_time": None
    }
    result = collection.insert_one(goal_schema)
    print(f"[INFO] Created Node: {title} -> ID: {result.inserted_id}")

    if parent:
        collection.update_one({"_id": parent}, {"$push": {"children": result.inserted_id}})
        print(f"[INFO] Added Node {result.inserted_id} to Parent {parent}")

    # 부모의 높이 및 너비 갱신을 자식 생성 후 호출
    if parent:
        update_height(parent)

    return result.inserted_id
# def add_child(parent_id, child_id):
#     """자식 노드 추가 및 부모 관계 설정."""
#     collection.update_one({"_id": parent_id}, {"$push": {"children": child_id}})
#     result = collection.update_one({"_id": child_id}, {"$set": {"parent": parent_id}})
#     print(f"Update result for parent: {result.modified_count}")
#     update_height(parent_id)

def add_leaf(node):
    """캘린더에 드래그 앤 드롭했을 때 호출되는 함수"""
    data = collection.find_one({"_id": node})
    data.pop('_id')
    leaf = collection.insert_one(data)
    collection.update_one({"_id": node}, {"$push": {"children": leaf.inserted_id}})
    collection.update_one({"_id": leaf.inserted_id}, {"$set": {"parent": node}})


def update_height(node):
    """부모 및 조상 노드의 높이와 너비를 갱신."""
    data = collection.find_one({"_id": ObjectId(node)})
    if not data:
        print(f"[ERROR] Node with ID {node} not found.")
        return

    maxheight = 1
    width = 1

    for childid in data.get("children", []):
        child = collection.find_one({"_id": ObjectId(childid)})
        if child:
            maxheight = max(maxheight, child.get("height", 1) + 1)
            width += child.get("width", 0)
        else:
            print(f"[WARNING] Child with ID {childid} not found.")

    # MongoDB에 업데이트
    collection.update_one(
        {"_id": ObjectId(node)},
        {"$set": {"height": maxheight, "width": width}}
    )
    print(f"[INFO] Updated Node {data['title']} ({node}): Height={maxheight}, Width={width}")

    # 부모 노드 갱신
    if data.get("parent"):
        update_height(data["parent"])
    """부모 및 조상 노드의 높이와 너비를 갱신."""
    data = collection.find_one({"_id": ObjectId(node)})
    if not data:
        print(f"[ERROR] Node with ID {node} not found.")
        return

    maxheight = 1
    width = 1

    for childid in data.get("children", []):
        child = collection.find_one({"_id": ObjectId(childid)})
        if child:
            maxheight = max(maxheight, child.get("height", 1) + 1)
            width += child.get("width", 0)
        else:
            print(f"[WARNING] Child with ID {childid} not found.")

    # MongoDB에 업데이트
    collection.update_one(
        {"_id": ObjectId(node)},
        {"$set": {"height": maxheight, "width": width}}
    )

    # 부모 노드 갱신
    if data.get("parent"):
        update_height(data["parent"])
    """부모 및 조상 노드의 높이와 너비를 갱신."""
    data = collection.find_one({"_id": node})
    maxheight = 1
    for childid in data["children"]:
        child = collection.find_one({"_id": childid})
        if child["height"]+1 > maxheight:
            maxheight = child["height"]+1
    data["height"] = maxheight

    width = 1
    for childid in data["children"]:
        child = collection.find_one({"_id": childid})
        width += child["width"]
    data["width"] = width

    collection.update_one(
    {"_id": node},
    {"$set": {"height": maxheight, "width": width}}
    )

    if data["parent"]!=None:
        update_height(data["parent"])