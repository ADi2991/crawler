import scorer as scorer
import csv
from nltk.tokenize import word_tokenize

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

thesaurus = read_thesaurus_from_file()
while True:
    print("\n")
    print("--------------------")
    query = input("Enter query: ")
    query = query.lower()
    if query == "quit":
        break
    else:
        queries = get_alternate_queries(word_tokenize(query), thesaurus)
        for query in queries:
            query_concat = str(query)
            print('Using query "%s"' % query_concat)
            results = get_top_results(query_concat, 6)
            if len(results) >= 3:
                print("Top %s results:" % (len(results)))
                for i in results:
                    print("%s: %s\n%s...\n" % (i[0], i[1], i[2]))
                break
            else:
                print("Number of results less than 3, using thesaurus expansion..")
                pass
        if len(results) <= 3:
            if len(results) == 0:
                print("Thesaurus expansion failed, no results found")
            else:
                print("Thesaurus expansion failed, could only get the following results:")
                for i in results:
                    print("%s: %s\n%s...\n" % (i[0], i[1], i[2]))



