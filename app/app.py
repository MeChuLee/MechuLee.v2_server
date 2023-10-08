from flask import Flask, request, jsonify
from flask_cors import CORS
import recommend
import pandas as pd
import random
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import MongoClient

app = Flask(__name__)

# MongoDB 연결
client = MongoClient("mongodb://localhost:27017/")

# 데이터베이스 이름 
db = client.mechulee_db

# 컬렉션 이름
collection_menu = db.menu_list
collection_ingredient = db.ingredient_list

# 조회하는거 하기 전에 메뉴의 재료 부분 array인거 수정해줘야 동작가능

# MongoDB에서 전체 메뉴 조회
def select_menu_list(now_collection):
    menu_list = []
    for menu in now_collection.find({}, {'_id': False}):
        menu_list.append(menu)
    return menu_list

# MongoDB에서 전체 재료 조회
def select_ingredient_list(now_collection):
    ingredient_list = []
    for ingredient in now_collection.find({}, {'_id': False}):
        ingredient_list.append(ingredient)
    return ingredient_list

CORS(app)

# 오늘의 메뉴 리스트
todays_menu = []

# 오늘의 메뉴 선정
def select_today_menu():
    global todays_menu

    menu_list = pd.read_csv('app/menu_list.csv')
    # menu_list2 = select_menu_list(collection_menu)

    # 새로운 메뉴 선택 전, 오늘의 메뉴 리스트 초기화
    todays_menu.clear()

    # 전체 인덱스에서 3개 선택하여 오늘의 메뉴로 선정
    selected_indices = random.sample(range(len(menu_list)), 3)

    # temp = []

    for index in selected_indices:
        menu_info = menu_list.iloc[index].to_dict()
        menu = {}
        menu['name'] = menu_info['메뉴 이름']
        menu['ingredients'] = menu_info['재료']
        menu['category'] = menu_info['분류']
        todays_menu.append(menu)

    #     menu_info2 = menu_list2[index]
    #     menu2 = {}
    #     menu2['name'] = menu_info2['name']
    #     menu2['ingredients'] = menu_info2['ingredients']
    #     menu2['category'] = menu_info2['classification']
    #     temp.append(menu2)

    # print("오늘 메뉴 확인", todays_menu)
    # print("임시 확인", temp)


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
    print(data)
    totalList = []  # totalList 초기화 (IngredientInfo 객체를 포함하는 빈 리스트)
    totalList = data

    liked_ingredients = []
    disliked_ingredients = []

    # 전체 리스트에서 liked_ingredients,disliked_ingredients에는 title만 추가한다.
    for ingredient_info in totalList:
        rating = ingredient_info['rating']
        if rating == 1: #평점이 1점인 경우 disliked_ingredients에 2번 삽입
            disliked_ingredients.append(ingredient_info['title'])
            disliked_ingredients.append(ingredient_info['title'])
        elif rating == 2: #평점이 2점인 경우 disliked_ingredients에 1번 삽입
            disliked_ingredients.append(ingredient_info['title'])
        elif rating == 3: #평점이 3점인 경우 liked_ingredients에 1번 삽입
            liked_ingredients.append(ingredient_info['title'])
        elif rating == 4: #평점이 4점인 경우 liked_ingredients에 2번 삽입
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
        elif rating == 5: #평점이 5점인 경우 liked_ingredients에 4번 삽입
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])
            liked_ingredients.append(ingredient_info['title'])

    #content_based_filterting_thompson을 text기반으로 수행하기 때문에 title리스트로 넣어준다.
    ai_menu = recommend.content_based_filtering_thompson(liked_ingredients, disliked_ingredients)
    print("메뉴 결과가 무엇일까요?~",ai_menu)

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


# 좌표 받아오기
@app.route('/location', methods=['GET'])
def save_location():
    
    latitude = request.args.get('latitude', type=int)
    longitude = request.args.get('longitude', type=int)

    # config에 값을 저장
    app.config['latitude'] = latitude
    app.config['longitude'] = longitude

    # 위도와 경도 값을 받아서 출력
    print("Received latitude={} and longitude={}".format(app.config['latitude'], app.config['longitude']))

    
    # 예를 들어, JSON 응답을 반환
    response_data = {
        "latitude": latitude,
        "longitude": longitude,
        "message": "Received latitude and longitude successfully."
    }

    return jsonify(response_data)


# 좌표 받아와서 날씨api요청보내고 필요한
if __name__ == '__main__':
    scheduler = BackgroundScheduler(daemon=True)
    
    # 매일 자정에 select_menu 함수 실행 설정 
    scheduler.add_job(select_today_menu,'cron', hour=0)
    
    scheduler.start()

    # 서버 시작 전, 첫 날의 메뉴 선택 
    select_today_menu()


    # local 테스트를 위해 host='0.0.0.0' 로 설정 -> 추후 변경 필요
    app.run(host='0.0.0.0', debug=True, port=8000)