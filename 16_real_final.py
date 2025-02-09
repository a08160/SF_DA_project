import json
import geopandas as gpd
import pandas as pd
import folium
import branca

# ✅ 1. 파일 불러오기
file_path = "최종정렬_preprocessing_data.xlsx"
df = pd.read_excel(file_path)

# ✅ 2. "자치구", "행정동" 칼럼은 유지, 나머지는 지표 데이터
fixed_columns = ["자치구", "행정동"]
data_columns = [col for col in df.columns if col not in fixed_columns]

# 대분류 ("-" 기준 왼쪽 부분) 추출
df_categories = {col: col.split("-")[0] for col in data_columns}
categories = set(df_categories.values())

# ✅ 3. 사용자 입력 (소분류 가중치 입력)
print("\n💡 [소분류 가중치 입력] 각 소분류 지표의 가중치를 -1 ~ 1 범위로 입력하세요.")
weights_detailed = {}
for col in data_columns:
    while True:
        try:
            weight = float(input(f"{col}: "))
            if -1 <= weight <= 1:
                weights_detailed[col] = weight
                break
            else:
                print("❌ -1과 1 사이의 값만 입력하세요.")
        except ValueError:
            print("❌ 숫자를 입력하세요.")

# ✅ 4. 사용자 입력 (대분류 가중치 입력)
print("\n💡 [대분류 가중치 입력] 각 대분류의 가중치를 -1 ~ 1 범위로 입력하세요.")
weights_category = {}
for category in categories:
    while True:
        try:
            weight = float(input(f"{category}: "))
            if -1 <= weight <= 1:
                weights_category[category] = weight
                break
            else:
                print("❌ -1과 1 사이의 값만 입력하세요.")
        except ValueError:
            print("❌ 숫자를 입력하세요.")

# ✅ 5. 최종 Score 계산 (엑셀 저장 없이 바로 활용)
df["최종 Score"] = 0  # 새로운 칼럼 추가

for category in categories:
    category_columns = [col for col in data_columns if df_categories[col] == category]
    category_weight = weights_category[category]  # 대분류 가중치

    # 🔹 양수/음수 가중치 분리
    positive_weights = {col: max(weights_detailed[col], 0) for col in category_columns}
    negative_weights = {col: abs(min(weights_detailed[col], 0)) for col in category_columns}

    # 🔹 분모가 0이 되는 경우 방지 (0이면 기본값 1 적용)
    sum_pos_weights = sum(positive_weights.values()) or 1
    sum_neg_weights = sum(negative_weights.values()) or 1

    # 🔹 대분류별 점수 계산 (양수/음수 가중치 각각 적용)
    df[f"{category}_점수"] = (
        sum(df[col] * positive_weights[col] for col in category_columns) / sum_pos_weights
        - sum(df[col] * negative_weights[col] for col in category_columns) / sum_neg_weights
    )

    # 🔹 최종 점수 계산 (대분류 가중치 적용)
    df["최종 Score"] += df[f"{category}_점수"] * category_weight

# ✅ 6. Folium 지도 생성 과정 (엑셀 대신 df 활용)
geojson_path = "hangjeongdong_서울특별시.geojson"
with open(geojson_path, "r", encoding="utf-8") as f:
    geojson_data = json.load(f)

# ✅ 7. 행정동명 컬럼 생성 (자치구 + 행정동)
df["행정동명"] = df["자치구"] + " " + df["행정동"]

# ✅ 8. GeoJSON 데이터에서 행정동명 추출
for feature in geojson_data["features"]:
    properties = feature["properties"]
    properties["행정동명"] = properties["sggnm"] + " " + properties["adm_nm"].split()[-1]

# ✅ 9. GeoJSON 데이터와 점수 데이터 병합
score_dict = df.set_index("행정동명")["최종 Score"].to_dict()
for feature in geojson_data["features"]:
    properties = feature["properties"]
    properties["최종 Score"] = score_dict.get(properties["행정동명"], None)

# ✅ 10. 점수 범위를 정규화하여 색상 매핑
scores = [f["properties"]["최종 Score"] for f in geojson_data["features"] if f["properties"]["최종 Score"] is not None]
min_score, max_score = min(scores), max(scores)

colormap = branca.colormap.linear.YlGnBu_09.scale(min_score, max_score)
colormap.caption = "최종 Score에 따른 색상 범위"

# ✅ 11. Folium 지도 생성
m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)  # 서울 중심 좌표

# ✅ 12. GeoJSON을 Folium 지도에 추가
folium.GeoJson(
    geojson_data,
    name="서울 행정동",
    style_function=lambda feature: {
        "fillColor": colormap(feature["properties"]["최종 Score"]) if feature["properties"]["최종 Score"] is not None else "#ffffff",
        "color": "black",
        "weight": 0.5,
        "fillOpacity": 0.7,
    },
    tooltip=folium.GeoJsonTooltip(
        fields=["행정동명", "최종 Score"],
        aliases=["행정동", "최종 Score"],
        localize=True,
        sticky=True,
        labels=True,
        style="background-color: white; color: black; font-size: 12px; font-weight: bold;",
    ),
).add_to(m)

# ✅ 13. 컬러바 추가
colormap.add_to(m)

# ✅ 14. HTML 파일로 저장
map_file_path = "my_map.html"
m.save(map_file_path)

print(f"\n✅ 지도 생성 완료: {map_file_path}")
