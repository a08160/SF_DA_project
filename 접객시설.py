# 데이터 불러오기
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

df = pd.read_csv("서울시 상권분석서비스(집객시설-행정동).csv", encoding="EUC-KR", encoding_errors="replace", low_memory=False)

print(df.head())
print(df.info())

df.drop(["기준_년분기_코드","행정동_코드"], axis=1, inplace=True)

dong_df = pd.read_excel("dong_info.xlsx")
print(dong_df.head())

df["행정동_코드_명"] = df["행정동_코드_명"].astype(str)
dong_df["adm_nm"] = dong_df["adm_nm"].astype(str)

df["행정동_코드_명"] = df["행정동_코드_명"].apply(
    lambda x: next((adm for adm in dong_df["adm_nm"] if x in adm), 0)
)

# df와 dong_df에서 "행정동_코드_명"과 "adm_nm"을 비교하여, 없는 행정동을 찾기
missing_dongs = dong_df[~dong_df["adm_nm"].isin(df["행정동_코드_명"])]

# missing_dongs에 있는 행정동을 df에 추가하고, 나머지 column 값은 0으로 설정
for adm_nm in missing_dongs["adm_nm"]:
    # 새로운 행을 생성
    new_row = {col: 0 for col in df.columns}  # df의 모든 열에 대해 0으로 초기화
    new_row["행정동_코드_명"] = adm_nm  # 행정동_코드_명은 해당 행정동으로 설정
    
    # df에 새로운 행을 추가
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

df_grouped = df.groupby("행정동_코드_명").sum().T
df_grouped = df_grouped.loc[:, df_grouped.columns != 0]
df_grouped

df_grouped.to_excel("접객시설.xlsx")