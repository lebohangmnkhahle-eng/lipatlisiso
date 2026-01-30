# human_evaluation.py

import os
import pandas as pd
from transformers import T5ForConditionalGeneration, AutoTokenizer
from rule_based_normalizer import SesothoNormalizer

def select_evaluation_samples(test_df, n=200):
    """Select stratified sample for human evaluation"""
    samples = []

    # Define strata
    short_df = test_df[test_df['source'].str.split().str.len() < 10]
    medium_df = test_df[
        (test_df['source'].str.split().str.len() >= 10) &
        (test_df['source'].str.split().str.len() <= 20)
    ]
    long_df = test_df[test_df['source'].str.split().str.len() > 20]

    # Sample from each stratum, handling cases where we have fewer samples than desired
    samples.append(short_df.sample(min(50, len(short_df))))
    samples.append(medium_df.sample(min(100, len(medium_df))))
    samples.append(long_df.sample(min(50, len(long_df))))

    return pd.concat(samples).sample(frac=1).reset_index(drop=True) # Shuffle

if __name__ == '__main__':
    # Load data and models
    test_df = pd.read_csv('data/splits/test.tsv', sep='\t')
    normalizer = SesothoNormalizer()

    from huggingface_hub.errors import HFValidationError
    try:
        model_path = os.path.abspath('./checkpoints/byt5-small')
        byt5_model = T5ForConditionalGeneration.from_pretrained(model_path)
        byt5_tokenizer = AutoTokenizer.from_pretrained(model_path)
        byt5_loaded = True
    except (OSError, HFValidationError):
        print("ByT5 model not found or invalid. Generating dummy predictions.")
        byt5_loaded = False

    # Select samples
    eval_samples = select_evaluation_samples(test_df)

    # Generate predictions
    eval_samples['pred_rule_based'] = eval_samples['source'].apply(
        lambda x: normalizer.normalize(x)[0]
    )

    if byt5_loaded:
        def predict_byt5(text):
            inputs = byt5_tokenizer(f"normalize: {text}", return_tensors="pt", max_length=256, truncation=True)
            outputs = byt5_model.generate(**inputs)
            return byt5_tokenizer.decode(outputs[0], skip_special_tokens=True)
        eval_samples['pred_byt5'] = eval_samples['source'].apply(predict_byt5)
    else:
        eval_samples['pred_byt5'] = "MODEL NOT LOADED"

    # Save to CSV
    eval_samples.to_csv('data/human_eval_samples.csv', index=False)
    print(f"Generated {len(eval_samples)} samples for human evaluation.")
