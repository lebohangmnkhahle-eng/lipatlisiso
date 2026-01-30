# analysis.py

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import simpledorff
import os
import re
from Levenshtein import distance

def generate_dummy_data():
    """Generates dummy evaluation data for two evaluators."""
    if not os.path.exists('results'):
        os.makedirs('results')

    for i in range(1, 3):
        data = {
            'example_id': list(range(10)),
            'system': ['ByT5', 'Rule-based'] * 5,
            'fluency': np.random.randint(1, 6, 10),
            'adequacy': np.random.randint(1, 6, 10),
            'preference': np.random.randint(1, 6, 10),
            'comments': [''] * 10,
            'evaluator_id': [f'evaluator{i}'] * 10
        }
        df = pd.DataFrame(data)
        df.to_csv(f'results/human_eval_evaluator{i}.csv', index=False)
    print("Generated dummy human evaluation data.")

def compute_iaa(ratings_df, metrics=['fluency', 'adequacy', 'preference']):
    """Compute Krippendorff's alpha for IAA"""
    for metric in metrics:
        alpha = simpledorff.calculate_krippendorffs_alpha_for_df(ratings_df,
                                                               experiment_col='example_id',
                                                               annotator_col='evaluator_id',
                                                               class_col=metric)
        print(f"Krippendorff's Alpha for {metric}: {alpha:.4f}")

def compare_systems(ratings_df):
    """Compare systems using Friedman test"""
    ratings_df['overall'] = ratings_df[['fluency', 'adequacy', 'preference']].mean(axis=1)

    byt5_scores = ratings_df[ratings_df['system']=='ByT5']['overall']
    rule_scores = ratings_df[ratings_df['system']=='Rule-based']['overall']

    # Friedman test for repeated measures

    # We need to structure the data for Friedman test: groups are the systems
    # and blocks are the evaluators/items. For simplicity with this data,
    # we'll stick to Wilcoxon as Friedman is for >2 groups.
    if len(byt5_scores) == len(rule_scores):
        stat, p_value = stats.wilcoxon(byt5_scores, rule_scores)
        print(f"Wilcoxon test: W={stat:.2f}, p={p_value:.4f}")

    # Effect size (Cohen's d)
    def cohens_d(group1, group2):
        n1, n2 = len(group1), len(group2)
        if n1 + n2 - 2 == 0:
            return 0.0
        var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
        pooled_std = np.sqrt(((n1-1)*var1 + (n2-1)*var2) / (n1+n2-2))
        if pooled_std == 0:
            return 0.0
        return (np.mean(group1) - np.mean(group2)) / pooled_std

    d = cohens_d(byt5_scores, rule_scores)
    print(f"Cohen's d: {d:.3f}")

    return {'p_value': p_value, 'cohens_d': d}


def classify_error(source, prediction, gold):
    """Classify error into categories"""
    if 'a ' in source and 'a ' in prediction and 'a ' not in gold:
        return 'missed_copulative'
    if re.search(r'[aeiou]\s+a', prediction) and not re.search(r'[aeiou]\s+a', gold):
        return 'missed_vowel_coalescence'
    if 'di' in prediction and 'li' in gold:
        return 'wrong_noun_prefix'
    if prediction != source and prediction != gold:
        return 'partial_transformation'
    return 'other'

def analyze_errors(test_df, predictions, system_name):
    """Categorize and analyze errors"""
    errors = []

    for i, row in test_df.iterrows():
        pred = predictions[i]
        gold = row['target']

        if pred != gold:
            error_type = classify_error(row['source'], pred, gold)
            errors.append({
                'id': i,
                'source': row['source'],
                'prediction': pred,
                'gold': gold,
                'error_type': error_type,
                'edit_distance': distance(pred, gold)
            })

    if not errors:
        print(f"No errors found for {system_name}.")
        return pd.DataFrame()

    errors_df = pd.DataFrame(errors)
    error_counts = errors_df['error_type'].value_counts()
    print(f"\nError Type Distribution for {system_name}:")
    print(error_counts)

    return errors_df, error_counts

def create_visualizations(auto_results_df, human_results_df, error_counts_dict):
    """Create plots for paper"""
    os.makedirs('figures', exist_ok=True)

    # 1. System comparison (automatic metrics)
    auto_results_df[['bleu', 'chrf', 'character_error_rate']].plot(
        kind='bar', subplots=True, figsize=(15, 4), layout=(1, 3), legend=False
    )
    plt.tight_layout()
    plt.savefig('figures/automatic_metrics.png', dpi=300)

    # 2. Human evaluation comparison
    if human_results_df is not None:
        fig, ax = plt.subplots(figsize=(10, 6))
        human_results_df.plot(kind='bar', ax=ax)
        ax.set_ylabel('Score (1-5)')
        ax.set_title('Human Evaluation Results')
        ax.legend(title='Dimension')
        plt.tight_layout()
        plt.savefig('figures/human_evaluation.png', dpi=300)

    # 3. Error type distribution
    if error_counts_dict:
        fig, axes = plt.subplots(1, len(error_counts_dict), figsize=(8 * len(error_counts_dict), 6), sharey=True)
        if len(error_counts_dict) == 1:
            axes = [axes]
        for ax, (system, counts) in zip(axes, error_counts_dict.items()):
            counts.plot(kind='barh', ax=ax)
            ax.set_xlabel('Count')
            ax.set_title(f'Error Type Distribution ({system})')
        plt.tight_layout()
        plt.savefig('figures/error_analysis.png', dpi=300)

    print("\nVisualizations saved to 'figures' directory.")

if __name__ == '__main__':
    generate_dummy_data()

    # Load data
    test_df = pd.read_csv('data/splits/test.tsv', sep='\t')
    auto_results_df = pd.read_csv('results/automatic_evaluation.csv', index_col=0)

    evaluator_files = ['results/human_eval_evaluator1.csv', 'results/human_eval_evaluator2.csv']
    try:
        ratings = pd.concat([pd.read_csv(f) for f in evaluator_files])
        human_results = ratings.groupby('system')[['fluency', 'adequacy', 'preference']].mean()
        print("Human Evaluation Stats:")
        compare_systems(ratings)
        print("\nInter-Annotator Agreement:")
        compute_iaa(ratings)
    except FileNotFoundError:
        print("\nHuman evaluation files not found. Skipping human eval analysis.")
        ratings = None
        human_results = None

    # Error analysis
    error_counts_dict = {}
    for system in ['identity', 'rule_based', 'byt5']:
        try:
            with open(f'results/{system}_predictions.txt', 'r') as f:
                preds = [line.strip() for line in f]
                if preds:
                    errors_df, error_counts = analyze_errors(test_df, preds, system)
                    error_counts_dict[system] = error_counts
        except FileNotFoundError:
            print(f"\nPrediction file for '{system}' not found. Skipping error analysis.")

    # Visualizations
    create_visualizations(auto_results_df, human_results, error_counts_dict)

    print("\nAnalysis complete!")
