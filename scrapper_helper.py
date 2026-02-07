
MAX_VISIT = 4

def store_url(url:str, blacklist: set[str], url_dict: dict[str: int]):
    if url not in url_dict.keys():
        url_dict[url] = 1
    else:
        if url_dict[url] > MAX_VISIT:
            blacklist.add(url)
        else:
            url_dict[url] += 1
