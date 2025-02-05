
# 데이터 불러오기
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

df = pd.read_csv("서울시 상권분석서비스(집객시설-행정동).csv", encoding="EUC-KR", encoding_errors="replace", low_memory=False)

df.drop(["기준_년분기_코드","행정동_코드"], axis=1, inplace=True)

dong_df = pd.read_excel("dong_info.xlsx")

df["행정동_코드_명"] = df["행정동_코드_명"].astype(str)
dong_df["adm_nm"] = dong_df["adm_nm"].astype(str)

df["행정동_코드_명"] = df["행정동_코드_명"].apply(
    lambda x: next((adm for adm in dong_df["adm_nm"] if x in adm), 0)
)

df_group = df.groupby("행정동_코드_명").sum()

df_group.to_excel("접객시설.xlsx")