from pyproj import CRS, Transformer
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

df = pd.read_csv("서울시 휴게음식점 인허가 정보.csv", encoding="EUC-KR", encoding_errors="replace", low_memory=False)

# 중부원점TM (EPSG:2097) -> WGS84 (EPSG:4326) 변환기
crs_tm = CRS.from_epsg(2097)
crs_wgs84 = CRS.from_epsg(4326)
transformer = Transformer.from_crs(crs_tm, crs_wgs84)

# 중부원점TM -> WGS84 위도/경도로 변환
df["위도"], df["경도"] = zip(*df.apply(lambda x: transformer.transform(x["좌표정보(X)"], x["좌표정보(Y)"]), axis=1))

# 영업 중인 지점만 추출
df = df[df["상세영업상태명"] == "영업"]
new_df = df[["경도","위도","업태구분명"]].reset_index(drop = True)

# 행정동 정보 추출
def find_administrative_dong(geojson_file, latitude, longitude):
    # GeoJSON 파일을 읽어들입니다.
    gdf = gpd.read_file(geojson_file)
    
    # 주어진 위도, 경도 좌표를 이용해 포인트 객체를 만듭니다.
    point = Point(longitude, latitude)
    
    # 포인트가 속한 행정동을 찾습니다.
    for index, row in gdf.iterrows():
        if row['geometry'].contains(point):
            return row['adm_nm']
    
    return "해당 좌표는 어떤 행정동에도 속하지 않습니다."

# GeoJSON 파일 경로와 테스트할 좌표를 지정합니다.
geojson_file = "hangjeongdong_서울특별시.geojson"

# 행정동을 찾는 함수를 호출합니다.
new_df["행정동"] = new_df.apply(lambda x: find_administrative_dong(geojson_file, x["위도"], x["경도"]), axis=1)
print(new_df)