import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from scipy.stats import beta as beta_dist
import random
from datetime import datetime
from gensim.models import KeyedVectors

def read_meun_data():
    # menu_list.csv 파일을 데이터프레임으로 읽어옴
    menu = pd.read_csv('app/menu_list.csv')

    ingredients = pd.read_csv('app/ingredient_list.csv')

    # 여기서 시간과 날씨대로 먼저 메뉴를 거른다.

    # '시간' 컬럼의 값이 낮인 행들만 선택하여 새로운 DataFrame 생성

    now = datetime.now()
    for _, row in menu.iterrows():
        if 7 <= now.hour < 19:
            menu = menu[menu['시간'] == '낮']
        else:
            menu = menu[menu['시간'] == '밤']

    # 딕셔너리 초기화
    menu_data = {}
    menu_list_dict = {}

    ingredient_list = []

    for _, row in ingredients.iterrows():
        ingredient_list.append(row['재료 이름'])

    for _, row in menu.iterrows():
        
        # 데이터프레임을 순회하며 '이름'과 '재료'를 딕셔너리에 저장
        menu_name = row['메뉴 이름']
        menu_ingredients = list(row['재료'].split(', '))
        menu_data[menu_name] = menu_ingredients

        # 데이터프레임으로 읽어온 메뉴들을 list - dictionary 형태로 변형
        menu = {}
        menu['name'] = row['메뉴 이름']
        menu['ingredients'] = row['재료']
        menu['category'] = row['분류']
        menu_list_dict[menu['name']] = menu

    print("model 로드 전")

    # FastText의 사전 훈련된 워드 임베딩 로드
    model = KeyedVectors.load_word2vec_format('app/cc.ko.300.vec', binary=False, limit=100000)

    print("model 로드 완료")

    # 각 재료에 대한 벡터 생성 (재료가 모델에 없으면 랜덤 벡터 사용)
    embedding_dict = {ingredient: model[ingredient] if ingredient in model else np.random.randn(300) for ingredient in ingredient_list}
    
    return embedding_dict, menu_data, menu_list_dict

def create_user_vector(liked_ingredients, embedding_dict):
    # 각 재료별 출현 횟수 계산
    ingredient_counts = Counter(liked_ingredients)

    # 각 재료별 가중치 적용
    weighted_vectors = [embedding_dict[ingredient] * count 
                        for ingredient, count in ingredient_counts.items()]

    user_vector = np.sum(weighted_vectors, axis=0) / len(liked_ingredients)

    return user_vector

# 콘텐츠 기반 필터링을 통한 추천 (톰슨 샘플링 적용)
def content_based_filtering_thompson(embedding_dict, menu_data, menu_list_dict, liked_ingredients, disliked_ingredients, num_recommendations=10, num_samples=10):
    # 사용자 선호 재료 벡터 생성
    user_vector = create_user_vector(liked_ingredients, embedding_dict)

    # 메뉴별 재료 벡터 생성
    menu_vectors = np.array([np.mean([embedding_dict[ingredient] for ingredient in menu_data[menu]], axis=0)
                             for menu in menu_data])

    # 코사인 유사도 계산
    similarities = cosine_similarity([user_vector], menu_vectors)

    # 싫어하는 재료가 포함된 메뉴에 대한 유사도를 낮춤
    for i, menu in enumerate(menu_data):
        for disliked_ingredient in disliked_ingredients:
            if disliked_ingredient in menu_data[menu]:
                similarities[0, i] *= 0.5

    # 톰슨 샘플링을 이용한 추천 메뉴 선정
    num_menus = similarities.shape[1]
    adjusted_similarities = similarities + 1  # 범위를 0~2로 변경
    alpha = np.clip((adjusted_similarities - adjusted_similarities.min()) / (adjusted_similarities.max() - adjusted_similarities.min()) * 50, 0.01, None) + 1
    beta_param = 51 - alpha
    
    alpha = np.maximum(alpha, 0.01)
    beta_param = np.maximum(beta_param, 0.01)

    # 여러 샘플을 생성하고 이전에 추천한 메뉴를 제외하며 무작위로 추천 메뉴 선택
    samples = np.array([[beta_dist.rvs(a, b) for _ in range(num_samples)] for a, b in zip(alpha.ravel(), beta_param.ravel())])
    recommended_menus = []
    for _ in range(num_recommendations):
        rand_sample_idx = np.random.randint(num_samples)
        recommended_menu_idx = np.argmax(samples[:, rand_sample_idx])

        # 이미 추천한 메뉴에 대한 샘플 값을 낮춤
        samples[recommended_menu_idx] = 0

        recommended_menu = list(menu_data.keys())[recommended_menu_idx]
        recommended_menus.append(recommended_menu)

    return [menu_list_dict[recommended_menus[i]] for i in range(3)][random.randint(0, 2)]


#print(content_based_filtering_thompson(["오리고기", "오리고기", "오리고기", "생선", "파"],["김치", "쯔유"]))