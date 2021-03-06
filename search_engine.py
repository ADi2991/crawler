import scorer as scorer
import csv
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

eng_stopwords = stopwords.words('english')
knn = scorer.KNN(5)
clusters = knn.cluster(scorer.doc_headers, scorer.norm_doc_vec)
cluster_hierarchy = knn.cluster_hierarchy()
knn.calculate_cluster_scores(cluster_hierarchy)


# print("Cluster hierarchy %s" % cluster_hierarchy)

# def make_legible(cluster_hierarchy, doc_headers, tp): #tp = titles_previews dataframe
#     leaders_idx = [cluster_hierarchy[cluster]['leader'] for cluster in cluster_hierarchy]
#     leaders = [doc_headers[idx] for idx in leaders_idx]
#     followers_idx = [cluster_hierarchy[cluster]['followers'] for cluster in cluster_hierarchy]
#
#     def make_legible():
#         legible_hier = dict()
#         def get_title_by_idx(idx):
#             header = doc_headers[idx]
#             table = tp
#             table = table[table['Document'] == header]
#             return table['title'].values[0]
#         for cluster in range(len(leaders_idx)):
#             leader = get_title_by_idx(leaders_idx[cluster])
#             followers = [get_title_by_idx(follower_id) for follower_id in followers_idx[cluster]]
#             legible_hier[cluster] = dict()
#             legible_hier[cluster]['leader'] = str(leader)
#             legible_hier[cluster]['follower'] = [str(follower) for follower in followers]
#         return legible_hier
#
#     legible = make_legible()
#     for cluster in legible:
#         ldr = legible[cluster]['leader']
#         flwr = legible[cluster]['follower']
#         print("cluster %d\nleader: %s\nfollowers: %s\n" % (cluster, ldr, flwr))

# Copy of prev
def make_legible(cluster_hierarchy, doc_headers, tp, cluster_scores): #tp = titles_previews dataframe
    leaders_idx = [cluster_hierarchy[cluster]['leader'] for cluster in cluster_hierarchy]
    leaders = [doc_headers[idx] for idx in leaders_idx]
    followers_idx = [cluster_hierarchy[cluster]['followers'] for cluster in cluster_hierarchy]

    def make_legible():
        legible_hier = dict()
        def get_title_by_idx(idx):
            header = doc_headers[idx]
            table = tp
            table = table[table['Document'] == header]
            return table['title'].values[0]
        for cluster in range(len(leaders_idx)):
            leader = get_title_by_idx(leaders_idx[cluster])
            followers = [get_title_by_idx(follower_id) for follower_id in followers_idx[cluster]]
            legible_hier[cluster] = dict()
            legible_hier[cluster]['leader'] = str(leader)
            legible_hier[cluster]['follower'] = [str(follower) for follower in followers]
        return legible_hier

    legible = make_legible()
    print("{Indicating distance from leader as dist}")
    for cluster in legible:
        ldr = legible[cluster]['leader']
        flwr = legible[cluster]['follower']
        scores = cluster_scores[cluster]
        print("cluster %d\nleader: %s\nfollowers: " % (cluster, ldr))
        for id in range(len(flwr)):
            print("%s (dist: %f)" % (flwr[id], scores[id]), end=",")
        print("")


def get_top_results(query, n):
    scores = scorer.get_score(query)
    non_zero_scores = scores[scores.values > 0]
    # document_nos = [leader for leader in leaders if leader in non_zero_scores.index]
    document_nos = non_zero_scores.index
    details = scorer.titles_previews.copy()
    details.index = details['Document']
    details.loc[document_nos, 'scores'] = non_zero_scores.values
    results = details.loc[document_nos][:n]
    return results.values


def read_thesaurus_from_file():
    thesaurus = dict()
    with open('thesaurus.csv', 'r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        rows = [row for row in reader]
        for i in range(len(rows)):
            rows[i] = [word.strip().lower() for word in rows[i] if word != '']
        for i in range(len(rows)):
            if i > 0:
                word = rows[i].pop(0)
                thesaurus[word] = rows[i]
    return thesaurus

def get_alternate_queries(query_words, thesaurus):
    queries = []

    def thesaurus_expander(query_words, current_query):
        current_word = query_words[0]
        words_to_try = []
        if current_word in thesaurus:
            words_to_try = list(thesaurus[current_word])
        words_to_try.insert(0, current_word)
        for word in words_to_try:
            if current_query != '':
                new_query = current_query+' '+word
            else:
                new_query = current_query + word
            if len(query_words)>1:
                thesaurus_expander(query_words[1:], new_query)
            else:
                queries.append(new_query)
    thesaurus_expander(query_words, '')
    for query in queries:
        yield query

def print_results(results):
    rank = 1
    for i in results:
        print("%s: %s (score: %s)\n%s...\nURL: %s\n" % (rank, i[1], i[4], i[2], i[3]))
        rank += 1

def display_results(results, mode, ldr_score=0):
    if mode in ['a', 'A']:
        print_results(results)
    else:
        scorer.print_cluster_details(results, ldr_score, 6)

thesaurus = read_thesaurus_from_file()
tp = scorer.titles_previews.copy()
# print("Cluster hierarchy:\n", )
make_legible(cluster_hierarchy, scorer.doc_headers, tp, knn.cluster_scores)
while True:
    print("\n")
    print("--------------------")
    query = input("Enter query: ")
    query = query.lower()
    if query == "quit":
        print("Goodbye!")
        break
    else:
        query_words = word_tokenize(query)
        query_no_stopwords = [word for word in query_words if word not in eng_stopwords]

        if len(query_no_stopwords) == 0:
            print("Query has only stopwords..please enter a different query")
        else:
            queries = get_alternate_queries(query_words, thesaurus)
            for query in queries:
                query_concat = str(query)
                print('Using query "%s"' % query_concat)
                print("Searching all documents...\n")
                results = get_top_results(query_concat, 6)
                if len(results) >= 3:
                    print("Top %s results:" % (len(results)))
                    print_results(results)
                    break
                else:
                    print("Number of results less than 3, using thesaurus expansion..")
                    pass
            if len(results) < 3:
                if len(results) == 0:
                    print("Thesaurus expansion failed, no results found")
                else:
                    print("Could only get the following results:")
                    print_results(results)
