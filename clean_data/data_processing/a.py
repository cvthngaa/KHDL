from sklearn.cluster import AgglomerativeClustering
from scipy.spatial.distance import cdist
import numpy as np

k = 3  # số cụm
agg = AgglomerativeClustering(n_clusters=k,metric='euclidean' ,linkage='average')
labels_train = agg.fit_predict(X_train)

# Thêm cột nhãn cụm vào df_train
df_train['Cụm'] = labels_train

# Tính tâm cụm
centroids = np.array([X_train[labels_train == i].mean(axis=0) for i in range(k)])

# Gán nhãn cho tập test theo centroid gần nhất
distances = cdist(X_test, centroids)
labels_test = distances.argmin(axis=1)

# Thêm cột nhãn cụm vào df_test
df_test['Cụm'] = labels_test


