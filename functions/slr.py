import json


def do_search(query):
    from wrapper.springerWrap import SpringerWrapper

    springer = SpringerWrapper(apiKey="***REMOVED***")

    results = springer.callAPI(f'keyword: "{query}"')

    from .db.connector import save_results

    save_results(results)

    return results


if __name__ == '__main__':
    do_search("bitcoin")
