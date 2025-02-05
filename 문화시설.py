# 데이터 불러오기
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

df = pd.read_csv("서울시 문화공간 정보.csv", encoding="EUC-KR", encoding_errors="replace", low_memory=False)
print(df.head())
print(df.info())

new_df = df[["주제분류","문화시설명","위도","경도"]]

geojson_file = "hangjeongdong_서울특별시.geojson"
gdf = gpd.read_file(geojson_file)

def find_administrative_dong(latitude, longitude, gdf):
    point = Point(longitude, latitude)
    result = gdf[gdf.contains(point)]
    return result.iloc[0]["adm_nm"] if not result.empty else "해당 좌표는 어떤 행정동에도 속하지 않습니다."

new_df["행정동"] = new_df.apply(lambda x: find_administrative_dong(x["위도"], x["경도"], gdf), axis=1)

final_data = pd.pivot_table(new_df, index="주제분류", columns="행정동", aggfunc="size", fill_value=0).T

final_data.to_excel("문화시설.xlsx")