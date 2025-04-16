import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import matplotlib.font_manager as fm
from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.model_selection import KFold, GridSearchCV
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn_extra.cluster import KMedoids
from sklearn.pipeline import Pipeline
from sklearn.metrics import make_scorer, silhouette_score

# 데이터 불러오기
df = pd.read_excel("찐막_preprocessing_data.xlsx")

# 데이터 표준화
scaler = MinMaxScaler()
df_scaled = scaler.fit_transform(df)

# PCA 수행
pca = PCA(n_components=7)
df_pca = pca.fit_transform(df_scaled)

# 파이프라인 정의
pipe = Pipeline([('classifier', None)])

# 실루엣 계수 scorer 정의
silhouette_scorer = make_scorer(silhouette_score)

# GridSearchCV에 전달할 scoring 매개변수
scoring = {'silhouette': silhouette_scorer}

# KFold 설정
kfold = KFold(n_splits=5, shuffle=True, random_state=2)

# 하이퍼파라미터 그리드
hyperparam_grid = [
    # KMeans
    {'classifier': [KMeans()],
     'classifier__n_clusters': [3, 4, 5, 6, 7],
     'classifier__init': ['k-means++', 'random'],
     'classifier__n_init': [10, 20],
     'classifier__max_iter': [100, 300],
     'classifier__tol': [1e-4, 1e-3]
    },

    # KMedoids
    {'classifier': [KMedoids()],
     'classifier__n_clusters': [3, 4, 5, 6, 7],
     'classifier__metric': ['euclidean', 'manhattan'],
     'classifier__max_iter': [100, 300],
     'classifier__random_state': [42],
     'classifier__init': ['random']
    },

    # AgglomerativeClustering
    {'classifier': [AgglomerativeClustering()],
     'classifier__n_clusters': [3, 4, 5, 6, 7],
     'classifier__metric': ['euclidean', 'manhattan'],
     'classifier__linkage': ['complete', 'average', 'single'],
     'classifier__compute_distances': [True, False]
    }
]

# GridSearchCV 설정
grid = GridSearchCV(pipe, hyperparam_grid, scoring=scoring, refit='silhouette', cv=kfold)

# GridSearchCV 실행
grid.fit(df_pca)

# 실루엣 계수에 대해 상위 3개 모델 출력
print("Top 3 models by silhouette score:")
silhouette_results = grid.cv_results_['mean_test_silhouette']
silhouette_indices = silhouette_results.argsort()[-3:][::-1]

for i in silhouette_indices:
    print(f"Model: {grid.cv_results_['params'][i]} | Silhouette Score: {silhouette_results[i]:.5f}")