from pymongo import MongoClient
from db.db import get_collection

tag_collection = get_collection("Tags")   # tag를 관리할 collection
goal_collection = get_collection("Test")

# 태그 DB 스키마
TAG_SCHEMA_TEMPLATE = {
    "name": "",         # 태그 이름
    "selected": False,  # 선택 여부
    
}

def update_tag_selection(tag_name, selected):
    tag_collection.update_one({"name": tag_name}, {"$set": {"selected": selected}})

def get_selected_tags():
    return [tag["name"] for tag in tag_collection.find({"selected": True})]

def filter_goals_by_tags():
    selected_tags = get_selected_tags()
    if not selected_tags:
        return []  # 선택된 태그가 없으면 빈 리스트 반환

    # 선택된 태그를 가진 Goal 필터링
    return list(goal_collection.find({"tag": {"$in": selected_tags}}))


