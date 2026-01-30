# train_lstm.py

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import pandas as pd
from collections import Counter
from baselines import LSTMSeq2Seq

# --- Data Loading and Preprocessing ---

class SesothoDataset(Dataset):
    def __init__(self, data, vocab):
        self.data = data
        self.vocab = vocab
        self.unk_token = '<unk>'

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        source = self.data.iloc[idx]['source']
        target = self.data.iloc[idx]['target']
        source_indices = [self.vocab.get(token, self.vocab[self.unk_token]) for token in source.split()]
        target_indices = [self.vocab.get(token, self.vocab[self.unk_token]) for token in target.split()]
        return torch.tensor(source_indices), torch.tensor(target_indices)

def build_vocab(texts, min_freq=2):
    word_counts = Counter()
    for text in texts:
        word_counts.update(text.split())

    vocab = {'<pad>': 0, '<sos>': 1, '<eos>': 2, '<unk>': 3}
    for word, count in word_counts.items():
        if count >= min_freq:
            vocab[word] = len(vocab)
    return vocab

def collate_fn(batch):
    sources, targets = zip(*batch)
    padded_sources = nn.utils.rnn.pad_sequence(sources, batch_first=True, padding_value=0)
    padded_targets = nn.utils.rnn.pad_sequence(targets, batch_first=True, padding_value=0)
    return padded_sources, padded_targets

# --- Training Loop ---

def train_lstm_model():
    # Load data
    train_df = pd.read_csv('data/splits/train.tsv', sep='\t')
    val_df = pd.read_csv('data/splits/val.tsv', sep='\t')

    # Build vocab
    all_texts = list(train_df['source']) + list(train_df['target'])
    vocab = build_vocab(all_texts)
    vocab_size = len(vocab)

    # Create datasets and dataloaders
    train_dataset = SesothoDataset(train_df, vocab)
    val_dataset = SesothoDataset(val_df, vocab)
    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, collate_fn=collate_fn)
    DataLoader(val_dataset, batch_size=32, collate_fn=collate_fn)

    # Initialize model
    model = LSTMSeq2Seq(vocab_size)
    optimizer = optim.Adam(model.parameters())
    criterion = nn.CrossEntropyLoss(ignore_index=0) # Ignore padding

    # --- Simplified Training Loop ---
    # This is a basic loop and would need more features for a production model
    # (e.g., learning rate scheduling, early stopping, proper evaluation)

    model.train()
    for epoch in range(3): # A few epochs for demonstration
        for i, (source, target) in enumerate(train_loader):
            optimizer.zero_grad()

            # The target for the decoder input needs a <sos> token
            # The target for the loss function is the original target
            decoder_input = target[:, :-1]
            decoder_output_target = target[:, 1:]

            output = model(source, decoder_input)

            # Reshape for loss function
            output = output.contiguous().view(-1, output.shape[-1])
            target = decoder_output_target.contiguous().view(-1)

            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            if i % 1 == 0:
                print(f"Epoch: {epoch+1}, Batch: {i+1}/{len(train_loader)}, Loss: {loss.item():.4f}")

    # Save the model (optional)
    # torch.save(model.state_dict(), 'models/lstm_baseline.pt')

if __name__ == '__main__':
    train_lstm_model()
