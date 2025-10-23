# analysis.py

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
import simpledorff
import os

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
    """Compare systems using Wilcoxon signed-rank test."""
    ratings_df['overall'] = ratings_df[['fluency', 'adequacy', 'preference']].mean(axis=1)

    byt5_scores = ratings_df[ratings_df['system']=='ByT5']['overall']
    rule_scores = ratings_df[ratings_df['system']=='Rule-based']['overall']

    # Ensure we have paired samples
    if len(byt5_scores) == len(rule_scores):
        statistic, p_value = stats.wilcoxon(byt5_scores, rule_scores)
        print("\nWilcoxon Signed-Rank Test:")
        print(f"Statistic: {statistic:.4f}, p-value: {p_value:.4f}")
        if p_value < 0.05:
            print("The difference between the systems is statistically significant.")
        else:
            print("The difference between the systems is not statistically significant.")

def plot_results(ratings_df):
    """Create and save plots of the results."""
    plt.figure(figsize=(12, 6))
    sns.boxplot(x='system', y='overall', data=ratings_df)
    plt.title('Overall Score Distribution by System')
    plt.savefig('results/system_comparison.png')
    print("\nSaved system comparison plot to results/system_comparison.png")

if __name__ == '__main__':
    # Generate dummy data for demonstration
    generate_dummy_data()

    # Load human evaluation results
    evaluator_files = [
        'results/human_eval_evaluator1.csv',
        'results/human_eval_evaluator2.csv',
    ]

    try:
        ratings = pd.concat([pd.read_csv(f) for f in evaluator_files])

        print("Inter-Annotator Agreement:")
        compute_iaa(ratings)

        compare_systems(ratings)

        plot_results(ratings)

    except FileNotFoundError:
        print("Evaluation files not found. Please ensure the human evaluation has been completed.")
