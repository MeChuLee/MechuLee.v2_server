from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
import recommend
import pandas as pd
import random

app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/mechulee_db"
# mongo = PyMongo(app)
CORS(app)

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
        ingredient['name'] = row['재료 이름']
        ingredient['classification'] = row['분류']
        ingredient_list.append(ingredient)

    return jsonify({'ingredientList': ingredient_list})


# ai 추천 (liked_ingredients, disliked_ingredients 필요)
@app.route('/recommend/ai', methods=['POST'])
def recommend_ai():
    data = request.get_json()

    liked_ingredients = data['liked_ingredients']
    disliked_ingredients = data['disliked_ingredients']

    ai_menu = recommend.content_based_filtering_thompson(liked_ingredients, disliked_ingredients)
    print(ai_menu)

    return jsonify({'recommendAiResult': ai_menu})


# 비슷한 메뉴 추천
@app.route('/recommend/similar', methods=['POST'])
def recommend_similar():
    data = request.get_json()
    current_menu = data['menu']

    # menu_list.csv 파일을 데이터프레임으로 read
    menus = pd.read_csv('app/menu_list.csv')
    
    # 데이터프레임으로 읽어온 메뉴들을 list - dictionary 형태로 변형
    selected_items = []
    for _, row in menus.iterrows():
        if current_menu['category'] == row['분류']:
            menu = {}
            menu['name'] = row['메뉴 이름']
            menu['ingredients'] = row['재료']
            menu['category'] = row['분류']
            selected_items.append(menu)

    similar_menu_list = random.sample(selected_items, min(5, len(selected_items)))

    return jsonify({'similarMenuList': similar_menu_list})


# 재료 기반 추천
@app.route('/recommend/ingredient', methods=['POST'])
def recommend_ingredient():
    ingredient_menu_list = []
    return jsonify({'result' : ingredient_menu_list})


if __name__ == '__main__':
    # local 테스트를 위해 host='0.0.0.0' 로 설정 -> 추후 변경 필요
    app.run(host='0.0.0.0', debug=True, port=8000)