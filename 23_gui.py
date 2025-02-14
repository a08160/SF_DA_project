import tkinter as tk
from tkinter import ttk
import pandas as pd

import json
import geopandas as gpd
import folium
import branca
import webbrowser
# import webview

# 엑셀 파일 로드
file_path = "최종정렬_preprocessing_data.xlsx"
df = pd.read_excel(file_path)

# 인스턴스 만들기
win = tk.Tk()
win.title("서울Fit")
win.geometry("640x480")
win.resizable(True, True)

# 스크롤 가능한 캔버스와 프레임 생성
canvas = tk.Canvas(win)
scroll_y = tk.Scrollbar(win, orient="vertical", command=canvas.yview)
frame = ttk.Frame(canvas)

# 프레임을 캔버스에 배치하고 스크롤 가능하도록 설정
frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=frame, anchor="nw")
canvas.configure(yscrollcommand=scroll_y.set)

# 탭 만들기
tabControl = ttk.Notebook(frame)
tab1 = ttk.Frame(tabControl)
tabControl.add(tab1, text='기능 1 - 나에게 Fit한 자취방 지역 추천')
tabControl.pack(expand=1, fill="both")

# 라벨 프레임 목록
categories = [
    ("교육", ["유치원 수", "초등학교 수", "중학교 수", "고등학교 수", "대학교 수"]),
    ("교통", ["지하철역 수", "버스 정거장 수"]),
    ("복지", ["관공서 수", "은행 수", "약국 수", "도서관 수", "병원 수", "문화예술회관+문화원 수", "전시관,미술관 수"]),
    ("생활 편의시설", ["백화점 수", "극장 수", "숙박시설 수", "일반 조리판매점 수", "커피숍 수", "패스트푸드점 수", "공연장 수", "슈퍼+편의점 수"]),
    ("안전", ["가로등 수", "범죄발생건수", "치안센터 수"]),
    ("주거 환경", ["아파트 수", "주거 부담 비율", "연립+다세대주택 수", "독립주택 수"]),
    ("지역 인구", ["총 인구수", "청년층 인구", "고령층 인구"])
]

radio_vars = {}  # 가중치 선택값 저장용 딕셔너리

for category, labels in categories:
    frame_category = ttk.LabelFrame(tab1, text=f'{category} - 세부 지표의 중요도를 정하세요', labelanchor='n')
    frame_category.pack(side='top', pady=10, fill='x', padx=5)
    
    for row, label_text in enumerate(labels):
        ttk.Label(frame_category, text=label_text).grid(row=row, column=0, padx=5, pady=2)
        radio_var = tk.IntVar(value=0)  # 기본값: 상관없음(0)
        radio_vars[label_text] = radio_var  # 변수 저장
        
        tk.Radiobutton(frame_category, text="많음", value=1, variable=radio_var).grid(row=row, column=1)
        tk.Radiobutton(frame_category, text="상관없음", value=0, variable=radio_var).grid(row=row, column=2)
        tk.Radiobutton(frame_category, text="적음", value=-1, variable=radio_var).grid(row=row, column=3)

# 캔버스와 스크롤바 배치
canvas.pack(side="left", fill="both", expand=True)
scroll_y.pack(side="right", fill="y")

# tab 1에 라벨 프레임 (srch) 만들기 
srch = ttk.LabelFrame(tab1, text='버튼을 클릭하세요', labelanchor='n')
srch.pack(side='top', pady=10)

# 지역 검색 및 점수 계산 함수
def generate_map():
    global df  # 기존 DataFrame 활용

    # 사용자 선택 가중치 가져오기
    weights = {category: {} for category, _ in categories}

    for category, indicators in categories:
        for indicator in indicators:
            weights[category][indicator] = radio_vars[indicator].get()

    # 새로운 점수 컬럼 추가
    for category, _ in categories:
        df[f"{category}-점수"] = 0.0
    df["최종_Score"] = 0.0

    for index, row in df.iterrows():
        category_scores = {}

        for category, indicators in categories:
            pos_weights = []
            pos_values = []
            neg_weights = []
            neg_values = []

            for indicator in indicators:
                col_name = f"{category}-{indicator}"
                weight = weights[category][indicator]
                value = row[col_name]

                if weight == 1:
                    pos_weights.append(1)
                    pos_values.append(value)
                elif weight == -1:
                    neg_weights.append(1)
                    neg_values.append(value)

            # 대분류 점수 계산
            if sum(pos_weights) > 0:
                pos_score = sum([w * v for w, v in zip(pos_weights, pos_values)]) / sum(pos_weights)
            else:
                pos_score = 0

            if sum(neg_weights) > 0:
                neg_score = sum([w * v for w, v in zip(neg_weights, neg_values)]) / sum(neg_weights)
            else:
                neg_score = 0

            category_score = pos_score - neg_score
            category_scores[category] = category_score

        # 대분류 점수를 데이터프레임에 추가
        for category, score in category_scores.items():
            df.loc[index, f"{category}-점수"] = score

        # 최종 Score 계산
        final_score = sum(category_scores.values())
        df.loc[index, "최종_Score"] = final_score

    df["행정동명"] = df["자치구"] + " " + df["행정동"]
    top_10 = df.nlargest(10, "최종_Score")[["행정동명", "최종_Score"] + [f"{category[0]}-점수" for category in categories]]
    top_10["순위"] = range(1, 11)
    top_10["최고 대분류"] = top_10[[f"{category[0]}-점수" for category in categories]].idxmax(axis=1).str.replace("-점수", "")
    # # 엑셀 파일로 저장
    # output_path = "분석결과.xlsx"
    # with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
    #     df.to_excel(writer, index=False)

    # print(f"엑셀 파일이 저장되었습니다: {output_path}")
    geojson_path = "hangjeongdong_서울특별시.geojson"


    # GeoJSON 데이터 불러오기
    with open(geojson_path, "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # GeoJSON에 행정동명 추가
    for feature in geojson_data["features"]:
        properties = feature["properties"]
        properties["행정동명"] = properties["sggnm"] + " " + properties["adm_nm"].split()[-1]

    # GeoJSON 매핑
    top_10_dict = top_10.set_index("행정동명")[["최종_Score", "최고 대분류", "순위"]].to_dict(orient="index")
    for feature in geojson_data["features"]:
        properties = feature["properties"]
        행정동명 = properties["행정동명"]
        if 행정동명 in top_10_dict:
            properties.update(top_10_dict[행정동명])
        else:
            properties.update({"최종_Score": None, "최고 대분류": None, "순위": None})

    # 색상 범위 설정
    scores = [v["최종_Score"] for v in top_10_dict.values()]
    min_score, max_score = min(scores), max(scores)
    colormap = branca.colormap.linear.YlGnBu_09.scale(min_score, max_score)
    colormap.caption = "최종 Score 상위 10개 행정동 색상"

    # Folium 지도 생성
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)

    # GeoJSON을 Folium 지도에 추가
    folium.GeoJson(
        geojson_data,
        name="서울 행정동",
        style_function=lambda feature: {
            "fillColor": colormap(feature["properties"].get("최종_Score", min_score)) if feature["properties"].get("최종_Score") is not None else "#ffffff",
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.7,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["순위", "행정동명", "최고 대분류"],
            aliases=["추천 순위", "행정동", "특징 지표"],
            localize=True,
            sticky=True,
            labels=True,
            style="background-color: white; color: black; font-size: 12px; font-weight: bold;",
            texttemplate="추천 {순위}순위: {행정동명} (특징: {최고 대분류})"
        ),
    ).add_to(m)

    # 컬러바 추가
    colormap.add_to(m)

    # HTML 파일 저장
    map_file_path = "seoul_top10_map.html"
    m.save(map_file_path)
    print(f"\n✅ 지도 생성 완료: {map_file_path}")
    
    # # ✅ WebView 실행 (새 창에서 지도 표시)
    # webview.create_window("서울Fit - 추천 지역", "http://127.0.0.1:5500/seoul_top10_map.html")
    # webview.start()
    # ✅ 기본 웹 브라우저에서 지도 열기
    webbrowser.open(map_file_path)
    
# 버튼 추가
srchbutton = ttk.Button(srch, text="조건에 맞는 지역 찾기", width=20, command=generate_map) 
srchbutton.grid(row=0, column=0)

# 실행
win.mainloop()

