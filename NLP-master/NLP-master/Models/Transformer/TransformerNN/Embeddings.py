import torch.nn as nn
import math
import torch


class Embeddings(nn.Module):
    def __init__(self, d_model, vocab):
        super(Embeddings, self).__init__()
        self.lut = nn.Embedding(vocab, d_model)
        self.d_model = d_model

    def forward(self, x):
        x = x.type(torch.LongTensor)
        return self.lut(x) * math.sqrt(self.d_model)