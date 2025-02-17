
import pandas as pd

file_name = "자치구별_가로등.csv"
df = pd.read_csv(file_name, encoding="utf-8", header=None)  # 헤더 없이 로드

# 세 번째 행을 컬럼명으로 설정하고 첫 번째, 두 번째 행 삭제
df.columns = df.iloc[2]  # 세 번째 행을 컬럼으로 지정
df = df.iloc[3:].reset_index(drop=True)  # 0, 1, 2 번째 행 삭제
# 컬럼명을 리스트로 변환하여 정리
df.columns = df.columns.tolist()

df = df.drop(index=range(1, 9)).reset_index(drop=True)
# 숫자형 데이터만 선택하여 합계 계산
total_sum = df.iloc[1:, 2].astype(int).sum()  # 첫 번째 행(소계 행)을 제외한 나머지 행들의 합

# 첫 번째 행(소계 행)의 숫자 값 업데이트
df.iloc[0, 2] = total_sum

# 컬럼명 변경
df = df.rename(columns={'자치구별(2)': '자치구별', '개소 (개소)': '개소'})

# 첫 번째 컬럼 삭제
df = df.iloc[:, 1:]

# 소계 행(index 0) 삭제
df = df.drop(index=0).reset_index(drop=True)

# 결과 확인
print(df.tail())

# 저장할 파일 이름 설정
output_file = "전처리된_자치구별_가로등.csv"

# CSV 파일로 저장
with open(output_file, mode="w", encoding="utf-8", newline="") as file:
    df.to_csv(file, index=False)
# print(df.info())