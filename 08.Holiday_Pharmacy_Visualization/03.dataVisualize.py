import folium
import pandas as pd
import json
import matplotlib.pyplot as plt
import seaborn as sns


# windows 한글 폰트 문제 해결
plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)

BASE_PATH = './data/'
seoul_pharm_sat = pd.read_csv(BASE_PATH + 'seoul_pharm_sat.csv', thousands=',', encoding='utf-8')
seoul_pharm_sun = pd.read_csv(BASE_PATH + 'seoul_pharm_sun.csv', thousands=',', encoding='utf-8')
seoul_pharm_holi = pd.read_csv(BASE_PATH + 'seoul_pharm_holi.csv', thousands=',', encoding='utf-8')


### Step 05 - 휴일 오픈 약국 시각화 처리

# 토요일 확인
print("토요일 영업 약국수: {}".format(len(seoul_pharm_sat['구별'])))
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
plt.show()

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
# 토요일 구별 운영 약국수
pharm_num = seoul_pharm_sat.groupby(seoul_pharm_sat['구별']).size()

# 토요일 오픈 개수 map 확인
seoul_pharm_sat_coord = pd.read_csv(BASE_PATH + 'seoul_pharm_sat.csv', thousands=',', encoding='utf-8')
map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

map.choropleth(geo_data=geo_str,
               data=pharm_num,
               columns=['구별', '개수'],
               fill_color='YlGnBu',  # PuRd, YlGnBu
               key_on='feature.id')

map.save('./map/seoul_pharm_sat_district.html')

# %%
# 일요일 확인
print("일요일 영업 약국수: {}".format(len(seoul_pharm_sun['구별'])))
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
# 일요일 구별 운영 약국수
pharm_num = seoul_pharm_sun.groupby(seoul_pharm_sun['구별']).size()

# 일요일 오픈 개수 map 확인
seoul_pharm_sun_coord = pd.read_csv(BASE_PATH + 'seoul_pharm_sun.csv', thousands=',', encoding='utf-8')
map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

map.choropleth(geo_data=geo_str,
               data=pharm_num,
               columns=['구별', '개수'],
               fill_color='YlGnBu',  # PuRd, YlGnBu
               key_on='feature.id')

map.save('./map/seoul_pharm_sun_district.html')

# %%
# 공휴일 확인
print("공휴일 영업 약국수: {}".format(len(seoul_pharm_holi['구별'])))
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
# 공휴일 구별 운영 약국수
pharm_num = seoul_pharm_holi.groupby(seoul_pharm_holi['구별']).size()

# 공휴일 오픈 개수 map 확인
seoul_pharm_holi_coord = pd.read_csv(BASE_PATH + 'seoul_pharm_holi.csv', thousands=',', encoding='utf-8')
map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

map.choropleth(geo_data=geo_str,
               data=pharm_num,
               columns=['구별', '개수'],
               fill_color='YlGnBu',  # PuRd, YlGnBu
               key_on='feature.id')

map.save('./map/seoul_pharm_holi_district.html')
