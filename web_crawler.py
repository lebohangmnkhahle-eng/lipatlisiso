# web_crawler.py

import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
import pandas as pd
from difflib import SequenceMatcher

class BilingualCrawler:
    def __init__(self, seed_urls):
        self.seed_urls = seed_urls
        self.visited = set()
        self.sesotho_pages = []

    def is_sesotho(self, text):
        """
        Simple heuristic: check for Sesotho-specific words
        Better: use fastText language detection
        """
        sesotho_markers = ['ke', 'le', 'ba', 'ho', 'hore', 'tsa', 'ena']
        word_count = sum(1 for word in sesotho_markers if word in text.lower().split())
        return word_count >= 3

    def classify_orthography(self, text):
        """
        Classify as SA or Lesotho orthography
        Based on presence of characteristic patterns
        """
        # SA markers: "Ke a", "o a", spaced copulatives
        sa_score = len(re.findall(r'\b[KkOoRrLlBb]e?\s+a\s+', text))
        # Lesotho markers: "Kea", "oa", joined copulatives
        les_score = len(re.findall(r'\b[KkOoRrLlBb][ea]a\s+', text))

        if sa_score > les_score:
            return 'SA'
        elif les_score > sa_score:
            return 'Lesotho'
        else:
            return 'unknown'

    def crawl(self, max_pages=1000):
        """Crawl websites and collect Sesotho content"""
        queue = list(self.seed_urls)

        while queue and len(self.visited) < max_pages:
            url = queue.pop(0)
            if url in self.visited:
                continue

            try:
                response = requests.get(url, timeout=10)
                self.visited.add(url)

                soup = BeautifulSoup(response.content, 'html.parser')
                text = soup.get_text()

                if self.is_sesotho(text):
                    orthography = self.classify_orthography(text)
                    self.sesotho_pages.append({
                        'url': url,
                        'text': text,
                        'orthography': orthography
                    })

                # Find more links
                for link in soup.find_all('a', href=True):
                    new_url = urljoin(url, link['href'])
                    if new_url not in self.visited:
                        queue.append(new_url)

                time.sleep(1)  # Be polite

            except Exception as e:
                print(f"Error crawling {url}: {e}")
                continue

        return self.sesotho_pages

def load_seed_urls(filepath='bilingual_sites.txt'):
    urls = []
    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith('- www.'):
                # Extract just the URL part, handling potential comments
                url_part = line.strip().split(' ')[1]
                urls.append('https://' + url_part)
    return urls

def align_sentences(sa_sents, les_sents):
    """
    Align sentences from SA and Lesotho documents
    Using similarity matching
    """
    aligned = []

    for sa_sent in sa_sents:
        best_match = None
        best_score = 0

        for les_sent in les_sents:
            score = SequenceMatcher(None, sa_sent, les_sent).ratio()
            if score > best_score:
                best_score = score
                best_match = les_sent

        if best_score > 0.7:  # Threshold for alignment
            aligned.append((sa_sent, best_match, best_score))

    return aligned

if __name__ == '__main__':
    seed_urls = load_seed_urls()
    crawler = BilingualCrawler(seed_urls)
    sesotho_pages = crawler.crawl(max_pages=100) # Limit for testing

    df_web = pd.DataFrame(sesotho_pages)
    df_web.to_csv('data/raw/web_crawled.csv', index=False)

    print(f"Crawled {len(df_web)} Sesotho pages.")

    # Example of sentence alignment if we had separate SA and Lesotho docs
    # sa_texts = df_web[df_web['orthography'] == 'SA']['text'].tolist()
    # les_texts = df_web[df_web['orthography'] == 'Lesotho']['text'].tolist()
    # if sa_texts and les_texts:
    #     sa_sents = '. '.join(sa_texts).split('. ')
    #     les_sents = '. '.join(les_texts).split('. ')
    #     aligned_sentences = align_sentences(sa_sents, les_sents)
    #     print(f"Aligned {len(aligned_sentences)} sentences.")
