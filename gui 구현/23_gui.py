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
frame_container = ttk.Frame(canvas)

# 프레임을 캔버스에 배치하고 스크롤 가능하도록 설정
frame_container.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=frame_container, anchor="nw")
canvas.configure(yscrollcommand=scroll_y.set)

# 기능 선택을 위한 프레임 생성
menu_frame = ttk.Frame(win)
menu_frame.pack(side="top", fill="x")

main_frame = ttk.Frame(frame_container)
main_frame.pack(fill="both", expand=True)

# 기능 1,2 프레임 생성
frame_1 = ttk.Frame(main_frame)
frame_2 = ttk.Frame(main_frame)

# 기능 1,2 버튼 (자취방 추천)
def show_frame_1():
    frame_2.pack_forget()
    frame_1.pack(fill="both", expand=True)
    canvas.yview_moveto(0)  # ✅ 스크롤을 최상단으로 이동


def show_frame_2():
    frame_1.pack_forget()
    frame_2.pack(fill="both", expand=True)
    canvas.yview_moveto(0)  # ✅ 스크롤을 최상단으로 이동


btn_1 = ttk.Button(menu_frame, text="기능 1 - 사용자 맞춤형 지역 추천", command=show_frame_1)
btn_1.pack(side="left", padx=10, pady=5)
btn_2 = ttk.Button(menu_frame, text="기능 2 - 클러스터링 지역 추천", command=show_frame_2)
btn_2.pack(side="left", padx=10, pady=5)

# 기능 1 내용 (기존 tab1 내용 이동)
# frame_1.pack(fill="both", expand=True)

# 기능 2 (클러스터링) 프레임 내부 요소
cluster = ttk.LabelFrame(frame_2, text="원하는 추천 분류를 선택하세요")
cluster.pack(side='top', pady=10)

def clusturing_0():
    map_cluster_0 = "cluster_map_0 (1).html"
    webbrowser.open(map_cluster_0)

def clusturing_1():
    map_cluster_1 = "cluster_map_1 (1).html"
    webbrowser.open(map_cluster_1)

def clusturing_2():
    map_cluster_2 = "cluster_map_2 (1).html"
    webbrowser.open(map_cluster_2)
    
# 버튼 추가
cluster_0_button = ttk.Button(cluster, text="Cluster0\n안전 복지 교육", width=20, command=clusturing_0) 
cluster_0_button.grid(row=0, column=0)
cluster_1_button = ttk.Button(cluster, text="Cluster1\n교육 문화 인구", width=20, command=clusturing_1) 
cluster_1_button.grid(row=0, column=1)
cluster_2_button = ttk.Button(cluster, text="Cluster2\n교통 주거환경 편의시설", width=20, command=clusturing_2) 
cluster_2_button.grid(row=0, column=2)


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
    frame_category = ttk.LabelFrame(frame_1, text=f'{category} - 세부 지표의 중요도를 정하세요', labelanchor='n')
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
srch = ttk.LabelFrame(frame_1, text='버튼을 클릭하세요', labelanchor='n')
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
    m = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles="CartoDB Positron")

    # ✅ 상위 10개 행정동과 나머지 행정동을 분리하여 툴팁 다르게 적용
    for feature in geojson_data["features"]:
        properties = feature["properties"]
        행정동명 = properties["행정동명"]

        if 행정동명 in top_10_dict:
            # ✅ 상위 10개 행정동 (순위, 최고 대분류 표시)
            tooltip_content = folium.GeoJsonTooltip(
                fields=["순위", "행정동명", "최고 대분류"],
                aliases=["추천 순위", "행정동", "특징 지표"],
                localize=True,
                sticky=True,
                labels=True,
                style="background-color: white; color: black; font-size: 12px; font-weight: bold;",
                texttemplate="추천 {순위}순위: {행정동명} (특징: {최고 대분류})"
            )
            fill_color = colormap(properties.get("최종_Score", min_score))

        else:
            # ✅ 나머지 행정동 (행정동명만 표시)
            tooltip_content = folium.GeoJsonTooltip(
                fields=["행정동명"],
                aliases=["행정동"],
                localize=True,
                sticky=True,
                labels=True,
                style="background-color: white; color: black; font-size: 12px; font-weight: bold;"
            )
            fill_color = "#ffffff"  # 흰색 계열로 기본 색상 적용

        folium.GeoJson(
            feature,
            name="서울 행정동",
            style_function=lambda feature, fill_color=fill_color: {
                "fillColor": fill_color,
                "color": "black",
                "weight": 0.5,
                "fillOpacity": 0.7 if feature["properties"].get("순위") is not None else 0.7,  # 상위 10개는 불투명도 높게 설정
            },
            tooltip=tooltip_content,
        ).add_to(m)

    # 컬러바 추가
    colormap.add_to(m)

    # HTML 파일 저장
    map_file_path = "seoul_top10_map.html"
    m.save(map_file_path)
    print(f"\n✅ 지도 생성 완료: {map_file_path}")
    
    
    # ✅ 기본 웹 브라우저에서 지도 열기
    webbrowser.open(map_file_path)
    
# 버튼 추가
srchbutton = ttk.Button(srch, text="조건에 맞는 지역 찾기", width=20, command=generate_map) 
srchbutton.grid(row=0, column=0)


# Change the main windows icon 아이콘 변경
icon = tk.PhotoImage(file='seoulfit_icon2.png')

win.iconphoto(False, icon)
# 실행
win.mainloop()


    # # 엑셀 파일로 저장
    # output_path = "분석결과.xlsx"
    # with pd.ExcelWriter(output_path, engine="xlsxwriter") as writer:
    #     df.to_excel(writer, index=False)

    # print(f"엑셀 파일이 저장되었습니다: {output_path}")
    
    
    # # ✅ WebView 실행 (새 창에서 지도 표시)
    # webview.create_window("서울Fit - 추천 지역", "http://127.0.0.1:5500/seoul_top10_map.html")
    # webview.start()