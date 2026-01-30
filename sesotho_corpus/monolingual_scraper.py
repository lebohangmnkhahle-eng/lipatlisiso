# Sources:
# 1. Wikipedia dumps (if available)
# 2. News websites (News24, SABC)
# 3. Government documents
# 4. Social media (with care for privacy)

import wikipediaapi
from newspaper import Article

def scrape_wikipedia():
    wiki = wikipediaapi.Wikipedia('st', headers={'User-Agent': 'MyCoolBot/0.0 (https://example.com/bot; my@email.com)'})  # Sesotho
    pages = ['Lesotho', 'Sesotho', 'Free_State', 'Thaba Nchu', 'Maseru', 'QwaQwa']
    texts = []
    for page_name in pages:
        page = wiki.page(page_name)
        if page.exists():
            texts.append(page.text)
    return texts

def scrape_news(urls):
    articles = []
    for url in urls:
        try:
            article = Article(url)
            article.download()
            article.parse()
            articles.append(article.text)
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    return articles

def collect_monolingual_corpus():
    wiki_texts = scrape_wikipedia()
    news_urls = [
        "https://www.news24.com/Sotho/",
    ]
    news_texts = scrape_news(news_urls)

    # Simple sentence splitting
    sa_sentences = []
    for text in wiki_texts + news_texts:
        sa_sentences.extend(text.split('. '))
    return sa_sentences

if __name__ == '__main__':
    # Collect 10,000+ SA Sesotho sentences
    sa_sentences = collect_monolingual_corpus()
    # Save
    with open('data/raw/sa_monolingual.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(sa_sentences))

    print(f"Collected {len(sa_sentences)} sentences.")
