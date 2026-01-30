# generate_synthetic.py

from rules import SesothoRuleBasedNormalizer
import pandas as pd
from collections import Counter

# Load normalizer
normalizer = SesothoRuleBasedNormalizer()

# Load SA sentences
with open('data/raw/sa_sentences_manual.txt', 'r', encoding='utf-8') as f:
    sa_sentences = [line.strip() for line in f if line.strip()]

# Generate synthetic pairs
synthetic_pairs = []

for i, sa_sent in enumerate(sa_sentences):
    # Normalize
    les_sent, log = normalizer.normalize(sa_sent)

    # Only keep if something changed
    if les_sent != sa_sent:
        synthetic_pairs.append({
            'id': f'synth_{i:04d}',
            'source': sa_sent,
            'target': les_sent,
            'source_type': 'synthetic',
            'rules_applied': ','.join([log_entry['rule'] for log_entry in log]),
            'num_transformations': len(log)
        })

# Create DataFrame
df_synthetic = pd.DataFrame(synthetic_pairs)

print(f"Generated {len(df_synthetic)} synthetic pairs")
print("\nTransformation distribution:")
print(df_synthetic['num_transformations'].value_counts())

print("\nRule frequency:")
all_rules = ','.join(df_synthetic['rules_applied']).split(',')
rule_counts = Counter(all_rules)
for rule, count in rule_counts.most_common():
    print(f"  {rule}: {count}")

# Save
df_synthetic.to_csv('data/raw/synthetic_pairs.csv', index=False)

print("\n✅ Synthetic pairs saved to: data/raw/synthetic_pairs.csv")

# Show samples
print("\nSample pairs:")
for i in range(min(5, len(df_synthetic))):
    row = df_synthetic.iloc[i]
    print(f"\n{i+1}. SA:  {row['source']}")
    print(f"   Les: {row['target']}")
    print(f"   Rules: {row['rules_applied']}")
