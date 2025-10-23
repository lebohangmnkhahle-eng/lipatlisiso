# evaluate.py

import os
import pandas as pd
from sacrebleu import BLEU, CHRF
from Levenshtein import distance
from transformers import T5ForConditionalGeneration, AutoTokenizer

from baselines import identity_baseline
from rule_based_normalizer import SesothoNormalizer

def evaluate_model(model, test_data, model_type='function', tokenizer=None):
    """Evaluate model on test set"""
    predictions = []
    references = test_data['target'].tolist()

    for _, row in test_data.iterrows():
        source = row['source']
        if model_type == 'function':
            pred = model(source)
        elif model_type == 'normalizer':
            pred, _ = model.normalize(source)
        elif model_type == 'transformer':
            inputs = tokenizer(f"normalize: {source}", return_tensors="pt", max_length=256, truncation=True)
            outputs = model.generate(**inputs)
            pred = tokenizer.decode(outputs[0], skip_special_tokens=True)
        else:
            raise ValueError(f"Unknown model_type: {model_type}")
        predictions.append(pred)

    # BLEU
    bleu = BLEU()
    bleu_score = bleu.corpus_score(predictions, [references])

    # chrF
    chrf = CHRF()
    chrf_score = chrf.corpus_score(predictions, [references])

    # Edit distance
    edit_distances = [distance(p, r) for p, r in zip(predictions, references)]
    avg_edit_dist = sum(edit_distances) / len(edit_distances) if edit_distances else 0

    # Character error rate
    total_chars = sum(len(r) for r in references)
    cer = sum(edit_distances) / total_chars if total_chars > 0 else 0

    scores = {
        'bleu': bleu_score.score,
        'chrf': chrf_score.score,
        'avg_edit_distance': avg_edit_dist,
        'character_error_rate': cer * 100
    }
    return scores, predictions

if __name__ == '__main__':
    # Load test data
    test_df = pd.read_csv('data/splits/test.tsv', sep='\t')

    results = {}

    def save_predictions(predictions, filename):
        with open(os.path.join('results', filename), 'w') as f:
            for pred in predictions:
                f.write(pred + '\n')

    # Evaluate identity baseline
    results['identity'], identity_preds = evaluate_model(identity_baseline, test_df, model_type='function')
    save_predictions(identity_preds, 'identity_predictions.txt')

    # Evaluate rule-based normalizer
    normalizer = SesothoNormalizer()
    results['rule_based'], rule_based_preds = evaluate_model(normalizer, test_df, model_type='normalizer')
    save_predictions(rule_based_preds, 'rule_based_predictions.txt')

    # Evaluate ByT5 model
    # Note: This assumes training has produced a checkpoint.
    from huggingface_hub.errors import HFValidationError
    try:
        model_path = os.path.abspath('./checkpoints/byt5-small')
        byt5_model = T5ForConditionalGeneration.from_pretrained(model_path)
        byt5_tokenizer = AutoTokenizer.from_pretrained(model_path)
        results['byt5'], byt5_preds = evaluate_model(byt5_model, test_df, model_type='transformer', tokenizer=byt5_tokenizer)
        save_predictions(byt5_preds, 'byt5_predictions.txt')
    except (OSError, HFValidationError):
        print("ByT5 model not found or invalid. Skipping evaluation.")
        results['byt5'] = { 'bleu': 0, 'chrf': 0, 'avg_edit_distance': 'N/A', 'character_error_rate': 'N/A' }
        save_predictions([], 'byt5_predictions.txt') # Save empty file

    # Placeholder for LSTM
    results['lstm'] = { 'bleu': 0, 'chrf': 0, 'avg_edit_distance': 'N/A', 'character_error_rate': 'N/A' }
    save_predictions([], 'lstm_predictions.txt')


    # Print and save results
    results_df = pd.DataFrame(results).T
    print(results_df)

    os.makedirs('results', exist_ok=True)
    results_df.to_csv('results/automatic_evaluation.csv')
