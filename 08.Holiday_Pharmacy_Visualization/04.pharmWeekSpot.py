import numpy as np
import folium
import pandas as pd
import matplotlib.pyplot as plt
import json

# windows 한글 폰트 문제 해결
plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)

BASE_PATH = './data/'

### Step 06 - 휴일 약국 취약 지역 확인
# - 기준 측정: 국제 제약 연맹(FIP)와 WHO의 통계에 따르면(2017년 기준) 건강을 위한 필요한 약사의 수는
# 인구 수 1 만명당 약 5 명이 있어야 합니다.
# (참고 자료: https://www.fip.org/files/fip/publications/2017-09-Pharmacy_at_a_Glance-2015-2017.pdf)
# 하지만 이것은 2017년 기준이고 2019년이 지난 지금 최신 자료가 없으므로 예상을 해야 합니다.
# 즉 인구 수가 2017 년에 비해 늘었으므로 이에 대비한 인구 1 만명당 약사 수는 6 명으로 책정을 하였고
# 약사 1 명당 약국의 개수를 1개로 잡는다면 인구 1 만명당 약국의 수는 6 개라는 기준을 책정하였습니다.
# 분석 결과 값과 실제와는 다소 차이가 있으므로 참고용으로 확인하면 됩니다.

# %%

# 토요일 확인
# 구별로 공휴일에 약국을 운영하는 개수를 정리해 둔 csv를 불러온다
# 비례 값 계산 식 = 약국 운영 수 / ((인구수/10000) * 6)
seoul_pharm_sat_ratio = pd.read_csv(BASE_PATH + 'seoul_pharm_sat_ratio.csv', thousands=',', encoding='utf-8')
print(seoul_pharm_sat_ratio.head())

# %%

# geo json 파일 불러오기
geo_path = BASE_PATH+'geo_seoul.json'
geo_str = json.load(open(geo_path, encoding='utf-8'))

# 토요일 오픈 개수 비례 값으로 지도 확인
map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

map.choropleth(geo_data=geo_str,
               data=seoul_pharm_sat_ratio,
               columns=['구별', '비례값'],
               fill_color='YlGnBu',  # PuRd, YlGnBu
               key_on='feature.id')

map.save('./map/seoul_pharm_sat_ratio.html')

# %%

# index 다시 설정
seoul_pharm_sat_ratio = seoul_pharm_sat_ratio.set_index("구별")

# %%

plt.figure(figsize=(10, 10))
plt.axis((0, 700000, 0, 1.8))
plt.scatter(seoul_pharm_sat_ratio['인구수'], seoul_pharm_sat_ratio['비례값'], s=50)
plt.axhline(y=1.0, color='g', linewidth=3)

for n in range(0, 25):
    plt.text(seoul_pharm_sat_ratio['인구수'][n] * 1.02, seoul_pharm_sat_ratio['비례값'][n] * 0.98,
             seoul_pharm_sat_ratio.index[n], fontsize=12)

plt.title('토요일 약국 취약지역')
plt.xlabel('인구수')
plt.ylabel('비례값')
plt.grid()
plt.savefig('./plot/seoul_pharm_sat_ratio.png')
plt.show()

# %%

# 일요일 확인
# 구별로 공휴일에 약국을 운영하는 개수를 정리해 둔 csv를 불러온다
# 비례 값 계산 식 = 약국 운영 수 / ((인구수/10000) * 6)
seoul_pharm_sun_ratio = pd.read_csv(BASE_PATH + 'seoul_pharm_sun_ratio.csv', thousands=',', encoding='utf-8')
print(seoul_pharm_sun_ratio.head())

# %%

# 일요일 오픈 개수 비례 값으로 지도 확인
map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

map.choropleth(geo_data=geo_str,
               data=seoul_pharm_sun_ratio,
               columns=['구별', '비례값'],
               fill_color='YlGnBu',  # PuRd, YlGnBu
               key_on='feature.id')

map.save('./map/seoul_pharm_sun_ratio.html')

# %%

# index 다시 설정
seoul_pharm_sun_ratio = seoul_pharm_sun_ratio.set_index("구별")

# %%

plt.figure(figsize=(10, 10))
plt.axis((0, 700000, 0, 1.8))
plt.scatter(seoul_pharm_sun_ratio['인구수'], seoul_pharm_sun_ratio['비례값'], s=50)
plt.axhline(y=1.0, color='g', linewidth=3)

for n in range(0, 25):
    plt.text(seoul_pharm_sun_ratio['인구수'][n] * 1.02, seoul_pharm_sun_ratio['비례값'][n] * 0.98,
             seoul_pharm_sun_ratio.index[n], fontsize=11)

plt.title('일요일 약국 취약지역')
plt.xlabel('인구수')
plt.ylabel('비례값')
plt.grid()
plt.savefig('./plot/seoul_pharm_sun_ratio.png')
plt.show()

# %%

# 공휴일 확인
# 구별로 공휴일에 약국을 운영하는 개수를 정리해 둔 csv를 불러온다
# 비례 값 계산 식 = 약국 운영 수 / ((인구수/10000) * 6)
seoul_pharm_holi_ratio = pd.read_csv(BASE_PATH + 'seoul_pharm_holi_ratio.csv', thousands=',', encoding='utf-8')
print(seoul_pharm_holi_ratio.head())

# %%

# 공휴일 오픈 개수 비례 값으로 지도 확인
map = folium.Map(location=[37.5502, 126.982], zoom_start=11)

map.choropleth(geo_data=geo_str,
               data=seoul_pharm_holi_ratio,
               columns=['구별', '비례값'],
               fill_color='YlGnBu',  # PuRd, YlGnBu
               key_on='feature.id')

map.save('./map/seoul_pharm_holi_ratio.html')

# %%
# index 다시 설정
seoul_pharm_holi_ratio = seoul_pharm_holi_ratio.set_index("구별")

# %%

plt.figure(figsize=(10, 10))
plt.axis((0, 700000, 0, 1.8))
plt.scatter(seoul_pharm_holi_ratio['인구수'], seoul_pharm_holi_ratio['비례값'], s=50)
plt.axhline(y=1.0, color='g', linewidth=3)

for n in range(0, 25):
    plt.text(seoul_pharm_holi_ratio['인구수'][n] * 1.02, seoul_pharm_holi_ratio['비례값'][n] * 0.98,
             seoul_pharm_holi_ratio.index[n], fontsize=11)

plt.title('공휴일 약국 취약지역')
plt.xlabel('인구수')
plt.ylabel('비례값')
plt.grid()
plt.savefig('./plot/seoul_pharm_holi_ratio.png')
plt.show()