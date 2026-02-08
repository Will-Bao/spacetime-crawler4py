import re
import threading
from urllib.parse import urlparse, urljoin, urlunparse
from bs4 import BeautifulSoup
from tokenizer import tokenize, compute_word_frequencies
from scrapper_helper import store_url

COMMON_WORDS_COUNT = 50
MAX_PAGE_SIZE = 2000000

blackList_host = {"swiki.ics.uci.edu", "calendar.ics.uci.edu", "ngs.ics.uci.edu", "grape.ics.uci.edu", "isg.ics.uci.edu", 
                  "intranet.ics.uci.edu", "wics.ics.uci.edu", "wiki.ics.uci.edu", "www.cs.jhu.edu", "cs.jhu.edu", "www.physics.uci.edu",
                  "doi.org", "dx.doi.org", "arxiv.org", "ieeexplore.ieee.org", "www.cs.cmu.edu", "cs.cmu.edu"}
blacklist_path = {"/~eppstein/pix/", "/events/"}
blacklist_url = set()
unique_urls = dict() # dictionary of keys: url and value: visit_counter
longest_page = {"url": "", "length": -1}
common_words = dict()
check_sums = []
subdomain_page_count = dict()
report_file = "report.txt"

data_lock = threading.Lock()

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]


def extract_next_links(url: str, resp):
    # Implementation required.
    # url: the URL that was used to get the page
    # resp.url: the actual url of the page
    # resp.status: the status code returned by the server. 200 is OK, you got the page. Other numbers mean that there was some kind of problem.
    # resp.error: when status is not 200, you can check the error here, if needed.
    # resp.raw_response: this is where the page actually is. More specifically, the raw_response has two parts:
    #         resp.raw_response.url: the url, again
    #         resp.raw_response.content: the content of the page!
    # Return a list with the hyperlinks (as strings) scrapped from resp.raw_response.content
    if not (can_extract(resp)):
        return list()

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")

    file_sum = 0
    tokenized_text = []
    for currentText in soup.stripped_strings:
        # Gets the current text from a generator that contains the content of the webpage
        token_values = tokenize(currentText)
        tokenized_text.extend(token_values[0])
        file_sum += token_values[1]

    if file_sum in check_sums:
        print("This is a duplicate of a pre-existing URL.")
        return list()
    else:
        check_sums.append(file_sum)
        

    links = get_links(soup, resp.url)

    with data_lock:
        check_page_length(len(tokenized_text), resp.url)
        compute_word_frequencies(tokenized_text, common_words)
        store_url(url, blacklist_url, unique_urls)
        increment_subdomain_count(resp.url, subdomain_page_count)
        
        sorted_frequencies = sorted(common_words.items(), key = lambda x: x[1], reverse = True)
        update_report(unique_urls, longest_page, sorted_frequencies, subdomain_page_count)
    return links


def get_links(soup: BeautifulSoup, url: str):
    # Retrieves the links on the web page.
    found_links = set()
    extracted_links = soup.find_all("a", href=True)

    for tag in extracted_links:
        # Convert to full url
        href = tag.get("href")
        full_url = urljoin(url, href)

        # Defragment url
        parsed = urlparse(full_url)
        defragmented_url = urlunparse(parsed._replace(fragment=""))

        # checks if defragmented URL is valid
        if is_valid(defragmented_url):
            found_links.add(defragmented_url)
        
    return list(found_links)


def check_page_length(length: int, url: str):
    # Checks and updates longest page
    if length > longest_page["length"]:
        longest_page["url"] = url
        longest_page["length"] = length


def increment_subdomain_count(current_url: str,
                              current_subdomains: dict[str: int]) -> dict[str: int]:
    parsed = urlparse(current_url)
    subdomain = parsed.netloc.lower()

    if subdomain in current_subdomains.keys():
        current_subdomains[subdomain] += 1
    else:
        current_subdomains[subdomain] = 1
    return current_subdomains

def update_report(unique_urls, longest_page, words, subdomain_counts):
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("Crawler Report\n")
        f.write(f"Total unique URLs: {len(unique_urls)}\n")
        f.write(f"Longest page: {longest_page['url']} : {longest_page['length']} Words\n")
        f.write("\nCommon Words:\n")
        for word, count in words[:COMMON_WORDS_COUNT]:
            f.write(f"{word} {count}\n")
        f.write("\nSubdomain Counts:\n")
        for subdomain, count in subdomain_counts.items():
            f.write(f"{subdomain}, {count}\n")


def is_valid(url: str):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]) or is_crawler_trap(url, parsed):
            return False
        return not re.match(
            r".*\.(css|js|bmp|gif|jpe?g|ico"
            + r"|png|tiff?|mid|mp2|mp3|mp4"
            + r"|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf"
            + r"|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names"
            + r"|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso"
            + r"|epub|dll|cnf|tgz|sha1"
            + r"|thmx|mso|arff|rtf|jar|csv"
            + r"|rm|smil|wmv|swf|wma|zip|rar|gz)$", parsed.path.lower())

    except TypeError:
        print ("TypeError for ", parsed)
        raise


def is_crawler_trap(url: str, parsed_url) -> bool:
    for p in blacklist_path:
        # Checks for blacklisted path values
        if parsed_url.path.lower().startswith(p):
            return True

    # Checks for blacklisted urls
    return (parsed_url.hostname in blackList_host
            or url in blacklist_url)


def is_too_large(resp) -> bool:
    length = resp.raw_response.headers.get("Content-Length")
    if length is None:
        return False
    try:
        clean_length = re.sub(r"\D", "", str(length))
        if not clean_length:
            return False
        return int(clean_length) > MAX_PAGE_SIZE
    except (ValueError, TypeError):
        return False


def can_extract(resp) -> bool:
    if resp.status != 200:
        print(f"Failed to retrieve the webpage: {resp.error}. Status code: {resp.status}")
        return False

    if not resp.raw_response.content:
        print("No data found, skipping page.")
        return False

    if is_too_large(resp):
        print("Page too large, skipping.")
        return False
    
    return True