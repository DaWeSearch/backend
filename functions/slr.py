def do_search(query):
    from wrapper.springerWrap import SpringerWrapper

    springer = SpringerWrapper(apiKey="51502308cc700373e75693f79b5697aa")

    res = springer.callAPI(f'keyword: "{query}"')
    print(res)

    return res