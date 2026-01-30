# baselines.py

import torch
import torch.nn as nn
from rule_based_normalizer import SesothoNormalizer

# 1. Identity Baseline (trivial)
def identity_baseline(source):
    return source

# 2. Rule-based (already implemented)
normalizer = SesothoNormalizer()

# 3. LSTM Baseline

class LSTMSeq2Seq(nn.Module):
    def __init__(self, vocab_size, embedding_dim=128, hidden_dim=256):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embedding_dim)
        self.encoder = nn.LSTM(embedding_dim, hidden_dim, num_layers=2,
                               bidirectional=True, batch_first=True)
        self.decoder = nn.LSTM(embedding_dim, hidden_dim*2, num_layers=2,
                               batch_first=True)
        self.fc = nn.Linear(hidden_dim*2, vocab_size)

    def forward(self, src, tgt):
        embedded = self.embedding(src)
        encoder_outputs, (hidden, cell) = self.encoder(embedded)

        # We need to rearrange the hidden state from the bidirectional encoder
        # to be compatible with the unidirectional decoder.
        # This is a common pattern for seq2seq models.
        hidden = torch.cat((hidden[0:1], hidden[1:2]), dim=2)
        cell = torch.cat((cell[0:1], cell[1:2]), dim=2)

        tgt_embedded = self.embedding(tgt)
        decoder_outputs, _ = self.decoder(tgt_embedded, (hidden, cell))

        return self.fc(decoder_outputs)

# A full training script for this model would require a separate implementation
# including vocabulary creation, data loading, a proper training loop,
# and evaluation metrics.
