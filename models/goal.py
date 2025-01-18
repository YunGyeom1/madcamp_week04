from pymongo import MongoClient
from bson.objectid import ObjectId
import os
from dotenv import load_dotenv
load_dotenv()

connection_string = os.getenv("MONGODB_URI")
client = MongoClient(connection_string)
db = client["W4_Calendar"]
collection = db["Test"]



def MakeNode(title: str, parent: ObjectId, description: str = "", tag: str = "", location: str = ""):
    """부모 노드에 시간 일정이 있으면 자식 노드를 만들 수 없도록"""
    parent_node = collection.find_one({"_id": parent})
    if parent_node["start_time"] is not None and parent_node["end_time"] is not None:
        print("부모 노드가 leaf 노드입니다.")
        return
    goal_schema = {
        "title": title,
        "description": description,
        "children": [],  # 하위 목표의 ID 리스트
        "parent": parent,
        "task": [0, 0, 0],
        "tag": tag,
        "height": 1,
        "width": 1,
        "isOpen": True,
        "location": location,
        "due_date": "2025-01-30T10:00:00Z",  # Leaf Node만 해당
        "start_time": None,
        "end_time": None
    }
    result = collection.insert_one(goal_schema)
    collection.update_one({"_id": parent}, {"$push": {"children": result.inserted_id}})
    update_height(parent)
    return result.inserted_id


def add_child(parent_id, child_id):
    """자식 노드 추가 및 부모 관계 설정. MakeNode로 합쳐서 이젠 필요없음"""
    collection.update_one({"_id": parent_id}, {"$push": {"children": child_id}})
    result = collection.update_one({"_id": child_id}, {"$set": {"parent": parent_id}})
    print(f"Update result for parent: {result.modified_count}")
    update_height(parent_id)

def add_leaf(node):
    """캘린더에 드래그 앤 드롭했을 때 호출되는 함수"""
    data = collection.find_one({"_id": node})
    data.pop('_id')
    leaf = collection.insert_one(data)
    collection.update_one({"_id": node}, {"$push": {"children": leaf.inserted_id}})
    collection.update_one({"_id": leaf.inserted_id}, {"$set": {"parent": node}})


def update_height(node, cache=None):
    """부모 및 조상 노드의 높이와 너비를 갱신."""
    if cache is None:
        cache = {}

    # 노드 데이터 가져오기 (캐시에서 검색)
    if node not in cache:
        data = collection.find_one({"_id": node})
        cache[node] = data
    else:
        data = cache[node]
    
    maxheight = 1
    width = 0
    
    # 자식들의 높이와 너비를 갱신
    for childid in data["children"]:
        if childid not in cache:
            child = collection.find_one({"_id": childid})
            cache[childid] = child
        else:
            child = cache[childid]
        
        maxheight = max(maxheight, child["height"] + 1)
        width += child["width"]

    # 데이터베이스에 업데이트
    collection.update_one(
        {"_id": node},
        {"$set": {"height": maxheight, "width": max(width, 1)}}
    )

    # 부모 노드 갱신 (재귀적으로 호출)
    if data["parent"] is not None:
        update_height(data["parent"], cache)


    

    

def is_leaf(node):
    """리프 노드 여부 확인."""
    data = collection.find_one({"_id": node})
    return len(data["children"]) == 0