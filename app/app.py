from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS
import recommend
import pandas as pd

app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/mechulee_db"
# mongo = PyMongo(app)
CORS(app)

@app.route('/get', methods=['GET'])
def get_test():
    return jsonify({'result': True})

@app.route('/post', methods=['POST'])
def post_test():
    data = request.get_json()

    liked_ingredients = data['liked_ingredients']
    disliked_ingredients = data['disliked_ingredients']

    recommend_menu = recommend.content_based_filtering_thompson(liked_ingredients, disliked_ingredients)
    print(recommend_menu)

    return jsonify({'result': recommend_menu})

@app.route('/allmenu', methods=['GET'])
def get_all_menu_items():
    # menu_list.csv 파일을 데이터프레임으로 읽어옴
    menus = pd.read_csv('app/menu_list.csv')
    
    menu_list = []
    for _, row in menus.iterrows():
        menu = {}
        menu['name'] = row['메뉴 이름']
        menu['ingredients'] = row['재료']
        menu['category'] = row['분류']
        menu_list.append(menu)

    return jsonify({'menuList': menu_list})

@app.route('/allingredient', methods=['GET'])
def get_all_ingredient_items():
    # menu_list.csv 파일을 데이터프레임으로 읽어옴
    ingredients = pd.read_csv('app/ingredient_list.csv')

    ingredient_list = []
    for _, row in ingredients.iterrows():
        ingredient = {}
        ingredient['name'] = row['재료 이름']
        ingredient['classification'] = row['분류']
        ingredient_list.append(ingredient)

    return jsonify({'result': ingredient_list})

if __name__ == '__main__':
    app.run(debug=True, port=8000)