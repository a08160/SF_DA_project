# 한글 폰트 설정
font_path = 'C:/Windows/Fonts/malgun.ttf'  # 사용하는 한글 폰트 경로 설정
font_prop = fm.FontProperties(fname=font_path, size=14)

import os
import pandas as pd

'''자치구별 관리비 2020-2024 4개년치 데이터 통합'''

folder_path = "C:\\Users\\TG\\Desktop\\maintenance_cost"

# 데이터를 저장할 리스트
data_list = []

# 2020년부터 2024년까지 각 연도의 1~12월 파일 병합
for year in range(2020, 2025):
    for month in range(1, 13):
        file_name = f"자치구별 관리비 통계({year}.{month:02d}).xlsx"
        file_path = os.path.join(folder_path, file_name)
        
        # 파일이 존재하는지 확인 후 처리
        if os.path.exists(file_path):
            xls = pd.ExcelFile(file_path)
            df = pd.read_excel(xls, sheet_name=xls.sheet_names[0])  # 첫 번째 시트 로드
            
            # '년도'와 '월' 컬럼 추가
            df['년도'] = year
            df['월'] = month
            
            # 데이터 리스트에 추가
            data_list.append(df)

# 데이터프레임 병합
final_df = pd.concat(data_list, ignore_index=True)

print(final_df)
df = final_df.sort_index(axis = 0)
df.to_csv("자치구별_통계.csv", index = False, encoding="utf-8-sig")



'''이상치 탐색 및 전처리'''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 한글 폰트 설정
plt.rc('font', family='Malgun Gothic')  # Windows 사용자
plt.rcParams['axes.unicode_minus'] = False  # 마이너스 부호 깨짐 방지

column_name = "공용관리비용"
df[column_name] = pd.to_numeric(df[column_name], errors='coerce')  # 숫자로 변환, 오류 시 NaN 처리

# 결측값 개수 확인
missing_values = df[column_name].isnull().sum()

# 이상치 탐색: IQR 방식 사용
Q1 = df[column_name].quantile(0.25)
Q3 = df[column_name].quantile(0.75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

# 이상치 여부 확인
outliers = df[(df[column_name] < lower_bound) | (df[column_name] > upper_bound)]

# 시각화: 결측값 및 이상치 그래프
plt.figure(figsize=(12, 5))

# Boxplot (이상치 확인)
plt.subplot(1, 2, 1)
sns.boxplot(x=df[column_name], color='orange')
plt.title("공용관리비용 이상치 확인 (Boxplot)")

# 이상치 및 결측값 정보 출력
print(f"공용관리비용 이상치 개수: {outliers.shape[0]}")


# 이상치 제거
df_cleaned = df[(df[column_name] >= lower_bound) & (df[column_name] <= upper_bound)]

# 이상치 제거 후 결측값 재확인
missing_values_after = df_cleaned[column_name].isnull().sum()

# 시각화: 이상치 제거 전/후 비교
plt.figure(figsize=(12, 5))

# Boxplot (이상치 제거 전)
plt.subplot(1, 2, 1)
sns.boxplot(x=df[column_name], color='orange')
plt.title("공용관리비용 이상치 제거 전 (Boxplot)")

# Boxplot (이상치 제거 후)
plt.subplot(1, 2, 2)
sns.boxplot(x=df_cleaned[column_name], color='blue')
plt.title("공용관리비용 이상치 제거 후 (Boxplot)")

plt.tight_layout()
plt.show()

# 이상치 및 결측값 정보 출력
print(f"공용관리비용 이상치 제거 전 갯수: {df.shape[0]}")
print(f"이상치 제거 후 데이터 개수: {df_cleaned.shape[0]}")

import pandas as pd

# 지역별 "공용관리비용" 평균 계산
average_management_fees = df_cleaned.groupby("지역")["공용관리비용"].mean().reset_index()

# 평균 계산 결과 출력
print(average_management_fees)

# 인덱스 없이 CSV 파일로 저장
average_management_fees = average_management_fees.sort_values(by="지역")  # 지역별로 정렬
average_management_fees.to_csv("자치구별_관리비_평균.csv", index=False, encoding="utf-8-sig")

