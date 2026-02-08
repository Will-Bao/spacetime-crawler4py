import threading
import time
from urllib.parse import urlparse

class PolitnessDelay:
    def __init__(self, delay):
        self.delay = delay
        self.last_visit = {}
        self.lock = threading.Lock()

    def wait(self, url):
        domain = urlparse(url).netloc.lower()
        with self.lock:
            now = time.time()
            last_time = self.last_visit.get(domain, 0)
            delay_time = last_time + self.delay - now
            if delay_time > 0:
                time.sleep(delay_time)
            self.last_visit[domain] = time.time()