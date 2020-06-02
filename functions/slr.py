import json


def do_search(query):
    from wrapper.springerWrap import SpringerWrapper

    springer = SpringerWrapper(apiKey="51502308cc700373e75693f79b5697aa")

    results = springer.callAPI(f'keyword: "{query}"')

    # from .db.connector import save_results

    # save_results(review_id, results)

    return results


if __name__ == '__main__':
    do_search("bitcoin")
