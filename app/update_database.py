import pandas as pd
import csv
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

# 데이터베이스 이름 
db = client.mechulee_db

# 컬렉션 이름
collection_menu = db.menu_list
collection_ingredient = db.ingredient_list

# csv 파일을 read
menu_data = pd.read_csv("app/menu_list.csv", encoding='utf-8')
ingredient_data = pd.read_csv("app/ingredient_list.csv", encoding='utf-8')

def clear_collection(now_collection):
    now_collection.delete_many({})

# 저장하는 함수
def save_menu_data(now_collection, menu_data):
    jsonList = []

    for i in range(len(menu_data["메뉴 이름"])):
        jsonData = {}
        jsonData['name'] = list(menu_data["메뉴 이름"])[i]
        jsonData['ingredients'] = list(menu_data["재료"])[i].split(', ')
        jsonData['weather'] = list(menu_data["날씨"])[i]
        jsonData['time'] = list(menu_data["시간"])[i]
        jsonData['type'] = list(menu_data["종류"])[i]
        jsonData['classification'] = list(menu_data["분류"])[i]
        jsonData['delivery'] = True if list(menu_data["배달용"])[i] == 'T' else False

        jsonList.append(jsonData)
    now_collection.insert_many(jsonList)

def save_ingredient_data(now_collection, ingredient_data):
    jsonList = []
    for i in range(len(ingredient_data["재료 이름"])):
        jsonData = {}
        jsonData['name'] = list(ingredient_data["재료 이름"])[i]
        jsonData['classification'] = list(ingredient_data["분류"])[i]

        jsonList.append(jsonData)
    now_collection.insert_many(jsonList)


def export_ingredients(menu_data):
    tempDict = {}
    for i in range(len(ingredient_data["재료 이름"])):
        tempDict[list(ingredient_data["재료 이름"])[i]] = list(ingredient_data["분류"])[i]

    tempList = []
    for i in range(len(menu_data["메뉴 이름"])):
        tempList.extend(list(menu_data["재료"])[i].split(', '))
    tempList = list(set(tempList))

    for i in range(len(tempList)):
        tempList[i] = [tempList[i], tempDict[tempList[i]]]

    # temp_ingredient_list.csv 파일로 저장
    # 이름만 바꿔주면 됩니다
    with open('app/ingredient_list.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['재료 이름', '분류'])
        writer.writerows(tempList)
    f.close()

if __name__ == "__main__":
    None
    # DB 데이터 지우고 다시 저장하는 부분
    clear_collection(collection_menu)
    clear_collection(collection_ingredient)
    save_menu_data(collection_menu, menu_data)
    save_ingredient_data(collection_ingredient, ingredient_data)

    # 재료 csv파일 만드는 부분
    # export_ingredients(menu_data)
