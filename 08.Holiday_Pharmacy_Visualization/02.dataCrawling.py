### Step 04 - 휴일지킴이 약국 크롤링 및 데이터 셋 만들기
# - 휴일지킴이 약국(http: // www.pharm114. or.kr) 에서 크롤링 하려 했으나 웹사이트의 리퀘스트 요청 거부로
# 인해 사용이 불가능해졌습니다
# - 이에 따라 공공데이터 포털의 전국 명절 비상 진료기관 정보 조회 서비스 API 사용신청을 하였고
# 이를 활용하여 크롤링 했습니다.
# - 참고: 국림중앙의료원 기준을 따랐고 약국정보조회서비스 API의 Document를 따라 휴일의 기준을
# 토, 일, 공휴일(국가공휴일)의 항목은 dutyTime6s, dutyTime7s, dutyTime8s 을 사용했습니다.
# - 참고 document: https: // www.data.go.kr / dataset / 15000576 / openapi.do

# %%
import pandas as pd
import json
from tqdm import tqdm
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib import parse

BASE_PATH = './data/'

pharm_data_clear = pd.read_csv(BASE_PATH + 'seoul_pharm_clean.csv', thousands=',', encoding='utf-8')

query_pharm_name = pharm_data_clear["사업장명"]
query_pharm_district = pharm_data_clear["구별"]

# %%

# 공공데이터 전국 약국 정보 조회 서비스 API에 있는 약국 오픈 정보(국립중앙의료원에 등록된 약국 정보)
# 이 api의 원리가 근처의 약국도 다 조사하기 때문에 numOfRows=1 값으로 두면 그 약국 네이밍만 찾습니다

with open('./secrets.json') as f:
    key_file = json.loads(f.read())

emer_pharm_key = key_file["EMER_PHARM_KEY"]

pharm_name = []
pharm_sat_start = []
pharm_sat_end = []
pharm_sun_start = []
pharm_sun_end = []
pharm_holiday_start = []
pharm_holiday_end = []

for i in tqdm(range(len(query_pharm_name))):
    url = parse.urlparse(
        "http://apis.data.go.kr/B552657/ErmctInsttInfoInqireService/getParmacyListInfoInqire?serviceKey=" +
        emer_pharm_key +
        "&Q0=서울특별시&Q1=" +
        query_pharm_district[i] +
        "&QT=1&QN=" +
        query_pharm_name[i] +
        "&ORD=NAME&pageNo=1&numOfRows=1")
    url_source = "http://apis.data.go.kr/B552657/ErmctInsttInfoInqireService/getParmacyListInfoInqire?"
    query = parse.parse_qs(url.query)
    url_encode = parse.urlencode(query, doseq=True)

    real_url = str(url_source) + str(url_encode)

    page = urlopen(real_url)

    soup = BeautifulSoup(page, "html.parser")

    # 약국명 찾기
    try:
        top_right = soup.find("dutyname").text
        pharm_name.append(top_right)
    except AttributeError as e:
        pharm_name.append(None)

    # 토요일 오픈 정보 찾기
    try:
        find_sat_s = soup.find("dutytime6s").text
        pharm_sat_start.append(find_sat_s)
    except AttributeError as e:
        pharm_sat_start.append(None)

    # 토요일 종료 정보 찾기
    try:
        find_sat_c = soup.find("dutytime6c").text
        pharm_sat_end.append(find_sat_c)
    except AttributeError as e:
        pharm_sat_end.append(None)

    # 일요일 오픈 정보 찾기
    try:
        find_sun_s = soup.find("dutytime7s").text
        pharm_sun_start.append(find_sun_s)
    except AttributeError as e:
        pharm_sun_start.append(None)

    # 일요일 종료 정보 찾기
    try:
        find_sun_c = soup.find("dutytime7c").text
        pharm_sun_end.append(find_sun_c)
    except AttributeError as e:
        pharm_sun_end.append(None)

    # 공휴일 시작 정보 찾기
    try:
        find_holiday_s = soup.find("dutytime8s").text
        pharm_holiday_start.append(find_holiday_s)
    except AttributeError as e:
        pharm_holiday_start.append(None)

    # 공휴일 종료 정보 찾기
    try:
        find_holiday_c = soup.find("dutytime8c").text
        pharm_holiday_end.append(find_holiday_c)
    except AttributeError as e:
        pharm_holiday_end.append(None)


# %%

seoul_pharm = pd.DataFrame({'약국명': pharm_name,
                            '토요일 시작': pharm_sat_start,
                            '토요일 종료': pharm_sat_end,
                            '일요일 시작': pharm_sun_start,
                            '일요일 종료': pharm_sun_end,
                            '공휴일 시작': pharm_holiday_start,
                            '공휴일 종료': pharm_holiday_end},
                           index=range(len(pharm_name)))

seoul_pharm.insert(0, '위도', pharm_data_clear['위도'])
seoul_pharm.insert(0, '경도', pharm_data_clear['경도'])
seoul_pharm.insert(0, '구별', pharm_data_clear['구별'])

#seoul_pharm['위도'] = (pharm_data_clear['위치정보(X)'])
#seoul_pharm['경도'] = (pharm_data_clear['위치정보(Y)'])
#seoul_pharm['구별'] = (pharm_data_clear['구별'])


# 약국명에 None 값이 있는 경우 폐업이 되었거나 정보에 등록되지 않은 약국이기 때문에 삭제 한다.
seoul_pharm = seoul_pharm.dropna(subset=['약국명'])
seoul_pharm = seoul_pharm.reset_index(drop=True)

# %%

seoul_pharm = seoul_pharm[['약국명',
                           '토요일 시작',
                           '토요일 종료',
                           '일요일 시작',
                           '일요일 종료',
                           '공휴일 시작',
                           '공휴일 종료',
                           '위도',
                           '경도',
                           '구별']]

# %%
# 정리된 약국별 휴일 오픈 csv 저장
seoul_pharm.to_csv(BASE_PATH + "seoul_pharm_open_data.csv", encoding='utf-8-sig', sep=',')
seoul_pharm = pd.read_csv(BASE_PATH + "seoul_pharm_open_data.csv", thousands=',', encoding='utf-8')

# %%
## 토요일에 오픈하는 것만 찾기
seoul_pharm_sat = seoul_pharm[seoul_pharm["토요일 시작"] >= 0]

seoul_pharm_sat = pd.DataFrame({'약국명': seoul_pharm_sat["약국명"],
                                '토요일 시작': seoul_pharm_sat["토요일 시작"],
                                '토요일 종료': seoul_pharm_sat["토요일 종료"],
                                '위도': seoul_pharm_sat["위도"],
                                '경도': seoul_pharm_sat["경도"],
                                '구별': seoul_pharm_sat["구별"]})

# 토요일 오픈 약국만 csv 저장 및 로드
seoul_pharm_sat = seoul_pharm_sat.dropna(subset=['위도', '경도'])
seoul_pharm_sat = seoul_pharm_sat.reset_index(drop=True)
seoul_pharm_sat.to_csv(BASE_PATH + "seoul_pharm_is_open_sat.csv", encoding='utf-8-sig', sep=',')

# %%
## 일요일에 오픈하는 것만 찾기
seoul_pharm_sun = seoul_pharm[seoul_pharm["일요일 시작"] >= 0]

seoul_pharm_sun = pd.DataFrame({'약국명': seoul_pharm_sun["약국명"],
                                '일요일 시작': seoul_pharm_sun["일요일 시작"],
                                '일요일 종료': seoul_pharm_sun["일요일 종료"],
                                '위도': seoul_pharm_sun["위도"],
                                '경도': seoul_pharm_sun["경도"],
                                '구별': seoul_pharm_sun["구별"]})

# 일요일 오픈 약국만 csv 저장 및 로드
seoul_pharm_sun = seoul_pharm_sun.dropna(subset=['위도', '경도'])
seoul_pharm_sun = seoul_pharm_sun.reset_index(drop=True)
seoul_pharm_sun.to_csv(BASE_PATH + "seoul_pharm_is_open_sun.csv", encoding='utf-8-sig', sep=',')

# %%
## 공휴일에 오픈하는 것만 찾기
seoul_pharm_holi = seoul_pharm[seoul_pharm["공휴일 시작"] >= 0]

seoul_pharm_holi = pd.DataFrame({'약국명': seoul_pharm_holi["약국명"],
                                 '공휴일 시작': seoul_pharm_holi["공휴일 시작"],
                                 '공휴일 종료': seoul_pharm_holi["공휴일 종료"],
                                 '위도': seoul_pharm_holi["위도"],
                                 '경도': seoul_pharm_holi["경도"],
                                 '구별': seoul_pharm_holi["구별"]})

# 공휴일 오픈 약국만 csv 저장 및 로드
seoul_pharm_holi = seoul_pharm_holi.dropna(subset=['위도', '경도'])
seoul_pharm_holi = seoul_pharm_holi.reset_index(drop=True)
seoul_pharm_holi.to_csv(BASE_PATH + "seoul_pharm_is_open_holi.csv", encoding='utf-8-sig', sep=',')