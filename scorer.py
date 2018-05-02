import pandas as pd
import numpy as np
from nltk.tokenize import word_tokenize
import nltk.stem.porter as porter
from collections import Counter

data = pd.read_csv('tf-df.csv')
titles_previews = pd.read_csv('title_preview.csv')
doc_headers = [column for column in data.columns if 'Document' in column]
titles_previews = titles_previews.fillna("N/A")
titles_previews['title'] = titles_previews['title'].apply(lambda word: word.lower())

# normalize document
doc_tf = data[doc_headers]

def ntc_normalize(tf, df):
    vecs = tf.copy()
    norm_doc_freq = np.log(len(vecs.columns)/df)
    # tf.df
    vecs = vecs.multiply(norm_doc_freq, axis='rows')
    # Cosine normalization:
    sum_sq = np.sum(vecs**2, axis=0)
    vecs = vecs/np.sqrt(sum_sq)
    return vecs

def ltc_normalize(tf, df):
    vecs = tf.copy()
    # log normalization
    vecs = 1 + np.log(vecs[vecs!=0])
    # df normalization
    norm_doc_freq = np.log(len(doc_headers) / df)
    # tf.df
    vecs = vecs.multiply(norm_doc_freq, axis='rows')
    # Cosine normalization:
    sum_sq = np.sum(vecs**2, axis=0)
    vecs = vecs/np.sqrt(sum_sq)
    return vecs

def nnc_normalize(tf, df):
    vecs = tf.copy()
    norm_doc_freq = 1
    # tf.df
    vecs = vecs.multiply(norm_doc_freq, axis='rows')
    # Cosine normalization:
    sum_sq = np.sum(vecs**2, axis=0)
    vecs = vecs/np.sqrt(sum_sq)
    return vecs

def lnc_normalize(tf, df):
    vecs = tf.copy()
    # log normalization
    vecs = 1 + np.log(vecs[vecs != 0])
    norm_doc_freq = 1
    # tf.df
    vecs = vecs.multiply(norm_doc_freq, axis='rows')
    # Cosine normalization:
    sum_sq = np.sum(vecs**2, axis=0)
    vecs = vecs/np.sqrt(sum_sq)
    return vecs


# normalize doc vecs
# norm_doc_vec = ntc_normalize(doc_tf, data['df'])
norm_doc_vec = nnc_normalize(doc_tf, data['df'])

def get_stemmed_tokenized_query(query):
    stemmer = porter.PorterStemmer(mode='ORIGINAL_ALGORITHM')
    # get tokenize'd words from query
    words = word_tokenize(query)
    # get stemmed words from query
    words = list(map(stemmer.stem, words))
    return words


# word_series is the series of words in our data, i.e data['word']
def get_query_tf(query, word_series):
    tf = word_series.copy()
    words = get_stemmed_tokenized_query(query)

    # count the occurrences
    freq = Counter(words)
    # set the value as the count if it exists, else 0
    tf = tf.transform(lambda word: freq[word] if word in freq else 0)
    return tf


# takes in normalized vecs and gives cosine score
def get_similarity_scores(norm_docs, norm_query):
    cosine_prod = norm_docs.multiply(norm_query, axis=0)
    return cosine_prod.sum(axis=0)


# calculates the bonus score according
def calculate_bonus_score(string, words):
    intersection = [word for word in words if word in string]
    return 0.25 * len(intersection)


# returns query score with bonus (title)
def get_score(query):
    query_words = get_stemmed_tokenized_query(query)
    # normalize query
    query_tf = get_query_tf(query, data['word'])
    norm_query_vec = nnc_normalize(query_tf, data['df'])

    modif = get_similarity_scores(norm_doc_vec, norm_query_vec)
    titles = titles_previews['title'].copy()
    titles.index = modif.index
    titles = titles.transform(lambda string: calculate_bonus_score(string, query_words))
    return (titles+modif).sort_values(ascending=False)

def get_normalized_query(query):
    query_tf = get_query_tf(query, data['word'])
    return nnc_normalize(query_tf, data['df'])

def get_nearest_cluster(query, cluster_hierarchy):
    leaders_idx = [cluster_hierarchy[cluster]['leader'] for cluster in cluster_hierarchy]
    ldr_headers = [doc_headers[ldr] for ldr in leaders_idx]
    vecs = norm_doc_vec.loc[:, ldr_headers].copy()
    query_words = get_stemmed_tokenized_query(query)
    norm_query_vec = get_normalized_query(query)

    modif = get_similarity_scores(vecs, norm_query_vec)
    tp = titles_previews.query("Document in " + str(ldr_headers))
    titles = tp['title'].copy()
    titles.index = modif.index
    titles = titles.transform(lambda string: calculate_bonus_score(string, query_words))
    total_scores = (titles + modif)
    doc = total_scores.idxmax()
    doc_id = doc_headers.index(doc)
    cluster_id = leaders_idx.index(doc_id)
    leader_score = total_scores[doc]
    return cluster_id, leader_score

def unpack_cluster(cluster_hier, cluster_id):
    leader = cluster_hier[cluster_id]['leader']
    followers = cluster_hier[cluster_id]['followers']

    docs = followers.copy()
    docs.insert(0, leader)
    return titles_previews.loc[docs].values

def print_cluster_details(details_subset, ldr_score, limit):
    rank = 1
    for i in details_subset:
        if rank > limit:
            break
        else:
            print("%s: %s (leader score: %s)\n%s...\nURL: %s\n" % (rank, i[1], ldr_score, i[2], i[3]))
            rank += 1


class KNN:
    def __init__(self, N):
        self.N = N

    def get_empty_clusters(self, N):
        clusters = dict()
        for i in range(N):
            clusters[i] = []
        return clusters

    def initialize_state(self, doc_headers, vecs):
        self.doc_headers = doc_headers
        self.vecs = vecs
        self.clusters = self.get_empty_clusters(self.N)

        # indices = np.arange(len(doc_headers))
        # np.random.shuffle(indices)
        doc_count = len(doc_headers)
        # indices = np.arange(start=0, stop=doc_count, step=doc_count/self.N, dtype=np.int)
        # indices = [0, 7, 15, 22, 30]
        indices = np.arange(0, 35, 6)

        for i in range(self.N):
            self.clusters[i].append(indices[i])

    # Calculates the centroids given clusters
    def get_centroids(self, clusters):
        cluster_centroids = []
        for i in clusters:
            cluster_vectors = [self.vecs[self.doc_headers[doc_nos]] for doc_nos in clusters[i]]
            # centroid = np.sum(cluster_vectors, axis=0)/len(clusters[i])
            centroid = np.mean(cluster_vectors, axis=0)
            cluster_centroids.append(centroid)
        return cluster_centroids

    # Get a matrix of shape(docs x clusters) containing the distance of doc from each cluster centroid.
    def get_absolute_distances(self, doc_headers, cluster_centroids):
        dist_matrix = np.zeros(shape=(len(doc_headers), len(cluster_centroids)), dtype=float)
        for vec in range(len(doc_headers)):
            for centroid in range(len(cluster_centroids)):
                vec_difference = self.vecs[doc_headers[vec]] - cluster_centroids[centroid]
                magnitude = np.sum(vec_difference ** 2)
                dist_matrix[vec][centroid] = np.sqrt(magnitude)
        return dist_matrix

    def get_clusters(self, dist_matrix):
        clusters = self.get_empty_clusters(self.N)
        distances = np.apply_along_axis(np.argmin, 1, dist_matrix)
        for doc in range(len(distances)):
            nearest = distances[doc]
            clusters[nearest].append(doc)
        return clusters

    def cluster_hierarchy(self):
        clust_hier = dict()
        clusters = self.clusters
        for i in clusters:
            clust_hier[i] = dict()
            dist_from_centroid = self.dist_matrix[clusters[i], i]
            closest = np.argmin(dist_from_centroid)
            leader = clusters[i][closest]
            clust_hier[i]['leader'] = leader
            clust_hier[i]['followers'] = [doc for doc in clusters[i] if doc != leader]
        return clust_hier

    def cluster(self, doc_headers, vecs):
        self.initialize_state(doc_headers, vecs)
        self.clusters = self.iteration(self.clusters)
        converged = False

        while (converged == False):
            calculated_clusters = self.iteration(self.clusters)
            converged = self.clusters == calculated_clusters
            self.clusters = calculated_clusters
        return self.clusters.copy()

    def iteration(self, clusters):
        cluster_centroids = self.get_centroids(clusters)
        self.dist_matrix = self.get_absolute_distances(self.doc_headers, cluster_centroids)
        return self.get_clusters(self.dist_matrix)

    def calculate_cluster_scores(self, cluster_hierarchy):
        cluster_scores = dict()
        for cluster in cluster_hierarchy:
            cluster_scores[cluster] = list()
            followers_idx = cluster_hierarchy[cluster]['followers']
            leader_idx = cluster_hierarchy[cluster]['leader']

            def get_doc_by_id(id):
                header = doc_headers[id]
                return norm_doc_vec[header].copy()

            for i in range(len(followers_idx)):
                vec_sub = get_doc_by_id(leader_idx) - get_doc_by_id(followers_idx[i])
                score = np.sqrt(np.sum(vec_sub ** 2))
                cluster_scores[cluster].append(score)
        self.cluster_scores = cluster_scores

