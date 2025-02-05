import pandas as pd
import os
import glob
import chardet
import re

'''자치구별 전월세'''

# 2021-2022년 전월세 파일은 txt 파일이기 때문에 csv로 변환해야 함..

# TXT 파일 경로 (변환할 파일 경로)
txt_file_path = r"C:\Users\TG\Documents\SF_DA_project\data\monthly_rent\서울특별시_전월세가_2021.txt"
csv_file_path = txt_file_path.replace(".txt", ".csv")  # 동일한 이름으로 CSV 변환

# 파일 인코딩 구분
def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        raw_data = f.read(10000)  # 파일 일부만 읽어서 인코딩 감지
    result = chardet.detect(raw_data)
    return result["encoding"]

encoding_type = detect_encoding(txt_file_path)
print(f"감지된 파일 인코딩: {encoding_type}")

with open(txt_file_path, "r", encoding=encoding_type) as file:
    first_line = file.readline()
    delimiter = "," if "," in first_line else "\t" if "\t" in first_line else " "  # 쉼표, 탭, 공백 중 선택

print(f"감지된 구분자: '{delimiter}'")

# df로 변환
df = pd.read_csv(txt_file_path, delimiter=delimiter, encoding=encoding_type)

# CSV 파일로 저장
df.to_csv(csv_file_path, index=False, encoding="utf-8-sig")

print(f" 변환 완료! CSV 파일 저장: {csv_file_path}")



# CSV 파일이 들어있는 폴더 경로
folder_path = r"C:\Users\TG\Documents\SF_DA_project\data\monthly_rent"

csv_files = glob.glob(os.path.join(folder_path, "*.csv"))

# 파일 인코딩 감지 함수 (이게 진짜 열받음, 2022는 EUC-KR, 2023은 UTF-8-SIG
def detect_encoding(file_path):
    with open(file_path, "rb") as f:
        raw_data = f.read(10000)  # 파일 일부만 읽어서 인코딩 감지
    result = chardet.detect(raw_data)
    return result["encoding"]

# CSV 파일을 하나씩 불러와 리스트에 저장 (자동 인코딩 감지)
data_list = []
for file in csv_files:
    encoding_type = detect_encoding(file)
    print(f"✅{file} 파일 인코딩 감지: {encoding_type}")
    
    try:
        df = pd.read_csv(file, encoding=encoding_type)
        data_list.append(df)
    except UnicodeDecodeError:
        print(f" {file}에서 {encoding_type} 인코딩 실패! UTF-8-SIG로 재시도")
        df = pd.read_csv(file, encoding="utf-8-sig", errors="replace")
        data_list.append(df)

# 🔹 모든 데이터를 하나의 데이터프레임으로 병합
df = pd.concat(data_list, ignore_index=True)


# 2. 전세를 월세로 변환하는 함수
def extract_contract_months(period):
    """ 계약 기간을 개월 수로 변환하는 함수 """
    if pd.isna(period):
        return 24  # 계약 기간이 없는 경우 기본 2년(24개월) 적용
    match = re.search(r'(\d{2})\.(\d{2})~(\d{2})\.(\d{2})', period)
    if match:
        start_year, start_month, end_year, end_month = map(int, match.groups())
        months = (end_year - start_year) * 12 + (end_month - start_month)
        return months
    return 24  # 기본값 2년

# 계약 개월 수 컬럼 추가
df["계약개월"] = df["계약기간"].apply(extract_contract_months)

# 법정 전환율 적용 (5.5%)
conversion_rate = 5.5 / 100  # 5.5% 연환산율
df["전환월세(만원)"] = (df["보증금(만원)"] * conversion_rate) / 12


# 3. 전세와 월세의 월세 비교 (자치구명 + 월세만 추출)
df_rent = df[["자치구명", "임대료(만원)"]].rename(columns={"임대료(만원)": "월세(만원)"})  # 기존 월세 데이터
df_jeonse = df[df["임대료(만원)"] == 0][["자치구명", "전환월세(만원)"]].rename(columns={"전환월세(만원)": "월세(만원)"})  # 전세 → 월세 변환된 데이터

# 두 데이터를 합쳐서 하나의 월세 데이터로 만들기
df_final = pd.concat([df_rent, df_jeonse], ignore_index=True)

# 4. 지역별 평균 월세 계산
df_avg_rent = df_final.groupby("자치구명")["월세(만원)"].mean().reset_index()

# Jupyter Notebook 실행 폴더에 저장
df_avg_rent.to_csv("지역별_평균_월세.csv", index=False, encoding="utf-8-sig")

# 데이터 확인 (처음 몇 개 행만 출력)
print("지역별 평균 월세 데이터:")
print(df_avg_rent.head())

