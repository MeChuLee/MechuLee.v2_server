from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
import recommend
import pandas as pd
import random
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime

app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/mechulee_db"
# mongo = PyMongo(app)
CORS(app)

# 오늘의 메뉴 리스트
todays_menu = []

# 컨텐츠 기반 필터링에서 사용할 메뉴와 재료 임베딩 정보
embedding_dict, menu_data, menu_list_dict = recommend.read_meun_data()

# 오늘의 메뉴 선정
def select_today_menu():
    global todays_menu

    menu_list = pd.read_csv('app/menu_list.csv')

    # 새로운 메뉴 선택 전, 오늘의 메뉴 리스트 초기화
    todays_menu.clear()

    # 전체 인덱스에서 3개 선택하여 오늘의 메뉴로 선정
    selected_indices = random.sample(range(len(menu_list)), 3)

    for index in selected_indices:
        menu_info = menu_list.iloc[index].to_dict()
        menu = {}
        menu['name'] = menu_info['메뉴 이름']
        menu['ingredients'] = menu_info['재료']
        menu['category'] = menu_info['분류']
        todays_menu.append(menu)


# 전체 메뉴 조회
@app.route('/allmenu', methods=['GET'])
def get_all_menu_items():
    # menu_list.csv 파일을 데이터프레임으로 read
    menus = pd.read_csv('app/menu_list.csv')
    
    # 데이터프레임으로 읽어온 메뉴들을 list - dictionary 형태로 변형
    menu_list = []
    for _, row in menus.iterrows():
        menu = {}
        menu['name'] = row['메뉴 이름']
        menu['ingredients'] = row['재료']
        menu['category'] = row['분류']
        menu_list.append(menu)

    return jsonify({'menuList': menu_list})


# 전체 재료 조회
@app.route('/allingredient', methods=['GET'])
def get_all_ingredient_items():
    # ingredient_list.csv 파일을 데이터프레임으로 read
    ingredients = pd.read_csv('app/ingredient_list.csv')

    # 데이터프레임으로 읽어온 재료들을 list - dictionary 형태로 변형
    ingredient_list = []
    for _, row in ingredients.iterrows():
        ingredient = {}
        ingredient['title'] = row['재료 이름']
        ingredient['classification'] = row['분류']
        ingredient_list.append(ingredient)

    return jsonify({'ingredientList': ingredient_list})


# ai 추천 (liked_ingredients, disliked_ingredients 필요)
@app.route('/recommend/ai', methods=['POST'])
def recommend_ai():
    data = request.get_json()
    
    totalList = []  # totalList 초기화 (IngredientInfo 객체를 포함하는 빈 리스트)
    totalList = data

    liked_ingredients = []
    disliked_ingredients = []

    # 전체 리스트에서 liked_ingredients,disliked_ingredients에는 title만 추가한다.
    for ingredient_info in totalList:
        rating = ingredient_info['rating']
        if rating == 1: #평점이 1점인 경우 disliked_ingredients에 2번 삽입
            disliked_ingredients.append(ingredient_info['title'])
        elif rating == 2: #평점이 2점인 경우 disliked_ingredients에 1번 삽입
            disliked_ingredients.append(ingredient_info['title'])
        elif rating == 3 or rating == 4 or rating == 5: #평점이 3점인 경우 liked_ingredients에 1번 삽입
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            
       

    # # 전체 리스트에서 liked_ingredients,disliked_ingredients에는 title만 추가한다.
    # for ingredient_info in totalList:
    #     rating = ingredient_info['rating']
    #     if rating == 1: #평점이 1점인 경우 disliked_ingredients에 2번 삽입
    #         disliked_ingredients.extend([ingredient_info['title'], ingredient_info['title']])
    #     elif rating == 2: #평점이 2점인 경우 disliked_ingredients에 1번 삽입
    #         disliked_ingredients.append(ingredient_info['title'])
    #     elif rating == 3: #평점이 3점인 경우 liked_ingredients에 1번 삽입
    #         liked_ingredients.append(ingredient_info['title'])
    #     elif rating == 4: #평점이 4점인 경우 liked_ingredients에 2번 삽입
    #         liked_ingredients.extend([ingredient_info['title'], ingredient_info['title']])
    #     elif rating == 5: #평점이 5점인 경우 liked_ingredients에 4번 삽입
    #         liked_ingredients.extend([ingredient_info['title'], ingredient_info['title'], ingredient_info['title'], ingredient_info['title']])

    #content_based_filterting_thompson을 text기반으로 수행하기 때문에 title리스트로 넣어준다.
    ai_menu = recommend.content_based_filtering_thompson(embedding_dict, menu_data, menu_list_dict, liked_ingredients, disliked_ingredients)

    return jsonify({'recommendAiResult': ai_menu})


# 비슷한 메뉴 추천
@app.route('/recommend/similar', methods=['POST'])
def recommend_similar():
    data = request.get_json()

    # menu_list.csv 파일을 데이터프레임으로 read
    menus = pd.read_csv('app/menu_list.csv')
    
    # 데이터프레임으로 읽어온 메뉴들을 list - dictionary 형태로 변형
    selected_items = []
    for _, row in menus.iterrows():
        if data['category'] == row['분류'] and data['name'] != row['메뉴 이름']:
            menu = {}
            menu['name'] = row['메뉴 이름']
            menu['ingredients'] = row['재료']
            menu['category'] = row['분류']
            selected_items.append(menu)

    similar_menu_list = random.sample(selected_items, min(5, len(selected_items)))

    return jsonify({'menuList': similar_menu_list})


# 재료 기반 추천
@app.route('/recommend/ingredient', methods=['POST'])
def recommend_ingredient():
    ingredient_menu_list = []
    return jsonify({'result' : ingredient_menu_list})


# 오늘의 추천
@app.route('/recommend/today', methods=['GET'])
def recommend_today():
    return jsonify({'menuList' : todays_menu})


# 랜덤 추천
@app.route('/recommend/random', methods=['GET'])
def recommend_random():
    menu_list = pd.read_csv('app/menu_list.csv')

    selected_index = random.sample(range(len(menu_list)), 1)

    menu_info = menu_list.iloc[selected_index[0]].to_dict()

    menu = {}
    menu['name'] = menu_info['메뉴 이름']
    menu['ingredients'] = menu_info['재료']
    menu['category'] = menu_info['분류']

    return jsonify({'menuInfo' : menu})


if __name__ == '__main__':
    scheduler = BackgroundScheduler(daemon=True)
    
    # 매일 자정에 select_menu 함수 실행 설정 
    scheduler.add_job(select_today_menu,'cron', hour=0)
    
    scheduler.start()
    
    # 서버 시작 전, 첫 날의 메뉴 선택 
    select_today_menu()

    # local 테스트를 위해 host='0.0.0.0' 로 설정 -> 추후 변경 필요
    app.run(host='0.0.0.0', debug=True, port=8000)