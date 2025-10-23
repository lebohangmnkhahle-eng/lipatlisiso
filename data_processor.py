# data_processor.py

import pandas as pd
from collections import Counter

def load_all_data():
    """Combine all data sources"""
    # Bible data is excluded for now as the current API only provides English text.
    # A new data source is needed for Sesotho bible verses.
    df_bible = pd.DataFrame(columns=['id', 'source', 'target', 'source_type', 'domain'])

    # Synthetic
    df_synthetic = pd.read_csv('data/raw/synthetic_pairs.csv')

    # Web (if available)
    try:
        df_web = pd.read_csv('data/raw/web_crawled.csv')
    except:
        df_web = pd.DataFrame()

    # Combine
    df_all = pd.concat([df_bible, df_synthetic, df_web], ignore_index=True)

    return df_all

def compute_statistics(df):
    """Compute dataset statistics"""
    stats = {
        'total_pairs': len(df),
        'sources': df['source_type'].value_counts().to_dict(),
        'avg_length_source': df['source'].str.len().mean(),
        'avg_length_target': df['target'].str.len().mean(),
        'avg_words_source': df['source'].str.split().str.len().mean(),
        'avg_words_target': df['target'].str.split().str.len().mean(),
    }

    # Edit distance
    from Levenshtein import distance
    df['edit_distance'] = df.apply(
        lambda row: distance(row['source'], row['target']), axis=1
    )
    stats['avg_edit_distance'] = df['edit_distance'].mean()

    return stats

def create_splits(df, train_ratio=0.8, val_ratio=0.1):
    """Create train/val/test splits"""
    from sklearn.model_selection import train_test_split

    # Stratify by source type if possible
    train_val, test = train_test_split(
        df, test_size=(1-train_ratio-val_ratio),
        random_state=42, stratify=df['source_type']
    )

    train, val = train_test_split(
        train_val, test_size=val_ratio/(train_ratio+val_ratio),
        random_state=42, stratify=train_val['source_type']
    )

    return train, val, test

# Execute
df = load_all_data()
print(f"Total pairs collected: {len(df)}")

stats = compute_statistics(df)
print("\nDataset Statistics:")
for key, value in stats.items():
    print(f"  {key}: {value}")

# Create splits
train, val, test = create_splits(df)
train.to_csv('data/splits/train.tsv', sep='\t', index=False)
val.to_csv('data/splits/val.tsv', sep='\t', index=False)
test.to_csv('data/splits/test.tsv', sep='\t', index=False)

print(f"\nSplits:")
print(f"  Train: {len(train)}")
print(f"  Val: {len(val)}")
print(f"  Test: {len(test)}")
