# %%
# - 인구밀집도에 따른 휴일지킴이 약국 현황 분석

### * 작성 : 컴퓨터공학과 박동수(20154339)
### * 참고 자료 : 2017 서울시 빅캠시상시공모전 -  휴일지킴이약국제 효율화 필요성(https://bit.ly/2Odh2uL)

# %%
## Step 01 - 데이터 전처리

# csv 데이터 처리하기 위한 라이브러리 import
import folium
import numpy as np
import pandas as pd

# %%
BASE_PATH = './data/'
# 데이터 셋 불러오기
pharm_coord = pd.read_csv(BASE_PATH + 'seoul_pharm_raw.csv', thousands=',', encoding='utf-8')

# 필요 없는 데이터 컬럼 삭제
del pharm_coord['폐업일자']
del pharm_coord['휴업시작일자']
del pharm_coord['휴업종료일자']
del pharm_coord['소재지면적']
del pharm_coord['소재지우편번호']
del pharm_coord['재개업일자']

# %%

# 인허가구분명의 한약국 네이밍 삭제
pharm_coord = pharm_coord[pharm_coord.인허가구분명 != '한약국']
pharm_coord.head()

# 구별 데이터 컬럼 추가
pharm_coord['구별'] = pharm_coord['도로명전체주소'].str.split(' ').str[1]

# 도로명 전체 주소 내용 수정
pharm_coord['도로명전체주소'] = (pharm_coord['도로명전체주소'].str.split(' ').str[0] +
                                 pharm_coord['도로명전체주소'].str.split(' ').str[1] +
                                 pharm_coord['도로명전체주소'].str.split(' ').str[2] +
                                 pharm_coord['도로명전체주소'].str.split(' ').str[3])


# 전처리된 데이터 저장 및 로드
pharm_coord.to_csv(BASE_PATH + "seoul_pharm_clear.csv", encoding='utf-8-sig', sep=',')
pharm_coord = pd.read_csv(BASE_PATH + 'seoul_pharm_clear.csv', thousands=',', encoding='utf-8')

# %% md
### Step 02 - 구글 맵스 geocode를 이용한 위도 경도 다시 구하기

# 구글 맵스 이용
import googlemaps
import json
from tqdm import tqdm

# %%
# Secret Key 로드
with open('./secrets.json') as f:
    key_file = json.loads(f.read())

# GMAP 키 로드
gmaps_key = key_file["GMAP_KEY"]
gmaps = googlemaps.Client(key=gmaps_key)

# %%
# 도로명 전체 주소를 drag_location_name 배열에 추가
pharm_address = []

for name in pharm_coord['도로명전체주소']:
    pharm_address.append(name)

# %%

# gmaps.geocode를 이용한 도로명 주소의 약국 장소 위도 경도 확인
pharm_coord_lat = []
pharm_coord_lng = []

for i in tqdm(range(len(pharm_address))):
    tmp = gmaps.geocode(pharm_address[i], language='ko')
    tmp_loc = tmp[0].get("geometry")

    pharm_coord_lat.append(tmp_loc['location']['lat'])
    pharm_coord_lng.append(tmp_loc['location']['lng'])

## 좌표를 저장할 데이터 프레임 생성
pharm_coord = pd.DataFrame({'x축': pharm_coord_lat, 'y축': pharm_coord_lng}, index=pharm_coord_lat)

# 백업을 위해 위도 경도를 따로 데이터프레임에 저장하고 csv로 저장하였습니다.
pharm_coord.to_csv(BASE_PATH + "seoul_pharm_coord.csv", encoding='utf-8-sig', sep=',', index=False)
pharm_coord = pd.read_csv(BASE_PATH + 'seoul_pharm_coord.csv', thousands=',', encoding='utf-8')

# %% md

### Step 03 - 서울시 약국 현황 지도 시각화 처리

import matplotlib.pyplot as plt
import seaborn as sns
from IPython.display import set_matplotlib_formats

# windows 한글 폰트 문제 해결
plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)
set_matplotlib_formats('retina')

plt.figure(figsize=(16, 8))
sns.countplot(data=pharm_coord, x="구별")
plt.title("서울시 전체 약국 개수")
plt.show()

# %%
# seaborn으로 그리기
# 원래는 folium map으로 처리하려고 했으나 map의 개수가 3300개 이상이 되면 folium이
# 정상적으로 처리가 되지 않아서 seaborn으로 형태만 잡았습니다.
plt.figure(figsize=(10, 8))
sns.scatterplot(data=pharm_coord[["y축", "x축"]], x='y축', y='x축')

# %% md

### Step 04 - 휴일지킴이 약국 크롤링 및 데이터 셋 만들기
# - 휴일지킴이 약국(http: // www.pharm114. or.kr) 에서 크롤링 하려 했으나 웹사이트의 리퀘스트 요청 거부로
# 인해 사용이 불가능해졌습니다
# - 이에 따라 공공데이터 포털의 전국 명절 비상 진료기관 정보 조회 서비스 API 사용신청을 하였고
# 이를 활용하여 크롤링 했습니다.
# - 참고: 국림중앙의료원 기준을 따랐고 약국정보조회서비스 API의 Document를 따라 휴일의 기준을
# 토, 일, 공휴일(국가공휴일)의 항목은 dutyTime6s, dutyTime7s, dutyTime8s 을 사용했습니다.
# - 참고 document: https: // www.data.go.kr / dataset / 15000576 / openapi.do

# %%
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib import parse

query_pharm_name = pharm_coord["사업장명"]
query_pharm_district = pharm_coord["구별"]

# %%

# 공공데이터 전국 약국 정보 조회 서비스 API에 있는 약국 오픈 정보(국립중앙의료원에 등록된 약국 정보)
# 이 api의 원리가 근처의 약국도 다 조사하기 때문에 numOfRows=1 값으로 두면 그 약국 네이밍만 찾습니다

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
        "http://apis.data.go.kr/B552657/ErmctInsttInfoInqireService/getParmacyListInfoInqire?serviceKey="
        + emer_pharm_key
        + "%3D%3D&Q0=서울특별시&Q1="
        + query_pharm_district[i]
        + "&QT=1&QN="
        + query_pharm_name[i]
        + "&ORD=NAME&pageNo=1&numOfRows=1")
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

seoul_pharm['위도'] = (pharm_coord['x축'])
seoul_pharm['경도'] = (pharm_coord['y축'])
seoul_pharm['구별'] = (pharm_coord['구별'])


# 약국명에 None 값이 있는 경우 폐업이 되었거나 정보에 등록되지 않은 약국이기 때문에 삭제 한다.
seoul_pharm = seoul_pharm.dropna(subset=['약국명'])
seoul_pharm = seoul_pharm.reset_index(drop=True)

# %%

seoul_pharm = seoul_pharm[['번호',
                           '약국명',
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
seoul_pharm = seoul_pharm.set_index("번호")
seoul_pharm.to_csv(BASE_PATH + "seoul_pharm.csv", encoding='utf-8-sig', sep=',')
seoul_pharm = pd.read_csv(BASE_PATH + "seoul_pharm.csv", thousands=',', encoding='utf-8')

# %%
## 토요일에 오픈하는 것만 찾기
seoul_pharm_sat = seoul_pharm[seoul_pharm["토요일 시작"] >= "0"]

seoul_pharm_sat = pd.DataFrame({'약국명': seoul_pharm_sat["약국명"],
                                    '토요일 시작': seoul_pharm_sat["토요일 시작"],
                                    '토요일 종료': seoul_pharm_sat["토요일 종료"],
                                    '위도': seoul_pharm_sat["위도"],
                                    '경도': seoul_pharm_sat["경도"],
                                    '구별': seoul_pharm_sat["구별"]})

# 토요일 오픈 약국만 csv 저장 및 로드
seoul_pharm_sat.to_csv(BASE_PATH + "seoul_pharm_sat.csv", encoding='utf-8-sig', sep=',')
seoul_pharm_sat = pd.read_csv(BASE_PATH + 'seoul_pharm_sat.csv', thousands=',', encoding='utf-8')
seoul_pharm_sat = seoul_pharm_sat.set_index("번호")

# %%
## 일요일에 오픈하는 것만 찾기
seoul_pharm_sun = seoul_pharm[seoul_pharm["일요일 시작"] >= "0"]

seoul_pharm_sun = pd.DataFrame({'약국명': seoul_pharm_sun["약국명"],
                                '일요일 시작': seoul_pharm_sun["일요일 시작"],
                                '일요일 종료': seoul_pharm_sun["일요일 종료"],
                                '위도': seoul_pharm_sun["위도"],
                                '경도': seoul_pharm_sun["경도"],
                                '구별': seoul_pharm_sun["구별"]})

# 일요일 오픈 약국만 csv 저장 및 로드
seoul_pharm_sun.to_csv(BASE_PATH + "seoul_pharm_sun.csv", encoding='utf-8-sig', sep=',')
seoul_pharm_sun = pd.read_csv(BASE_PATH + 'seoul_pharm_sun.csv', thousands=',', encoding='utf-8')
seoul_pharm_sun = seoul_pharm_sun.set_index("번호")

# %%
## 공휴일에 오픈하는 것만 찾기
seoul_pharm_holi = seoul_pharm[seoul_pharm["공휴일 시작"] >= "0"]

seoul_pharm_holi = pd.DataFrame({'약국명': seoul_pharm_holi["약국명"],
                                 '공휴일 시작': seoul_pharm_holi["공휴일 시작"],
                                 '공휴일 종료': seoul_pharm_holi["공휴일 종료"],
                                 '위도': seoul_pharm_holi["위도"],
                                 '경도': seoul_pharm_holi["경도"],
                                 '구별': seoul_pharm_holi["구별"]})

# 공휴일 오픈 약국만 csv 저장 및 로드
seoul_pharm_holi.to_csv(BASE_PATH + "seoul_pharm_holi.csv", encoding='utf-8-sig', sep=',')
seoul_pharm_holi = pd.read_csv(BASE_PATH + 'seoul_pharm_holi.csv', thousands=',', encoding='utf-8')
seoul_pharm_holi = seoul_pharm_holi.set_index("번호")

# %%
### Step 05 - 휴일 오픈 약국 시각화 처리

# 토요일 확인
print("토요일 영업 약국수: " + len(seoul_pharm_sat['구별']))
print(seoul_pharm_sat['구별'].unique())
print(seoul_pharm_sat['구별'].value_counts())

# %%
# 토요일 오픈 약국 막대리스트
plt.figure(figsize=(16, 8))
sns.countplot(data=seoul_pharm_sat, x="구별")
plt.title("서울시 토요일 운영 약국 개수")
plt.show()

# seaborn으로 그리기
plt.figure(figsize=(10, 8))
sns.scatterplot(data=seoul_pharm_sat[["경도", "위도"]], x='경도', y='위도')

# %%
# geo json 파일 불러오기
geo_path = BASE_PATH+'geo_seoul.json'
geo_str = json.load(open(geo_path, encoding='utf-8'))

# 토요일 오픈 약국 지도 시각화
map = folium.Map(location=[37.571419, 127.006855], zoom_start=11)

for n in seoul_pharm_sat.index:
    folium.CircleMarker([seoul_pharm_sat['위도'][n], seoul_pharm_sat['경도'][n]], radius=2).add_to(map)

map.save('./map/seoul_pharm_sat_markers.html')

# %%
# 토요일 오픈 개수 map 확인
seoul_pharm_sat_coord = pd.read_csv(BASE_PATH + 'seoul_pharm_sat.csv', thousands=',', encoding='utf-8')
map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

map.choropleth(geo_data=geo_str,
               data=seoul_pharm_sat_coord,
               columns=['구별', '개수'],
               fill_color='YlGnBu',  # PuRd, YlGnBu
               key_on='feature.id')
map.save('./map/seoul_pharm_sat_district.html')

# %%
# 일요일 확인
print("일요일 영업 약국수: " + len(seoul_pharm_sun['구별']))
print(seoul_pharm_sun['구별'].unique())
print(seoul_pharm_sun['구별'].value_counts())

# 일요일 오픈 약국 막대리스트
plt.figure(figsize=(16, 8))
sns.countplot(data=seoul_pharm_sun, x="구별")
plt.title("서울시 일요일 운영 약국 개수")
plt.show()

# %%
# 일요일 오픈 약국 지도 시각화
map = folium.Map(location=[37.571419, 127.006855], zoom_start=11)

for n in seoul_pharm_sun.index:
    folium.CircleMarker([seoul_pharm_sun['위도'][n], seoul_pharm_sun['경도'][n]], radius=2).add_to(map)

map.save('./map/seoul_pharm_sun_markers.html')

# %%
# 일요일 오픈 개수 map 확인
seoul_pharm_sun_coord = pd.read_csv(BASE_PATH + 'seoul_pharm_sun.csv', thousands=',', encoding='utf-8')
map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

map.choropleth(geo_data=geo_str,
               data=seoul_pharm_sun_coord,
               columns=['구별', '개수'],
               fill_color='YlGnBu',  # PuRd, YlGnBu
               key_on='feature.id')

map.save('./map/seoul_pharm_sun_district.html')

# %%
# 공휴일 확인
print("공휴일 영업 약국수: " + len(seoul_pharm_holi['구별']))
print(seoul_pharm_holi['구별'].unique())
print(seoul_pharm_holi['구별'].value_counts())

# 공휴일 오픈 약국 막대리스트
plt.figure(figsize=(16, 8))
sns.countplot(data=seoul_pharm_holi, x="구별")
plt.title("서울시 공휴일 운영 약국 개수")
plt.show()

# %%
# 공휴일 오픈 약국 지도 시각화
map = folium.Map(location=[37.571419, 127.006855], zoom_start=11)

for n in seoul_pharm_holi.index:
    folium.CircleMarker([seoul_pharm_holi['위도'][n], seoul_pharm_holi['경도'][n]], radius=2).add_to(map)

map.save('./map/seoul_pharm_holi_markers.html')

# %%
# 공휴일 오픈 개수 map 확인
seoul_pharm_holi_coord = pd.read_csv(BASE_PATH + 'seoul_pharm_holi.csv', thousands=',', encoding='utf-8')
map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

map.choropleth(geo_data=geo_str,
               data=seoul_pharm_holi_coord,
               columns=['구별', '개수'],
               fill_color='YlGnBu',  # PuRd, YlGnBu
               key_on='feature.id')

map.save('./map/seoul_pharm_holi_district.html')

# %% md

### Step 06 - 휴일 약국 취약 지역 확인
# - 기준 측정: 국제 제약 연맹(FIP)와 WHO의 통계에 따르면(2017년 기준) 건강을 위한 필요한 약사의 수는
# 인구 수 1 만명당 약 5 명이 있어야 합니다.
# (참고 자료: https: // www.fip.org / files / fip / publications / 2017-09-Pharmacy_at_a_Glance-2015-2017.pdf)
# 하지만 이것은 2017년 기준이고 2019년이 지난 지금 최신 자료가 없으므로 예상을 해야 합니다.
# 즉 인구 수가 2017 년에 비해 늘었으므로 이에 대비한 인구 1 만명당 약사 수는 6 명으로 책정을 하였고
# 약사 1 명당 약국의 개수를 1개로 잡는다면 인구 1 만명당 약국의 수는 6 개라는 기준을 책정하였습니다.
# 분석 결과 값과 실제와는 다소 차이가 있으므로 참고용으로 확인하면 됩니다.

# %%

# 토요일 확인
# 구별로 공휴일에 약국을 운영하는 개수를 정리해 둔 csv를 불러온다
# 비례 값 계산 식 = 약국 운영 수 / ((인구수/10000) * 6)
seoul_drag_sat_people = pd.read_csv(BASE_PATH+'seoul_pharm_sat_people.csv', thousands=',', encoding='utf-8')
seoul_drag_sat_people.tail()

# %%

# 토요일 오픈 개수 비례 값으로 지도 확인
map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

map.choropleth(geo_data=geo_str,
               data=seoul_drag_sat_people,
               columns=['구별', '비례 값'],
               fill_color='YlGnBu',  # PuRd, YlGnBu
               key_on='feature.id')
map

# %%

# index 다시 설정
seoul_drag_sat_people = seoul_drag_sat_people.set_index("구별")

# %%

seoul_drag_sat_people.tail()

# %%

plt.figure(figsize=(6, 6))
plt.scatter(seoul_drag_sat_people['인구수'], seoul_drag_sat_people['비례 값'], s=50)
plt.xlabel('인구수')
plt.ylabel('비례 값')
plt.grid()
plt.show()

# %%

fx = np.linspace(100000, 700000, 10)

# %%

plt.figure(figsize=(10, 10))
plt.scatter(seoul_drag_sat_people['인구수'], seoul_drag_sat_people['비례 값'], s=50)
plt.plot(fx, [1, 1, 1, 1, 1, 1, 1, 1, 1, 1], lw=3, color='g')
n = 0
for n in range(0, 25):
    plt.text(seoul_drag_sat_people['인구수'][n] * 1.02, seoul_drag_sat_people['비례 값'][n] * 0.98,
             seoul_drag_sat_people.index[n], fontsize=12)
plt.xlabel('인구수')
plt.ylabel('비례 값')
plt.grid()
plt.show()

# %%

# 일요일 확인
# 구별로 공휴일에 약국을 운영하는 개수를 정리해 둔 csv를 불러온다
# 비례 값 계산 식 = 약국 운영 수 / ((인구수/10000) * 6)
seoul_drag_sun_people = pd.read_csv(BASE_PATH+'seoul_pharm_sun_people.csv', thousands=',', encoding='utf-8')
seoul_drag_sun_people.tail()
# %%

# 일요일 오픈 개수 비례 값으로 지도 확인
map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

map.choropleth(geo_data=geo_str,
               data=seoul_drag_sun_people,
               columns=['구별', '비례 값'],
               fill_color='YlGnBu',  # PuRd, YlGnBu
               key_on='feature.id')
map

# %%

# index 다시 설정
seoul_drag_sun_people = seoul_drag_sun_people.set_index("구별")

# %%

seoul_drag_sun_people.tail()

# %%

plt.figure(figsize=(10, 10))
plt.scatter(seoul_drag_sun_people['인구수'], seoul_drag_sun_people['비례 값'], s=50)
n = 0
for n in range(0, 25):
    plt.text(seoul_drag_sun_people['인구수'][n] * 1.02, seoul_drag_sun_people['비례 값'][n] * 0.98,
             seoul_drag_sun_people.index[n], fontsize=11)
plt.xlabel('인구수')
plt.ylabel('비례 값')
plt.grid()
plt.show()

# %%

# 공휴일 확인
# 구별로 공휴일에 약국을 운영하는 개수를 정리해 둔 csv를 불러온다
# 비례 값 계산 식 = 약국 운영 수 / ((인구수/10000) * 6)
seoul_drag_holiday_people = pd.read_csv(BASE_PATH+'seoul_pharm_holi_people.csv', thousands=',', encoding='utf-8')
seoul_drag_holiday_people.tail()

# %%

# 일요일 오픈 개수 비례 값으로 지도 확인
map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

map.choropleth(geo_data=geo_str,
               data=seoul_drag_holiday_people,
               columns=['구별', '비례 값'],
               fill_color='YlGnBu',  # PuRd, YlGnBu
               key_on='feature.id')
map

# %%

# index 다시 설정
seoul_drag_holiday_people = seoul_drag_holiday_people.set_index("구별")

# %%

seoul_drag_holiday_people.tail()

# %%

plt.figure(figsize=(10, 10))
plt.scatter(seoul_drag_holiday_people['인구수'], seoul_drag_holiday_people['비례 값'], s=50)
n = 0
for n in range(0, 25):
    plt.text(seoul_drag_holiday_people['인구수'][n] * 1.02, seoul_drag_holiday_people['비례 값'][n] * 0.98,
             seoul_drag_holiday_people.index[n], fontsize=11)
plt.xlabel('인구수')
plt.ylabel('비례 값')
plt.grid()
plt.show()
