def do_search(query):
    from wrapper.springerWrap import SpringerWrapper

    springer = SpringerWrapper(apiKey="***REMOVED***")

    res = springer.callAPI(f'keyword: "{query}"')

    return res

