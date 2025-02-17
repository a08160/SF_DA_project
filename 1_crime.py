import pandas as pd

file_name = "5대_범죄_발생현황.csv"
df = pd.read_csv(file_name, encoding="utf-8")

# 첫 번째 열 제거
df = df.iloc[:, 1:]

# 필요한 컬럼만 선택
df = df[['자치구별(2)', '2020', '2021', '2022', '2023']]
df = df.drop(index=[0, 1, 2]).reset_index(drop=True)

df = df.rename(columns={'자치구별(2)': '자치구별'})

# '2020', '2021', '2022', '2023' 열을 숫자로 변환
df[['2020', '2021', '2022', '2023']] = df[['2020', '2021', '2022', '2023']].apply(pd.to_numeric, errors='coerce')

# 각 행에서 '2020', '2021', '2022', '2023' 열의 평균값을 계산하여 새로운 컬럼 '평균 발생 건수' 생성
df['평균 발생 건수'] = df[['2020', '2021', '2022', '2023']].mean(axis=1)

# '자치구별'과 '평균 발생 건수' 컬럼만 남기기
df = df[['자치구별', '평균 발생 건수']]

# 저장할 파일 이름 설정
output_file = "전처리된_5대_범죄_발생현황.csv"

# CSV 파일로 저장
with open(output_file, mode="w", encoding="utf-8", newline="") as file:
    df.to_csv(file, index=False)

# 데이터 확인
# print(df.info())
# print(df.head())
# print(df.columns)