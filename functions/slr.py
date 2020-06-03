import json


def do_search(query):
    # TODO: support for this syntax
    # search = {
    #     "search_groups": [
    #         {
    #             "search_terms": ["bitcoin", "test"],
    #             "match_and_or_not": "OR"
    #         },
    #         {
    #             "search_terms": ["bitcoin", "..."],
    #             "match_and_or_not": "OR"
    #         }
    #     ],
    #     "match_and_or": "AND"
    # }
    from wrapper.springerWrap import SpringerWrapper

    # TODO:
    # query multiple databases simultaneously
    # for each db:
    #   send initial query
    #   record how many total results will be returned
    #   query for additional pages in parallel

    springer = SpringerWrapper(apiKey="51502308cc700373e75693f79b5697aa")

    results = springer.callAPI(f'keyword: "{query}"')

    return results


def manage_query(review, search: dict):
    from db.connector import new_query, save_results

    query = new_query(review)

    # search in databases
    results = []
    results += do_search(search)

    save_results(results, review, query)


if __name__ == '__main__':
    pass


# for testing
def populate():
    from db.connector import add_review
    review = add_review("test_query")
    manage_query(review)
