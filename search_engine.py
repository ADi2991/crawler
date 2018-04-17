import scorer as scorer
import csv
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

eng_stopwords = stopwords.words('english')
knn = scorer.KNN(5)
clusters = knn.cluster(scorer.doc_headers, scorer.data[scorer.doc_headers])
cluster_hierarchy = knn.cluster_hierarchy().values()
leaders_idx = [cluster['leader'] for cluster in cluster_hierarchy]
leaders = [scorer.doc_headers[idx] for idx in leaders_idx]
followers = [cluster['followers'] for cluster in cluster_hierarchy]


print("Cluster hierarchy %s" % cluster_hierarchy)

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
    for i in results:
        print("%s (score: %s)\n%s...\nURL: %s\n" % (i[1], i[4], i[2], i[3]))

thesaurus = read_thesaurus_from_file()
while True:
    print("\n")
    print("--------------------")
    query = input("Enter query: ")
    query = query.lower()
    if query == "quit":
        break
    else:
        query_words = word_tokenize(query)
        query_no_stopwords = [word for word in query_words if word not in eng_stopwords]
        if len(query_no_stopwords) > 0:
            queries = get_alternate_queries(query_no_stopwords, thesaurus)
        else:
            print("Query has only stopwords..using query as it is")
            queries = get_alternate_queries(query_words, thesaurus)
        for query in queries:
            query_concat = str(query)
            print('Using query "%s"' % query_concat)
            results = get_top_results(query_concat, 6)
            if len(results) >= 3:
                print("Top %s results:" % (len(results)))
                print_results(results)
                break
            else:
                print("Number of results less than 3, using thesaurus expansion..")
                pass
        if len(results) <= 3:
            if len(results) == 0:
                print("Thesaurus expansion failed, no results found")
            else:
                print("Could only get the following results:")
                print_results(results)


