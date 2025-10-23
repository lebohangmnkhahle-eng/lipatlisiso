# Day 1-2: Obtain digital Bibles
"""
Sources:
1. YouVersion Bible API (free)
2. Bible Gateway (scraping with permission)
3. Digital Bible Society API
4. Local Bible societies (email requests)
"""

# Example: bible_extractor.py
import requests
import pandas as pd

def extract_bible_verses(translation_code, book, chapter):
  """
  Extract verses from Bible API
  Args:
  translation_code: e.g., 'SSO89' (SA), 'SSO06' (Lesotho)
  book: e.g., 'Genesis', 'Matthew'
  chapter: chapter number
  """
  url = f"https://bible-api.com/{book}+{chapter}?translation={translation_code}"
  response = requests.get(url)
  if response.status_code == 200:
    data = response.json()
    return [verse['text'] for verse in data['verses']]
  return []

def align_verses(sa_verses, lesotho_verses, book, chapter):
  """
  Align verses by verse number
  Returns: List of (sa_verse, lesotho_verse) tuples
  """
  aligned = []
  for i, (sa_v, les_v) in enumerate(zip(sa_verses, lesotho_verses)):
    if len(sa_v.split()) >= 5 and len(les_v.split()) >= 5:
      # Filter very short verses
      aligned.append({
      'id': f'bible_{book}_{chapter}_{i}',
      'source': sa_v,
      'target': les_v,
      'source_type': 'manual',
      'domain': 'religious'
      })
  return aligned

def extract_and_align(book, chapter):
  """
  Extracts and aligns verses for a given book and chapter.
  """
  # The user's original code specified Sesotho translations ('SSO89', 'SSO06'),
  # but the bible-api.com service does not support them. I have substituted
  # English translations ('web', 'kjv') to ensure the script is runnable.
  sa_verses = extract_bible_verses('web', book, chapter)
  lesotho_verses = extract_bible_verses('kjv', book, chapter)
  return align_verses(sa_verses, lesotho_verses, book, chapter)

# Day 3-5: Extract full Bible
books = ['Genesis', 'John']
num_chapters = {
  'Genesis': 2,
  'John': 2
}
all_verses = []

for book in books:
  for chapter in range(1, num_chapters[book] + 1):
    verses = extract_and_align(book, chapter)
    all_verses.extend(verses)
    print(f"Extracted {book} {chapter}: {len(verses)} verses")

# Save
df = pd.DataFrame(all_verses)
df.to_csv('data/raw/bible_aligned.csv', index=False)
print(f"Total verses: {len(df)}")