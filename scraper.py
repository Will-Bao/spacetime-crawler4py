import re
from urllib.parse import urlparse, urljoin, urlunparse
from bs4 import BeautifulSoup
from tokenizer import tokenize, compute_word_frequencies

MAX_VISIT = 4

blackList_host = {"swiki.ics.uci.edu", "calendar.ics.uci.edu"}
blacklist_url = set()
unique_urls = dict() # dictionary of keys: url and value: visit_counter
longest_page = {"url": "", "length": -1}
common_words = dict()
report_file = "report.txt"


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

    if (resp.status != 200):
        print(f"Failed to retrieve the webpage. Status code: {resp.status}")
        return list()

    soup = BeautifulSoup(resp.raw_response.content, "html.parser")

    tokenized_text = []
    for currentText in soup.stripped_strings:
        # Gets the current text from a generator that contains the content of the webpage
        tokenized_text.extend(tokenize(currentText))

    word_freq = compute_word_frequencies(tokenized_text)
    check_page_length(len(tokenized_text), resp.url)

    links = get_links(soup, resp.url)

    update_report(unique_urls, longest_page, common_words)
    print(f"Total unique urls: {len(unique_urls)}")
    print(f"Longest page: {longest_page['url']} - {longest_page['length']} Words")
    return links


def get_links(soup: BeautifulSoup, url: str):
    # Retrieves the links on the web page.
    found_links = list()
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
            found_links.append(defragmented_url)

            if defragmented_url not in unique_urls.keys():
                unique_urls.update(defragmented_url, 1)
            else:
                unique_urls[defragmented_url] += 1
                if unique_urls[defragmented_url] <= MAX_VISIT:
                    blacklist_url.add(defragmented_url)
        
    return found_links


def check_page_length(length: int, url: str):
    # Checks and updates longest page
    if length > longest_page["length"]:
        longest_page["url"] = url
        longest_page["length"] = length

def update_report(unique_urls, longest_page):
    with open(report_file, "w", encoding="utf-8") as f:
        f.write("Crawler Report\n")
        f.write(f"Total unique URLs: {len(unique_urls)}\n")
        f.write(f"Longest page: {longest_page['url']} - {longest_page['length']} Words\n")

def is_valid(url: str):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]) or is_crawler_trap(url, parsed.hostname):
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


def is_crawler_trap(url: str, hostname: str):
    return hostname in blackList_host or url in blacklist_url