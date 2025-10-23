# train_byt5.py

from transformers import T5ForConditionalGeneration, AutoTokenizer, DataCollatorForSeq2Seq
from transformers import Trainer, TrainingArguments
from datasets import load_dataset

# Load data
dataset = load_dataset('csv', data_files={
    'train': 'data/splits/train.tsv',
    'validation': 'data/splits/val.tsv',
    'test': 'data/splits/test.tsv'
}, delimiter='\t')

# Load model
model = T5ForConditionalGeneration.from_pretrained('google/byt5-small')
tokenizer = AutoTokenizer.from_pretrained('google/byt5-small')

# Preprocess
def preprocess(examples):
    inputs = [f"normalize: {src}" for src in examples['source']]
    targets = examples['target']

    model_inputs = tokenizer(inputs, max_length=256, truncation=True)
    labels = tokenizer(targets, max_length=256, truncation=True)

    model_inputs['labels'] = labels['input_ids']
    return model_inputs

tokenized_dataset = dataset.map(preprocess, batched=True)

# Data collator
data_collator = DataCollatorForSeq2Seq(tokenizer=tokenizer, model=model)

# Training arguments
training_args = TrainingArguments(
    output_dir='./checkpoints/byt5-small',
    eval_strategy='steps',
    eval_steps=50,
    save_steps=100,
    learning_rate=5e-4,
    per_device_train_batch_size=2,
    per_device_eval_batch_size=2,
    num_train_epochs=3,
    weight_decay=0.01,
    save_total_limit=3,
    load_best_model_at_end=True,
    metric_for_best_model='eval_loss',
)

# Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=tokenized_dataset['train'],
    eval_dataset=tokenized_dataset['validation'],
    tokenizer=tokenizer,
    data_collator=data_collator,
)

# Train
trainer.train()

# Save
trainer.save_model('./models/byt5-small-sesofix')
