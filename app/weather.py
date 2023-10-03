import requests
import datetime
import location_util

def calculate_one_hour_ago():
    # 현재 날짜와 시간을 가져옴
    current_datetime = datetime.datetime.now()

    # 1시간 전의 시간을 계산
    one_hour_ago = current_datetime - datetime.timedelta(hours=1)

    # 날짜를 YYYYMMDD 형식으로 포맷팅
    one_hour_ago_date = one_hour_ago.strftime("%Y%m%d")

    # 시간을 HHMM 형식으로 포맷팅
    one_hour_ago_time = one_hour_ago.strftime("%H%M")

    print("1시간 전 시간:", one_hour_ago_time)

    return one_hour_ago_date, one_hour_ago_time

def get_temperature_from_api():

    # 1시간 전의 시간을 먼저 가져온다.
    one_hour_ago_date, one_hour_ago_time = calculate_one_hour_ago()

    # 서비스키(decoding)
    serviceKey = 'Ux3PVlwB8oN9L6Vj/tQUyxOw2lE+EgBDF9cRJMC1QjOYRLNycIvKbjTNF0PVIdtNRIr1SUNi07syDl7VaNLXkw==' 
    pageNo = '1'    # 페이지 번호
    numOfRows = '30'    # 한 페이지 결과 수
    dataType = 'JSON'   # 응답자료형식
    base_date = one_hour_ago_date  # 발표일자
    base_time = one_hour_ago_time  # 발표시각

    #nx, ny = location_util.dfs_xy_conv(latitude, longitude) # 위도,경도 x-y좌표 변환
    #print(nx, ny)

    #예시좌표
    nx = '55'   # 예보지점 X좌표
    ny = '127'  # 예보지점 Y좌표

    weather_data = {
        "PTY": "",  # 강수형태
        "SKY": "",  # 하늘상태
        "T1H": ""   # 기온
    }

    # 초단기 예보조회
    url = 'http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst'

    params ={'serviceKey' : serviceKey, 
            'pageNo' : pageNo, 
            'numOfRows' : numOfRows, 
            'dataType' : dataType, 
            'base_date' : base_date, 
            'base_time' : base_time, 
            'nx' : nx, 
            'ny' : ny}

    # Api 요청
    response = requests.get(url, params=params)

    data = response.json()  # JSON 데이터를 파이썬 객체로 로드합니다.

    # "item" 항목이 리스트인 경우를 가정하여 출력
    for item in data['response']['body']['items']['item']:
        category = item['category']
        fcstValue = item['fcstValue']
        
        index = 0

        if index % 6 == 0 :
            if category == 'PTY' and fcstValue == '0':
                weather_data["PTY"] = ""
            elif category == 'PTY' and fcstValue == '1':
                weather_data["PTY"] = "비"
            elif category == 'PTY' and fcstValue == '2':
                weather_data["PTY"] = "비/눈"
            elif category == 'PTY' and fcstValue == '3':
                weather_data["PTY"] = "눈"
            elif category == 'PTY' and fcstValue == '5':
                weather_data["PTY"] = "빗방울"
            elif category == 'PTY' and fcstValue == '6':
                weather_data["PTY"] = "빗방울눈날림"
            elif category == 'PTY' and fcstValue == '7':
                weather_data["PTY"] = "눈날림"   
            elif category == 'SKY' and fcstValue == '1':
                weather_data["SKY"] = "맑음"
            elif category == 'SKY' and fcstValue == '3':
                weather_data["SKY"] = "구름많음"
            elif category == 'SKY' and fcstValue == '4':
                weather_data["SKY"] = "흐림"                 
            elif category == 'T1H':
                weather_data["T1H"] = fcstValue

        index+=1    
        #print(json.dumps(item, indent=4))  # 각 항목을 들여쓰기를 추가하여 출력합니다    

    print(weather_data["PTY"], weather_data["SKY"], weather_data["T1H"])

    return weather_data # weather_data 딕셔너리를 반환

# LGT, PTY, RN1, SKY, T1H, REH, UUU, VVV, VEC, WSD 10가지 카테고리(6가지 fcstTime)를 전부 출력하려면 한번에 60개를 조회해야함
# 필요한건 기온까지이기때문에 30개까지만 조회해도 필요한 PTY, SKY, T1H값을
# 전부 가져올 수 있음

# # 함수 호출하여 반환 값을 변수에 저장
# temperature_value = get_temperature_from_api()
# print(temperature_value)

