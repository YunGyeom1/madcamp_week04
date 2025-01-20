from pymongo import MongoClient
from db.db import get_collection

tag_collection = get_collection("Tags")   # tag를 관리할 collection
goal_collection = get_collection("Test")

# 태그 DB 스키마
TAG_SCHEMA_TEMPLATE = {
    "name": "",         # 태그 이름
    "selected": False,  # 선택 여부
    "restricted": False # 금지 여부
}

def sync_tags_with_goals():
    # Goal 컬렉션에서 모든 태그 수집
    all_tags = goal_collection.distinct("tag")

    if "deleted" not in all_tags:
        all_tags.append("deleted")
    if "all" not in all_tags:
        all_tags.append("all")

    for tag in all_tags:
        # 태그가 이미 존재하면 무시, 없으면 추가
        if not tag_collection.find_one({"name": tag}):
            restricted = (tag == "deleted")  # 'deleted' 태그는 기본적으로 restricted = True
            selected = (tag == "all")      # 'all' 태그는 기본적으로 selected = True
            tag_collection.insert_one({"name": tag, "selected": selected, "restricted": restricted})

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

def load_tags():
    sync_tags_with_goals()  # 태그 컬렉션과 Goal 컬렉션 동기화
    return list(tag_collection.find())  # 모든 태그 반환
