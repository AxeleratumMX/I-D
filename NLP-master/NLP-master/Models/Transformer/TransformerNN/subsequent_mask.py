import torch
import numpy as np
import matplotlib.pyplot as plt
import seaborn
seaborn.set_context(context="talk")

def subsequent_mask(size):
    "Mask out subsequent positions."
    attn_shape = (1, size, size)
    subsequent_mask = np.triu(np.ones(attn_shape), k=1).astype('uint8')
    return torch.from_numpy(subsequent_mask) == 0


# plt.figure(figsize=(5,5))
# plt.imshow(subsequent_mask(20))
# plt.show()