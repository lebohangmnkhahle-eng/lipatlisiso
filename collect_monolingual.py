# collect_monolingual.py

import requests
from bs4 import BeautifulSoup

def collect_from_wikipedia():
    """Scrape SA Sesotho Wikipedia articles"""

    # Sample Sesotho Wikipedia pages
    pages = [
        'https://st.wikipedia.org/wiki/Afrika_Borwa',
        'https://st.wikipedia.org/wiki/Lesotho',
        'https://st.wikipedia.org/wiki/Sesotho',
    ]

    sentences = []

    for url in pages:
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract paragraphs
            paragraphs = soup.find_all('p')

            for p in paragraphs:
                text = p.get_text()
                # Split into sentences
                sents = text.split('.')
                sentences.extend([s.strip() + '.' for s in sents if len(s.strip()) > 20])

        except Exception as e:
            print(f"Error with {url}: {e}")

    return sentences

def manual_sentences():
    """Manually create simple SA Sesotho sentences"""
    return [
        "Ke a sebetsa ka letsatsi le leng le le leng.",
        "Ba a kena sekolong hosasa.",
        "O a tseba ho bua Sesotho hantle.",
        "Re a hloka thuso ya hao.",
        "Ngwana o a bapala ka ntle.",
        "Dijo di monate haholo kajeno.",
        "Le a tla ha rona hosane.",
        "Ba a rata ho bala dibuka.",
        "Ke a leboha ka thuso ya hao.",
        "O a kena tlung.",
        "Pula e a na ka ntle.",
        "Letsatsi le a tjhaba hoseng.",
        "Ke a ya toropong kajeno.",
        "O a dula hae.",
        "Bana ba a bapala serapeng.",
        "Katse e a robala setulong.",
        "Ntja e a bohola haholo.",
        "Ke a rata ho ja mahe.",
        "O a noa tee hoseng.",
        "Re a mamela mmino.",
        "Ba a shebella thelevishene.",
        "Ke a bala buka e monate.",
        "O a ngola lengolo.",
        "Le a pheha dijo tsa mantsiboya.",
        "Ke a hlatswa dijana.",
        "O a fiela ka tlung.",
        "Ba a lema meroho serapeng.",
        "Ke a utlwisisa seo o se buang.",
        "O a ithuta Sesotho sekolong.",
        "Re a tsamaya ka maoto.",
        "Ba a palama bese ho ya mosebetsing.",
        "Ke a ikutloa ke lapile.",
        "O a kula kajeno.",
        "Letsatsi le a dikela.",
        "Ngwedi o a kganya bosiu.",
        "Dinaledi di a benya lehodimong.",
        "Ke a batla ho robala.",
        "O a tsoha ka nako hoseng.",
        "Re a apara diaparo tse ntjha.",
        "Ba a bina kerekeng.",
        "Ke a rapela hoseng le mantsiboya.",
        "O a thusa batho ba hlokang.",
        "Le a haha ntlo e ntjha.",
        "Ke a bona nonyana sefateng.",
        "O a utlwa modumo o moholo.",
        "Re a ja dijo tse matlafatsang.",
        "Ba a tshameka bolo ya maoto.",
        "Ke a bitsa motswalle waka."
    ]

# Collect sentences
wiki_sentences = collect_from_wikipedia()
manual_sents = manual_sentences()

all_sentences = wiki_sentences + manual_sents

# Save
with open('data/raw/sa_sentences.txt', 'w', encoding='utf-8') as f:
    for sent in all_sentences[:100]:  # Take first 100
        f.write(sent + '\n')

print(f"✅ Collected {len(all_sentences)} SA Sesotho sentences")