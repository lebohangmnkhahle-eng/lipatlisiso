# run_baseline_evaluation.py

import pandas as pd
from evaluation import Evaluator
from rules import SesothoRuleBasedNormalizer
from Levenshtein import distance

# Load test data
test_df = pd.read_csv('data/splits/test.tsv', sep='\t', dtype=str).fillna('')

print(f"Loaded {len(test_df)} test examples")

# Initialize evaluator
evaluator = Evaluator()

# ===== BASELINE 1: Identity (no transformation) =====
identity_predictions = test_df['source'].tolist()
references = test_df['target'].tolist()

identity_results = evaluator.evaluate(identity_predictions, references)
evaluator.print_results(identity_results, "Identity Baseline (No Normalization)")

# ===== BASELINE 2: Rule-Based =====
normalizer = SesothoRuleBasedNormalizer()

rule_based_predictions = []
for source in test_df['source']:
    normalized, _ = normalizer.normalize(source)
    rule_based_predictions.append(normalized)

rule_based_results = evaluator.evaluate(rule_based_predictions, references)
evaluator.print_results(rule_based_results, "Rule-Based Normalizer (5 rules)")

# ===== Comparison =====
print("IMPROVEMENT SUMMARY")
print("="*60)
print(f"BLEU improvement:  {rule_based_results['bleu'] - identity_results['bleu']:+.2f}")
print(f"CER improvement:   {identity_results['cer'] - rule_based_results['cer']:+.2f}%")
print(f"WER improvement:   {identity_results['wer'] - rule_based_results['wer']:+.2f}%")
print("="*60)

# ===== Error Analysis =====
print("\nERROR ANALYSIS (Rule-Based System)")
print("="*60)

errors = []
for i, (source, pred, ref) in enumerate(zip(test_df['source'], rule_based_predictions, references)):
    if pred != ref:
        errors.append({
            'id': i,
            'source': source,
            'prediction': pred,
            'reference': ref,
            'edit_dist': distance(pred, ref)
        })

print(f"Total errors: {len(errors)} / {len(test_df)} ({len(errors)/len(test_df)*100:.1f}%)")

if errors:
    print(f"\nSample errors (first 5):")
    for i, error in enumerate(errors[:5], 1):
        print(f"\n{i}. Source: {error['source']}")
        print(f"   Predicted: {error['prediction']}")
        print(f"   Reference: {error['reference']}")
        print(f"   Edit distance: {error['edit_dist']}")

# Save results
results_df = pd.DataFrame([
    {'system': 'Identity', **identity_results},
    {'system': 'Rule-Based (5 rules)', **rule_based_results}
])
results_df.to_csv('results/baseline_evaluation.csv', index=False)

print(f"\n✅ Results saved to: results/baseline_evaluation.csv")