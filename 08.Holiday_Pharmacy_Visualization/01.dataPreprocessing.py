import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import googlemaps
import json
from tqdm import tqdm

# %%
BASE_PATH = './data/'

# 데이터 셋 불러오기
pharm_data = pd.read_csv(BASE_PATH + '/raw/seoul_pharm_raw.csv', thousands=',', encoding='utf-8', index_col=0)

# 필요 없는 데이터 컬럼 삭제
del pharm_data['폐업일자']
del pharm_data['휴업시작일자']
del pharm_data['휴업종료일자']
del pharm_data['소재지면적']
del pharm_data['소재지우편번호']
del pharm_data['재개업일자']
del pharm_data['위치정보(X)']
del pharm_data['위치정보(Y)']

# %%

# 인허가구분명의 한약국 네이밍 삭제
pharm_data_clear = pharm_data[pharm_data.인허가구분명 != '한약국']

# 구별 데이터 컬럼 추가
pharm_data_clear['구별'] = pharm_data_clear['도로명전체주소'].str.split(' ').str[1]

# 도로명 전체 주소 내용 수정
pharm_data_clear['도로명전체주소'] = (pharm_data_clear['도로명전체주소'].str.split(' ').str[0] +
                         pharm_data_clear['도로명전체주소'].str.split(' ').str[1] +
                         pharm_data_clear['도로명전체주소'].str.split(' ').str[2] +
                         pharm_data_clear['도로명전체주소'].str.split(' ').str[3])

pharm_data_clear = pharm_data_clear.dropna(subset=['도로명전체주소'])
pharm_data_clear = pharm_data_clear.reset_index(drop=True)

# %% md
### Step 02 - 구글 맵스 geocode를 이용한 위도 경도 다시 구하기
# Secret Key 로드
with open('./secrets.json') as f:
    key_file = json.loads(f.read())

# GMAP 키 로드
gmaps_key = key_file["GMAP_KEY"]
gmaps = googlemaps.Client(key=gmaps_key)

# %%
# 도로명 전체 주소를 drag_location_name 배열에 추가
pharm_address = []

for name in pharm_data_clear['도로명전체주소']:
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
# 백업을 위해 위도 경도를 따로 데이터프레임에 저장하고 csv로 저장하였습니다.
pharm_coord = pd.DataFrame({'위도': pharm_coord_lat, '경도': pharm_coord_lng})
pharm_coord.to_csv(BASE_PATH + "seoul_pharm_coord.csv", encoding='utf-8-sig', sep=',')

# %%
# 위치정보를 위도 경도로 바꿉니다.
pharm_data_clear.insert(0, '경도', pharm_coord['경도'])
pharm_data_clear.insert(0, '위도', pharm_coord['위도'])

# 전처리된 데이터 저장 및 로드
pharm_data_clear.to_csv(BASE_PATH + "seoul_pharm_clean.csv", encoding='utf-8-sig', sep=',')
pharm_data_clear = pd.read_csv(BASE_PATH + 'seoul_pharm_clean.csv', thousands=',', encoding='utf-8')

# %% md

### Step 03 - 서울시 약국 현황 지도 시각화 처리
# windows 한글 폰트 문제 해결
plt.rc('font', family='Malgun Gothic')
plt.rc('axes', unicode_minus=False)
plt.figure(figsize=(16, 8))
sns.countplot(data=pharm_data_clear, x="구별")
plt.title("서울시 전체 약국 개수")
plt.show()

# %%
# seaborn으로 그리기
# 원래는 folium map으로 처리하려고 했으나 map의 개수가 3300개 이상이 되면 folium이
# 정상적으로 처리가 되지 않아서 seaborn으로 형태만 잡았습니다.
plt.figure(figsize=(10, 8))
sns.scatterplot(data=pharm_data_clear[["경도", "위도"]], x='경도', y='위도')
plt.show()
