import os
from typing import List, Dict, Set, Union, Optional, Tuple
from functools import partial

import numpy as np
from sklearn.feature_extraction.text import CountVectorizer # type: ignore

from scipy.cluster.hierarchy import linkage # type: ignore
from scipy.cluster.hierarchy import fcluster
from scipy.spatial.distance import pdist # type: ignore
from scipy.spatial import distance # type: ignore

from .feature_extractors import FasttextExtractor, TfidfExtractor
from .preprocessing import Preprocessor

from .local_types import *
from .config import ClusteringConfig

class NaiveLangDetector:

    def __init__(self):
        self.__latin_letters = set(u"qwertyuiopasdfghjklzxcvbnm")
        self.__digits = set(u"1234567890")

    def get_lang(self, text: str) -> str:
        letters = list(text.lower().strip())
        d = {"latin":0, "digits":0, "other":0}
        for letter in letters:
            if letter in self.__latin_letters:
                d["latin"] += 1
            elif letter in self.__digits: 
                d["digits"] += 1
            else: 
                d["other"] += 1
        if d["digits"] < len(letters):
            d["digits"] = 0
        else:
            return "latin"
        return sorted(d.items(), key=lambda v: v[1], reverse=True)[0][0]

class ClusteringPipeline:

    def __init__(self, config: ClusteringConfig, stop_words: Optional[List[str]] = None):
        self.__lang_detector = NaiveLangDetector()
        self.__outliers_class_name = "none"
        self.__preprocessor = Preprocessor(stop_words=stop_words, placeholder=self.__outliers_class_name)
        self.__fasttext_extractor = FasttextExtractor(
            partial(self.__preprocessor.run, replace_dates=False, replace_digits=False),
            config
        )
        self.__tfidf_extractor = TfidfExtractor(
            partial(self.__preprocessor.run, replace_dates=True, replace_digits=True)
        )
        self.__valid_extractors_names = set(["fasttext", "tfidf"])
        self.__min_cluster_size = config.min_cluster_size
        self.__center_data = config.center_fasttext_vectors

    def __get_merged_clusters_map(self, titles: Titles, cosine_thrsh: float = 0.45) -> ClustersMerge:
        seen = set([-1])
        clusters_map: Dict[int, Set[int]] = {-1:set()}
        titles_features = self.__fasttext_extractor.get_features(list(titles.values()))
        titles_features_dict = {k:v["mean"] for k, v in zip(list(titles.keys()), titles_features)}
        for k1, v1 in titles.items():
            if k1 in seen:
                continue
            clusters_map[k1] = set()
            for k2, v2 in titles.items():
                if k2 in seen:
                    continue
                dist = distance.cosine(
                    titles_features_dict[k1],
                    titles_features_dict[k2]
                )
                if dist <= cosine_thrsh:
                    clusters_map[k1].add(k2)
                    seen.add(k2)
        return clusters_map

    def get_clusters(self, inp: Union[List[str], np.ndarray], features_type: str = "fasttext") -> Tuple[Titles, np.ndarray]: 
        if len(inp) == 0:
            return {}, np.array([])
        if features_type not in self.__valid_extractors_names:
            raise ValueError("List of valid feature extractors names: {}".format(self.__valid_extractors_names))

        fault_lang_mask = np.full(len(inp), False)
        for i, text in enumerate(inp):
            lang = self.__lang_detector.get_lang(text)
            if lang == "other":
                inp[i] = self.__outliers_class_name
                fault_lang_mask[i] = True

        if features_type == "fasttext":
            prep = self.__fasttext_extractor.preprocess_texts(inp)
            features = np.concatenate([
                np.concatenate(list(vecs.values()))[np.newaxis, :]
                for vecs in self.__fasttext_extractor.get_features(prep)
            ], axis=0)
            if self.__center_data:
                features = features - features.mean(axis=0)
        elif features_type == "tfidf":
            prep = self.__tfidf_extractor.preprocess_texts(inp)
            features = self.__tfidf_extractor.get_features(prep)

        dist = pdist(features, metric='cosine')
        dist[np.isnan(dist)] = 1
        labels = get_clusters_by_dist_matrix(dist, self.__min_cluster_size)
        labels = filter_rare_labels(labels, self.__min_cluster_size)
        labels[fault_lang_mask] = -1
        titles = get_clusters_titles(labels, prep)
        clusters_map = self.__get_merged_clusters_map(titles)
        titles = merge_clusters_titles(titles, clusters_map)
        labels = merge_clusters_labels(labels, clusters_map)
        labels = filter_rare_labels(labels, self.__min_cluster_size)
        return titles, labels

def get_clusters_by_dist_matrix(dist: np.ndarray, min_cluster_size: int) -> np.ndarray:
    Z = linkage(dist, 'complete', metric="cosine")
    opt_thrsh = find_optimal_thrsh(Z, min_cluster_size)
    labels = fcluster(Z, opt_thrsh, 'distance')
    return labels

def merge_clusters_labels(labels: np.ndarray, clusters_map: ClustersMerge) -> np.ndarray:
    for i, _ in enumerate(labels):
        if labels[i] not in clusters_map:
            for k, v in clusters_map.items():
                if labels[i] in v:
                    labels[i] = k
    return labels

def merge_clusters_titles(titles: Titles, clusters_map: ClustersMerge) -> Titles:
    new_titles = dict()
    for k in titles:
        if k in clusters_map:
            new_titles[k] = titles[k]
    return new_titles

def get_clusters_titles(labels: np.ndarray, text: np.ndarray) -> Titles:
    classes = np.unique(labels)
    examples: Dict[int, ClusterNgrams] = {}
    titles: Dict[int, str] = {}
    counter = CountVectorizer(analyzer=u'word', ngram_range=(1, 3), tokenizer=None, stop_words=None,
                              max_features=5000, strip_accents="unicode", max_df=1.0, min_df=1, lowercase=True)
    for c in classes:
        if c == -1:
            titles[c] = "none"
            continue
        if c not in examples:
            examples[c] = {}
        counts = counter.fit_transform(text[labels == c])
        voc = counter.vocabulary_
        summ = np.array(counts.sum(axis=0)).flatten()
        for word in voc:
            n_words = len(word.split())
            if n_words not in examples[c]:
                examples[c][n_words] = {}
            examples[c][n_words][word] = summ[voc[word]]
        titles[c] = get_compound_title(examples[c], min_title_len=4)
        # titles[c] = get_most_frequent_title(examples[c])
    return titles

def join_new_line(tokens: List[str]) -> str:
    return "\n".join(tokens)

def get_compound_title(buckets: ClusterNgrams, min_title_len: int = 4) -> str:
    title: List[str] = []
    total_title_len = 0
    for bucket in buckets.keys():
        sorted_ngrams = sorted(buckets[bucket].items(), key=lambda v: v[1], reverse=True)[:2]
        for ngram in sorted_ngrams:
            if ngram[1] > 1 or (bucket == 1 and len(title) == 0):
                if set(title) == set(ngram[0].split()):
                    continue
                title.append(ngram[0])
                total_title_len += bucket
            if total_title_len >= min_title_len:
                return join_new_line(title)
    return join_new_line(title)

def get_most_frequent_title(buckets: ClusterNgrams) -> str:
    titles: Dict[int, Tuple[str, int]] = {}
    # 1 step filtering n-grams: keep the most frequent one for each "length" bucket
    for bucket in buckets.keys():
        max_ngram = max(buckets[bucket].items(), key=lambda v: v[1])
        titles[bucket] = max_ngram
    # 2 step filtering n-grams: leave a single longest and more frequent n-gram
    if len(titles):
        return max(titles.items(), key=lambda v: v[1][1])[1][0]
    return "none"

def filter_rare_labels(labels: np.ndarray, min_cluster_size: int = 2) -> np.ndarray:
    classes, counts = np.unique(labels, return_counts=True)
    noisy_labels = set(classes[counts <= min_cluster_size])
    for i in range(len(labels)):
        if labels[i] in noisy_labels:
            labels[i] = -1
    return labels

def get_labels_count_std(labels: np.ndarray) -> float:
    classes, counts = np.unique(labels, return_counts=True)
    return np.std(counts)

def find_optimal_thrsh(Z: np.ndarray, min_cluster_size: int = 2) -> float:
    thrsh_high = Z[:, 2].max()
    steps = round((thrsh_high - 0.5) / 0.01)
    thrshs = np.linspace(0.5, thrsh_high, steps)[1:-1]
    weights: List[float] = []
    for thrsh in thrshs:
        labels = fcluster(Z, thrsh, 'distance')
        labels = filter_rare_labels(labels, min_cluster_size)
        weight = get_labels_count_std(labels)
        weights.append(weight)
    return thrshs[np.argmin(weights)]
