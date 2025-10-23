# combine_data.py

import pandas as pd

# Load Bible pairs
df_bible = pd.read_csv('data/raw/bible_pairs.csv').reset_index(drop=True)
df_bible['id'] = 'bible_' + df_bible.index.astype(str)
df_bible['source_type'] = 'manual'
df_bible = df_bible[['id', 'sa_text', 'lesotho_text', 'source_type']]
df_bible.columns = ['id', 'source', 'target', 'source_type']

# Load synthetic pairs
df_synthetic = pd.read_csv('data/raw/synthetic_pairs.csv').reset_index(drop=True)
df_synthetic = df_synthetic[['id', 'source', 'target', 'source_type']]

# Combine
df_all = pd.concat([df_bible, df_synthetic], ignore_index=True)

print(f"Total pairs: {len(df_all)}")
print(f"  Bible: {len(df_bible)}")
print(f"  Synthetic: {len(df_synthetic)}")

# Create simple train/test split
from sklearn.model_selection import train_test_split

train, test = train_test_split(df_all, test_size=0.2, random_state=42)

print(f"\nSplit:")
print(f"  Train: {len(train)}")
print(f"  Test: {len(test)}")

# Save
train.to_csv('data/splits/train.tsv', sep='\t', index=False)
test.to_csv('data/splits/test.tsv', sep='\t', index=False)

print(f"\n✅ Data combined and split")