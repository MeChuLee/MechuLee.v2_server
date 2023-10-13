from flask import Flask, request, jsonify
from flask_cors import CORS
import recommend
import random
from apscheduler.schedulers.background import BackgroundScheduler
from pymongo import MongoClient
import weather
from waitress import serve

app = Flask(__name__)

CORS(app)

# MongoDB 연결
client = MongoClient("mongodb://localhost:27017/")

# 데이터베이스 이름 
db = client.mechulee_db

# 컬렉션 이름
collection_menu = db.menu_list
collection_ingredient = db.ingredient_list

# 오늘의 메뉴 리스트
todays_menu = []

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


# 컨텐츠 기반 필터링에서 사용할 메뉴와 재료 임베딩 정보
temp_menu_list = select_menu_list(collection_menu)
temp_ingredient_list = select_ingredient_list(collection_ingredient)
embedding_dict, menu_data, menu_list_dict = recommend.read_meun_data(temp_menu_list, temp_ingredient_list)

# 오늘의 메뉴 선정
def select_today_menu():
    global todays_menu
    
    menu_list = select_menu_list(collection_menu)

    # 새로운 메뉴 선택 전, 오늘의 메뉴 리스트 초기화
    todays_menu.clear()

    # 전체 인덱스에서 3개 선택하여 오늘의 메뉴로 선정
    selected_indices = random.sample(range(len(menu_list)), 3)

    for index in selected_indices:
        menu_info = menu_list[index]
        menu = {}
        menu['name'] = menu_info['name']
        menu['ingredients'] = menu_info['ingredients']
        menu['category'] = menu_info['category']
        todays_menu.append(menu)


# 오늘의 추천
@app.route('/recommend/today', methods=['GET'])
def recommend_today():
    return jsonify({'menuList' : todays_menu})


# 전체 메뉴 조회
@app.route('/allmenu', methods=['GET'])
def get_all_menu_items():
    menus = select_menu_list(collection_menu)

    menu_list = []
    for row in menus:
        menu = {}
        menu['name'] = row['name']
        menu['ingredients'] = row['ingredients']
        menu['category'] = row['category']
        menu_list.append(menu)

    return jsonify({'menuList': menu_list})


# 전체 재료 조회
@app.route('/allingredient', methods=['GET'])
def get_all_ingredient_items():
    ingredients = select_ingredient_list(collection_ingredient)

    ingredient_list = []
    for row in ingredients:
        ingredient = {}
        ingredient['title'] = row['name']
        ingredient['classification'] = row['classification']
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
            disliked_ingredients.extend([ingredient_info['title'], ingredient_info['title']])
        elif rating == 2: #평점이 2점인 경우 disliked_ingredients에 1번 삽입
            disliked_ingredients.append(ingredient_info['title'])
        elif rating == 3: #평점이 3점인 경우 liked_ingredients에 1번 삽입
            liked_ingredients.append(ingredient_info['title'])
        elif rating == 4: #평점이 4점인 경우 liked_ingredients에 2번 삽입
            liked_ingredients.extend([ingredient_info['title'], ingredient_info['title']])
        elif rating == 5: #평점이 5점인 경우 liked_ingredients에 4번 삽입
            liked_ingredients.extend([ingredient_info['title'], ingredient_info['title'], ingredient_info['title'], ingredient_info['title']])

    #content_based_filterting_thompson을 text기반으로 수행하기 때문에 title리스트로 넣어준다.
    ai_menu = recommend.content_based_filtering_thompson(embedding_dict, menu_data, menu_list_dict, liked_ingredients, disliked_ingredients)

    return jsonify({'recommendAiResult': ai_menu})


# 날씨 조회
@app.route('/weather', methods=['GET'])
def get_weather_info():
    # 특별시/광역시/특별자치시, 도/특별자치도, 지역명 받아오기
    # 'adminArea' 쿼리 매개변수를 추출하여 사용
    admin_area = request.args.get('adminArea')

    rain_type, sky, temp = weather.get_weatherinfo_by_location(admin_area)

    # 날씨 정보를 JSON 형식으로 패킹해서 반환
    weather_info = {
        "rainType": rain_type,
        "sky": sky,
        "temp": temp
    }

    return jsonify({'weatherInfo' : weather_info})


if __name__ == '__main__':
    scheduler = BackgroundScheduler(daemon=True)
    
    # 매일 자정에 select_menu 함수 실행 설정 
    scheduler.add_job(select_today_menu,'cron', hour=0)

    # 매 시간마다 get_temperature_and_store 함수 호출 -> 날씨 정보 30분마다 갱신
    scheduler.add_job(weather.loading_location_weather_data, 'interval', minutes=30)
    
    scheduler.start()

    # 서버 시작 전, 첫 날의 메뉴 선택 
    select_today_menu()

    # 서버 시작 하자마자 위치에 따른 기온 모두 받아두기
    weather.loading_location_weather_data()

    serve(app, host="0.0.0.0", port=8000)
