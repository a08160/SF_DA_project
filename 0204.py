# 한글 폰트 설정
font_path = 'C:/Windows/Fonts/malgun.ttf'  # 사용하는 한글 폰트 경로 설정
font_prop = fm.FontProperties(fname=font_path, size=14)

import os
import pandas as pd

### 자치구별 관리비 2020-2024 4개년치 데이터 통합

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