from typing import Any

import numpy as np
from sklearn.cluster import AgglomerativeClustering
from sklearn.base import BaseEstimator, ClusterMixin

def align_labels(labels: np.ndarray) -> np.ndarray:
    indexes = sorted(np.unique(labels, return_index=True)[1])
    uniques = np.array([labels[i] for i in indexes])
    uniques = uniques[uniques > -1]
    for i, label in enumerate(uniques):
        labels[labels == label] = i
    return labels

class Clustering(BaseEstimator, ClusterMixin):
    def __init__(self, min_cluster_size: int = 2, cosine_thrsh: float = 0.4):
        self.tol = 1e-5
        self.min_cluster_size = min_cluster_size
        self.cosine_thrsh = cosine_thrsh

    def fit(self, X: Any = None, y: Any = None) -> ClusterMixin:
        return self

    def predict(self, X: np.ndarray, y: Any = None) -> np.ndarray:
        cluster = AgglomerativeClustering(
            affinity="cosine",
            linkage="complete",
            distance_threshold=self.cosine_thrsh,
            n_clusters=None
        ).fit(X)
        return cluster.labels_

    def _filter_rare_labels(self, labels: np.ndarray) -> np.ndarray:
        classes, counts = np.unique(labels, return_counts=True)
        noisy_labels = set(classes[counts < self.min_cluster_size])
        for i in range(len(labels)):
            if labels[i] in noisy_labels:
                labels[i] = -1
        return labels

    def fit_predict(self, X: np.ndarray, y: Any = None) -> np.ndarray:
        # NOTE: assign -1 label to zero vectors, 
        #       since cosine distance is not defined for them
        normed = np.linalg.norm(X, axis=1)
        zero_norm_idxs = normed <= self.tol
        X_filtered = X[~zero_norm_idxs]
        result_labels = np.full(X.shape[0], -1)
        if X_filtered.shape[0] == 0:
            return result_labels
        labels = self.predict(X_filtered)
        result_labels[~zero_norm_idxs] = labels
        result_labels = self._filter_rare_labels(result_labels)
        result_labels = align_labels(result_labels)
        return result_labels
