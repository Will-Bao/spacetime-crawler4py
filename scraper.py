import re
from urllib.parse import urlparse, urljoin, urlunparse
from bs4 import BeautifulSoup

unique_urls = set()
longest_page = {"url": "", "length": -1}

def scraper(url, resp):
    links = extract_next_links(url, resp)
    return [link for link in links if is_valid(link)]

def extract_next_links(url, resp):
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

    page_text = soup.get_text(separator=" ", strip=True)
    check_page_length(page_text.split(), resp.url)

    links = get_links(soup, resp.url)

    print(f"Total unique urls: {len(unique_urls)}")
    print(f"Longest page: {longest_page['url']} - {longest_page['length']} Words")
    return links

def get_links(soup, url):
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

        if is_valid(defragmented_url):
            found_links.append(defragmented_url)
            unique_urls.add(defragmented_url)
        
    return found_links

def check_page_length(content, url):
    # Checks and updates longest page
    page_length = len(content)
    if page_length > longest_page["length"]:
        longest_page["url"] = url
        longest_page["length"] = page_length

def is_valid(url):
    # Decide whether to crawl this url or not. 
    # If you decide to crawl it, return True; otherwise return False.
    # There are already some conditions that return False.
    try:
        parsed = urlparse(url)
        if parsed.scheme not in set(["http", "https"]):
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
