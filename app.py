from flask import Flask, request, jsonify
from flask_pymongo import PyMongo
from flask_cors import CORS

app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/mechulee_db"
# mongo = PyMongo(app)
CORS(app)

# @app.route('/menu', methods=['GET'])
# def get_all_menu_items():
#     menu_items = mongo.db.menu_items
#     output = []

#     for item in menu_items.find():
#         output.append({
#             'name': item['name'],
#             'ingredients': item['ingredients'],
#             'image_url': item['image_url']
#         })

#     return jsonify({'result': output})

@app.route('/test', methods=['GET'])
def get_test():
    return jsonify({'result': True})

if __name__ == '__main__':
    app.run(debug=True)
