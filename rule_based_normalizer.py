# rule_based_normalizer.py

import re
from typing import List, Tuple

class SesothoNormalizer:
    def __init__(self):
        self.rules = self._initialize_rules()

    def _initialize_rules(self) -> List[Tuple]:
        """
        Define transformation rules
        Each rule: (name, pattern, replacement, exceptions)
        """
        rules = [
            # Copulative consolidation
            ('cop_ke_a', r'\bKe\s+a\s+', 'Kea ', []),
            ('cop_o_a', r'\bo\s+a\s+', 'oa ', []),
            ('cop_re_a', r'\bRe\s+a\s+', 'Rea ', []),
            ('cop_le_a', r'\bLe\s+a\s+', 'Lea ', []),
            ('cop_ba_a', r'\bBa\s+a\s+', 'Baa ', []),

            # Noun class prefixes (with exceptions)
            ('prefix_dijo', r'\bdijo\b', 'lijo', []),
            ('prefix_diphoofolo', r'\bdiphoofolo\b', 'liphoofolo', []),
            ('prefix_dibuka', r'\bdibuka\b', 'libuka', []),
            # Generic di -> li (careful with exceptions)
            ('prefix_di_generic', r'\bdi([a-z]+)\b',
             lambda m: f'li{m.group(1)}' if m.group(0) not in ['dipale', 'dimela', 'dinaha'] else m.group(0),
             []),

            # Consonant clusters
            ('cons_ngwana', r'\bngwana\b', 'ngoana', []),
            ('cons_ngwaneso', r'\bngwaneso\b', 'ngoaneso', []),

            # Possessives (context-dependent - simplified)
            ('poss_ya_hao', r'ya\s+hao\b', 'ea hao', []),
            ('poss_ya_rona', r'ya\s+rona\b', 'ea rona', []),
        ]
        return rules

    def normalize(self, text: str) -> str:
        """Apply all transformation rules"""
        normalized = text
        applied_rules = []

        for rule_name, pattern, replacement, exceptions in self.rules:
            # Check if text matches pattern
            if re.search(pattern, normalized):
                # Apply transformation
                new_text = re.sub(pattern, replacement, normalized)
                if new_text != normalized:
                    applied_rules.append(rule_name)
                    normalized = new_text

        return normalized, applied_rules

    def generate_synthetic_pairs(self, sa_sentences: List[str]) -> List[dict]:
        """Generate synthetic parallel corpus"""
        synthetic = []

        for i, sent in enumerate(sa_sentences):
            normalized, rules = self.normalize(sent)

            # Only keep if something changed
            if normalized != sent:
                synthetic.append({
                    'id': f'synth_{i:06d}',
                    'source': sent,
                    'target': normalized,
                    'source_type': 'synthetic',
                    'rules_applied': ','.join(rules),
                    'num_transformations': len(rules)
                })

        return synthetic

import pandas as pd
import random

def load_monolingual(filepath='data/raw/sa_monolingual.txt'):
    with open(filepath, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

if __name__ == '__main__':
    # Day 6: Generate and validate
    normalizer = SesothoNormalizer()
    sa_sentences = load_monolingual()
    synthetic_pairs = normalizer.generate_synthetic_pairs(sa_sentences)

    df_synthetic = pd.DataFrame(synthetic_pairs)

    # Manual validation of 200 samples if we have enough data
    if len(df_synthetic) > 200:
        sample = df_synthetic.sample(200)
    else:
        sample = df_synthetic

    # Mark as correct/incorrect
    # Calculate accuracy: expect 60-75%
    # For now, we will just save the sample for manual inspection
    sample.to_csv('data/raw/synthetic_pairs_sample_for_validation.csv', index=False)

    # Keep only high-confidence pairs (for now, all pairs)
    df_synthetic.to_csv('data/raw/synthetic_pairs.csv', index=False)

    print(f"Generated {len(df_synthetic)} synthetic pairs.")
    print("A sample for validation has been saved to data/raw/synthetic_pairs_sample_for_validation.csv")
