import json
import geopandas as gpd
import pandas as pd
import folium
import branca

# 파일 불러오기
file_path = "최종정렬_preprocessing_data.xlsx"
geojson_path = "hangjeongdong_서울특별시.geojson"

df = pd.read_excel(file_path)

# "자치구", "행정동" 칼럼 유지, 나머지는 지표 데이터
fixed_columns = ["자치구", "행정동"]
data_columns = [col for col in df.columns if col not in fixed_columns]

# 대분류 추출
df_categories = {col: col.split("-")[0] for col in data_columns}
categories = set(df_categories.values())

# 사용자 입력 (소분류 가중치 입력)
print("\n💡 [소분류 가중치 입력] 각 소분류 지표의 가중치를 -1 ~ 1 범위로 입력하세요.")
weights_detailed = {}
for col in data_columns:
    while True:
        try:
            weight = int(input(f"{col}: "))
            if -1 <= weight <= 1:
                weights_detailed[col] = weight
                break
            else:
                print("❌ -1과 1 사이의 값만 입력하세요.")
        except ValueError:
            print("❌ 숫자를 입력하세요.")

if all(weight == 0 for weight in weights_detailed.values()):
    print("\n❌ 모든 소분류 가중치를 0으로 입력할 수 없습니다. 최소 하나 이상의 가중치를 입력하세요.")
    exit()

# # 사용자 입력 (대분류 가중치 입력)
# print("\n💡 [대분류 가중치 입력] 각 대분류의 가중치를 -1 ~ 1 범위로 입력하세요.")
# weights_category = {}
# for category in categories:
#     while True:
#         try:
#             weight = int(input(f"{category}: "))
#             if -1 <= weight <= 1:
#                 weights_category[category] = weight
#                 break
#             else:
#                 print("❌ -1과 1 사이의 값만 입력하세요.")
#         except ValueError:
#             print("❌ 숫자를 입력하세요.")

# if all(weight == 0 for weight in weights_category.values()):
#     print("\n❌ 모든 대분류 가중치를 0으로 입력할 수 없습니다. 최소 하나 이상의 가중치를 입력하세요.")
#     exit()

# 최종 Score 계산
df["최종 Score"] = 0
for category in categories:
    category_columns = [col for col in data_columns if df_categories[col] == category]
    # category_weight = weights_category[category]
    
    positive_weights = {col: max(weights_detailed[col], 0) for col in category_columns}
    negative_weights = {col: min(weights_detailed[col], 0) for col in category_columns}
    
    sum_pos_weights = sum(positive_weights.values()) or 1
    sum_neg_weights = sum(negative_weights.values()) or -1
    
    df[f"{category}_점수"] = (
        sum(df[col] * positive_weights[col] for col in category_columns) / sum_pos_weights
        - sum(df[col] * negative_weights[col] for col in category_columns) / sum_neg_weights
    )
    df["최종 Score"] += df[f"{category}_점수"]  # * category_weight

geojson_path = "hangjeongdong_서울특별시.geojson"

# 최종_Score 상위 10개 행정동 추출
df["행정동명"] = df["자치구"] + " " + df["행정동"]
top_10 = df.nlargest(10, "최종_Score")[["행정동명", "최종_Score"] + [f"{category}-점수" for category in categories]]
top_10["순위"] = range(1, 11)

# 최고 대분류 찾기
top_10["최고 대분류"] = top_10[[f"{category}-점수" for category in categories]].idxmax(axis=1)
top_10["최고 대분류"] = top_10["최고 대분류"].apply(lambda x: x.replace("-점수", ""))

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
