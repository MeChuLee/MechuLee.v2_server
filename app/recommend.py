import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
from collections import Counter
from scipy.stats import beta as beta_dist


def read_meun_data():
    # menu_list.csv 파일을 데이터프레임으로 읽어옴
    menu = pd.read_csv('menu_list.csv')

    # 딕셔너리 초기화
    menu_data = {}
    ingredients = set()

    # 데이터프레임을 순회하며 '이름'과 '재료'를 딕셔너리에 저장
    for index, row in menu.iterrows():
        menu_name = row['메뉴 이름']
        menu_ingredients = list(row['재료'].split(', '))
        menu_data[menu_name] = menu_ingredients
        ingredients.update(menu_ingredients)

    # ingredients = ['밥', '김치', '고추장', '된장', '두부', '양파', '고춧가루', '대파', '계란']
    embedding_dict = {ingredient: np.random.randn(10) for ingredient in ingredients}

    return embedding_dict, menu_data

def create_user_vector(liked_ingredients, embedding_dict):
    # 좋아하는 재료들의 출현 횟수 계산
    ingredient_counts = Counter(liked_ingredients)
    total_count = sum(ingredient_counts.values())

    # 가중치를 적용한 벡터 계산
    weighted_vectors = [embedding_dict[ingredient] * (ingredient_counts[ingredient] / total_count)
                        for ingredient in ingredient_counts]

    user_vector = np.sum(weighted_vectors, axis=0)
    return user_vector

# 콘텐츠 기반 필터링을 통한 추천 (톰슨 샘플링 적용)
def content_based_filtering_thompson(liked_ingredients, disliked_ingredients, num_recommendations=10, num_samples=10):
    embedding_dict, menu_data = read_meun_data()

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

    return recommended_menus
