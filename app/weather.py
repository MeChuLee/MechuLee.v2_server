import requests
import datetime
import location_util
import local_properties

location_weather_data = {
    "서울특별시": {"latitude": 37,"longitude": 127,"rainType": "","sky": "흐림","temp": "10"},
    "부산광역시": {"latitude": 35,"longitude": 129,"rainType": "", "sky": "흐림","temp": "10"},
    "대구광역시": {"latitude": 35,"longitude": 128,"rainType": "","sky": "흐림","temp": "10"},
    "인천광역시": {"latitude": 37,"longitude": 126,"rainType": "","sky": "흐림","temp": "10"},
    "광주광역시": {"latitude": 35,"longitude": 126,"rainType": "","sky": "흐림","temp": "10"},
    "대전광역시": {"latitude": 36,"longitude": 127,"rainType": "","sky": "흐림","temp": "10"},
    "울산광역시": {"latitude": 35,"longitude": 129,"rainType": "", "sky": "흐림", "temp": "10"},
    "세종특별자치시": {"latitude": 36,"longitude": 127,"rainType": "", "sky": "흐림", "temp": "10"},
    "경기도": {"latitude": 37,"longitude": 127,"rainType": "", "sky": "흐림", "temp": "10"},
    "강원도": {"latitude": 37,"longitude": 128,"rainType": "", "sky": "흐림", "temp": "10"},
    "충청북도": {"latitude": 36,"longitude": 127,"rainType": "", "sky": "흐림", "temp": "10"},
    "충청남도": {"latitude": 36,"longitude": 126,"rainType": "", "sky": "흐림", "temp": "10"},
    "전라북도": {"latitude": 35,"longitude": 127,"rainType": "", "sky": "흐림", "temp": "10"},
    "전라남도": {"latitude": 34,"longitude": 126,"rainType": "", "sky": "흐림", "temp": "10"},
    "경상북도": {"latitude": 36,"longitude": 128,"rainType": "", "sky": "흐림", "temp": "10"},
    "경상남도": {"latitude": 35,"longitude": 128,"rainType": "", "sky": "흐림", "temp": "10"},
    "제주특별자치도": {"latitude": 33,"longitude": 126,"rainType": "", "sky": "흐림", "temp": "10"},
}


def loading_location_weather_data():
    for location_name in location_weather_data:
        location_info = location_weather_data[location_name]
        latitude = location_info["latitude"]
        longitude = location_info["longitude"]

        for _ in range(10):
            try:
                # 딕셔너리에 있는 value 수 만큼 api를 받아와서 날씨 정보에 저장한다.
                rain_type, sky, temp = get_weatherinfo_from_api(latitude, longitude)
                break
            except Exception:
                print("실패, 재시도")
                continue  # 다음 시도로 넘어감
        
        location_info["rainType"] = rain_type
        location_info["sky"] = sky
        location_info["temp"] = temp

        print(location_info)
    print("날씨 세팅 끝!")


def get_weatherinfo_by_location(admin_area):
    if admin_area in location_weather_data: 
        location_info = location_weather_data[admin_area]

        rain_type = location_info["rainType"]
        sky = location_info["sky"]
        temp = location_info["temp"]

        return rain_type, sky, temp
    else:
        #해당 도시 이름이 딕셔너리에 없는 경우 None을 반환
        print("연결안됨")
        return None, None, None


def calculate_one_hour_ago():
    # 현재 날짜와 시간을 가져옴
    current_datetime = datetime.datetime.now()

    # 1시간 전의 시간을 계산
    one_hour_ago = current_datetime - datetime.timedelta(hours=1)

    # 날짜를 YYYYMMDD 형식으로 포맷팅
    one_hour_ago_date = one_hour_ago.strftime("%Y%m%d")

    # 시간을 HHMM 형식으로 포맷팅
    one_hour_ago_time = one_hour_ago.strftime("%H%M")

    return one_hour_ago_date, one_hour_ago_time


def get_weatherinfo_from_api(latitude, longitude):
    # 1시간 전의 시간을 먼저 가져온다.
    one_hour_ago_date, one_hour_ago_time = calculate_one_hour_ago()

    # LGT, PTY, RN1, SKY, T1H, REH, UUU, VVV, VEC, WSD 10가지 카테고리(6가지 fcstTime)를 전부 출력하려면 한번에 60개를 조회해야함
    # 필요한건 기온까지이기때문에 30개까지만 조회해도 필요한 PTY, SKY, T1H값을 전부 가져올 수 있음

    # 서비스키(decoding)
    serviceKey = local_properties.weather_key
    pageNo = '1'    # 페이지 번호
    numOfRows = '30'    # 한 페이지 결과 수
    dataType = 'JSON'   # 응답자료형식
    base_date = one_hour_ago_date  # 발표일자
    base_time = one_hour_ago_time  # 발표시각
    nx, ny = location_util.set_location(latitude, longitude)

    weather_data = {
        "rainType": "",  # 강수형태
        "sky": "",  # 하늘상태
        "temp": ""   # 기온
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

    index = 0
    # "item" 항목이 리스트인 경우를 가정하여 출력
    for item in data['response']['body']['items']['item']:
        category = item['category']
        fcstValue = item['fcstValue']
        
        if index % 6 == 0 :
            if category == 'PTY' and fcstValue == '0':
                weather_data["rainType"] = ""
            elif category == 'PTY' and fcstValue == '1':
                weather_data["rainType"] = "비"
            elif category == 'PTY' and fcstValue == '2':
                weather_data["rainType"] = "비/눈"
            elif category == 'PTY' and fcstValue == '3':
                weather_data["rainType"] = "눈"
            elif category == 'PTY' and fcstValue == '5':
                weather_data["rainType"] = "빗방울"
            elif category == 'PTY' and fcstValue == '6':
                weather_data["rainType"] = "빗방울눈날림"
            elif category == 'PTY' and fcstValue == '7':
                weather_data["rainType"] = "눈날림"   
            elif category == 'SKY' and fcstValue == '1':
                weather_data["sky"] = "맑음"
            elif category == 'SKY' and fcstValue == '3':
                weather_data["sky"] = "구름많음"
            elif category == 'SKY' and fcstValue == '4':
                weather_data["sky"] = "흐림"                 
            elif category == 'T1H':
                weather_data["temp"] = fcstValue

        index+=1    

    return weather_data["rainType"], weather_data["sky"], weather_data["temp"] # weather_data 딕셔너리를 반환
