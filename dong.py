# GeoJSON 파일 로드
import geopandas as gpd
import pandas as pd

geojson = gpd.read_file("hangjeongdong_서울특별시.geojson", encoding = "utf-8")


# 행정동 정보 추출출
dong_info = pd.DataFrame(geojson["adm_nm"])

dong_info.to_excel("dong_info.xlsx")