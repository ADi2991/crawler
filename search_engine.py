import scorer as scorer


def get_top_results(query, n):
    scores = scorer.get_score(query)
    return scores[:n]

while True:
    query = input("Enter query:")
    query = query.lower()
    if query == "quit":
        break
    else:
        results = get_top_results(query, 6)
        print(results)
        # if len(results) >= 6:
        #     print("Top %s results:%s" % (n, results))
        # else:
        #     pass
