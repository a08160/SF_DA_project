from pyproj import Proj, Transformer
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

# 데이터 불러오기
df = pd.read_csv("서울시 휴게음식점 인허가 정보.csv", encoding="EUC-KR", encoding_errors="replace", low_memory=False)

# 중부원점TM (EPSG:2097) → WGS84 (EPSG:4326) 변환기 (방식 변경)
tm_proj = Proj("epsg:2097")
wgs84_proj = Proj("epsg:4326")
transformer = Transformer.from_proj(tm_proj, wgs84_proj, always_xy=True)

# 중부원점TM → WGS84 위도/경도 변환 (NaN 값 처리 + 좌표 변환 방식 개선)
df["경도"], df["위도"] = zip(*df.apply(
    lambda x: transformer.transform(x["좌표정보(X)"], x["좌표정보(Y)"])
    if pd.notna(x["좌표정보(X)"]) and pd.notna(x["좌표정보(Y)"]) else (None, None), axis=1
))

# 영업 중인 지점만 추출
df = df[df["상세영업상태명"] == "영업"]
new_df = df[["경도", "위도", "업태구분명"]].dropna().reset_index(drop=True)

# GeoJSON 파일 읽기 (성능 최적화: 한 번만 로드)
geojson_file = "hangjeongdong_서울특별시.geojson"
gdf = gpd.read_file(geojson_file)

# 행정동 정보 추출 함수 (속도 개선)
def find_administrative_dong(latitude, longitude, gdf):
    point = Point(longitude, latitude)
    result = gdf[gdf.contains(point)]
    return result.iloc[0]["adm_nm"] if not result.empty else "해당 좌표는 어떤 행정동에도 속하지 않습니다."

# 행정동을 찾는 함수를 적용
new_df["행정동"] = new_df.apply(lambda x: find_administrative_dong(x["위도"], x["경도"], gdf), axis=1)

# 결과 출력
full_data = new_df[new_df["행정동"] != "해당 좌표는 어떤 행정동에도 속하지 않습니다."]

# 행정동 / 업태구분명 별 데이터 정리
final_data = pd.pivot_table(full_data, index="업태구분명", columns="행정동", aggfunc="size", fill_value=0).T

final_data.to_excel("cafe_data.xlsx")