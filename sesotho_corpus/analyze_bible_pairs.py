# analyze_bible_pairs.py

import pandas as pd
from Levenshtein import distance
import re

df = pd.read_csv('data/raw/bible_pairs.csv', dtype=str).fillna('')

print(f"Total verse pairs collected: {len(df)}")
print("\nBooks covered:")
print(df['book'].value_counts())

# Analyze differences
df['edit_distance'] = df.apply(
    lambda row: distance(row['sa_text'], row['lesotho_text']),
    axis=1
)

print(f"\nAverage edit distance: {df['edit_distance'].mean():.2f}")
print(f"Min: {df['edit_distance'].min()}, Max: {df['edit_distance'].max()}")

# Identify common patterns
def find_copulative_differences(row):
    """Count copulative pattern differences"""
    sa_cops = len(re.findall(r'\b[KkOoRrLlBb]e?\s+a\s+', row['sa_text']))
    les_cops = len(re.findall(r'\b[KkOoRrLlBb][ea]a\s+', row['lesotho_text']))
    return sa_cops, les_cops

df['sa_copulatives'], df['les_copulatives'] = zip(*df.apply(find_copulative_differences, axis=1))

print(f"\nCopulative differences found in {(df['sa_copulatives'] > 0).sum()} verses")

# Save analysis
df.to_csv('data/processed/bible_pairs_analyzed.csv', index=False)

print("\n✅ Bible extraction complete!")
print("📁 Saved to: data/processed/bible_pairs_analyzed.csv")
