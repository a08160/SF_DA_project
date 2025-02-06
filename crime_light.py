import pandas as pd

light_df = pd.read_csv("자치구별_가로등.csv", encoding = "utf-8")
crime_df = pd.read_csv("자치구별_5대_범죄_평균발생수.csv", encoding = "utf-8")
size_df_dong = pd.read_excel("행정구역(동별)_20250206150408.xlsx")
size_df_gu = pd.read_excel("행정구역(구별).xlsx")
dong_df = pd.read_excel("dong_info.xlsx")

def dong_merge(df):
    global dong_df
    
    df["행정동"] = df["행정동"].apply(
        lambda x: next((adm for adm in dong_df["adm_nm"] if x in adm), 0)
    )

size_df_dong = size_df_dong[size_df_dong["행정동"] != "소계"].drop(["구성비"],axis=1).reset_index(drop=True)

size_df_dong = size_df_dong.rename(columns={"Unnamed: 2": "구성비"})

dong_merge(size_df_dong)

size_df_dong.loc[size_df_dong["행정동"]==0,"행정동"]="서울특별시 강남구 개포3동"

print(size_df_dong.info())

crime_df = crime_df.rename(columns={"자치구별":"구"})

size_df_gu.loc[size_df_gu["구"] == "서북구", "구"] = "성북구"

# 면적과 범죄 건수의 상관관계 확인

merged_df = size_df_gu.merge(crime_df, on='구', how='outer')

import numpy as np
import matplotlib.pyplot as plt
%matplotlib inline

# 꺾은 선 그래프 그리기
plt.scatter(merged_df["구성비"], merged_df["범죄 평균 발생 건수(20~23년)"], alpha=0.7, color='b')

# 선형 회귀 계산
x = merged_df["구성비"]
y = merged_df["범죄 평균 발생 건수(20~23년)"]

# 회귀선 계산 (y = mx + b 형태)
m, b = np.polyfit(x, y, 1)
plt.plot(x, m*x + b, color='r', label=f'Linear regression line: y = {m:.2f}x + {b:.2f}')

# 제목과 축 레이블 추가
plt.title('Correlation between size and crime')
plt.xlabel('size')
plt.ylabel('the number of crime')

# 범례 추가
plt.legend()

# 그래프 표시
plt.show()

light_df = light_df.rename(columns={"자치구":"구"}) 

gu_df = merged_df.merge(light_df, on='구', how='outer')

size_df_dong["가로등수"] = size_df_dong.apply(
    lambda x: next(
        (
            (gu_df[gu_df["구"] == gu]["가로등개수"].values[0] * x["구성비"]).round()
            for gu in gu_df["구"] if str(gu) in str(x["행정동"])  # 행정동을 문자열로 변환하여 비교
        ), 0), axis=1)

size_df_dong["평균범죄발생건수(20~23년)"] = size_df_dong.apply(
    lambda x: next(
        (
            (gu_df[gu_df["구"] == gu]["범죄 평균 발생 건수(20~23년)"].values[0] * x["구성비"])
            for gu in gu_df["구"] if str(gu) in str(x["행정동"])  # 행정동을 문자열로 변환하여 비교
        ), 0), axis=1) 

size_df_dong = size_df_dong[size_df_dong["행정동"] != "서울특별시 강남구 개포3동"]

size_df_dong.to_excel("light_crime_data.xlsx", index = False)