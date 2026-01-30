# evaluation.py

import pandas as pd
from Levenshtein import distance
from typing import List, Dict

class Evaluator:
    """Simple evaluation suite for orthographic normalization"""

    def __init__(self):
        pass

    def bleu_score_simple(self, predictions: List[str], references: List[str]) -> float:
        """
        Simplified BLEU (unigram precision with brevity penalty)
        For full BLEU, use sacrebleu library
        """
        total_precision = 0

        for pred, ref in zip(predictions, references):
            pred_words = pred.split()
            ref_words = ref.split()

            # Unigram precision
            matches = sum(1 for w in pred_words if w in ref_words)
            precision = matches / len(pred_words) if pred_words else 0

            # Brevity penalty
            bp = min(1.0, len(pred_words) / len(ref_words)) if ref_words else 0

            total_precision += precision * bp

        return (total_precision / len(predictions)) * 100 if predictions else 0

    def character_error_rate(self, predictions: List[str], references: List[str]) -> float:
        """Calculate character-level error rate"""
        total_distance = 0
        total_chars = 0

        for pred, ref in zip(predictions, references):
            total_distance += distance(pred, ref)
            total_chars += len(ref)

        return (total_distance / total_chars) * 100 if total_chars else 0

    def word_error_rate(self, predictions: List[str], references: List[str]) -> float:
        """Calculate word-level error rate"""
        total_errors = 0
        total_words = 0

        for pred, ref in zip(predictions, references):
            pred_words = pred.split()
            ref_words = ref.split()

            # Simple word-level distance
            errors = sum(1 for i in range(max(len(pred_words), len(ref_words)))
                        if i >= len(pred_words) or i >= len(ref_words) or
                        pred_words[i] != ref_words[i])

            total_errors += errors
            total_words += len(ref_words)

        return (total_errors / total_words) * 100 if total_words else 0

    def evaluate(self, predictions: List[str], references: List[str]) -> Dict[str, float]:
        """Run full evaluation suite"""

        results = {
            'bleu': self.bleu_score_simple(predictions, references),
            'cer': self.character_error_rate(predictions, references),
            'wer': self.word_error_rate(predictions, references),
            'num_examples': len(predictions)
        }

        # Calculate average edit distance
        edit_distances = [distance(p, r) for p, r in zip(predictions, references)]
        results['avg_edit_distance'] = sum(edit_distances) / len(edit_distances)

        # Exact match accuracy
        exact_matches = sum(1 for p, r in zip(predictions, references) if p == r)
        results['exact_match'] = (exact_matches / len(predictions)) * 100

        return results

    def print_results(self, results: Dict[str, float], system_name: str):
        """Pretty print results"""
        print(f"\n{'='*60}")
        print(f"EVALUATION RESULTS: {system_name}")
        print(f"{'='*60}")
        print(f"Number of examples: {results['num_examples']}")
        print(f"BLEU score:         {results['bleu']:.2f}")
        print(f"Character Error Rate: {results['cer']:.2f}%")
        print(f"Word Error Rate:    {results['wer']:.2f}%")
        print(f"Avg Edit Distance:  {results['avg_edit_distance']:.2f}")
        print(f"Exact Match Acc:    {results['exact_match']:.2f}%")
        print(f"{'='*60}\n")

if __name__ == '__main__':
    from rules import SesothoRuleBasedNormalizer

    # Load test data
    try:
        test_df = pd.read_csv('data/splits/test.tsv', sep='\t', dtype=str).fillna('')
    except FileNotFoundError:
        print("Test data not found. Please run `combine_data.py` first.")
        exit()

    # Initialize models
    evaluator = Evaluator()
    normalizer = SesothoRuleBasedNormalizer()

    # Generate predictions
    predictions = [normalizer.normalize(sent)[0] for sent in test_df['source']]
    references = test_df['target'].tolist()

    # Run evaluation
    rule_based_results = evaluator.evaluate(predictions, references)

    # Print results
    evaluator.print_results(rule_based_results, "Rule-based System")