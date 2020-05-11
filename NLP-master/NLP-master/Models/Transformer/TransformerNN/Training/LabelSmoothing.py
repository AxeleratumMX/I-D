import torch
import torch.nn as nn
from torch.autograd import Variable


class LabelSmoothing(nn.Module):
    "Implement label smoothing."

    def __init__(self, size, padding_idx, smoothing=0.0):
        super(LabelSmoothing, self).__init__()
        self.criterion = nn.KLDivLoss(size_average=False)
        self.padding_idx = padding_idx
        self.confidence = 1.0 - smoothing
        self.smoothing = smoothing
        self.size = size
        self.true_dist = None

    def forward(self, x, target):
        assert x.size(1) == self.size
        true_dist = x.data.clone()
        true_dist.fill_(self.smoothing / (self.size - 2))
        true_dist.scatter_(1, target.data.unsqueeze(1).type(torch.LongTensor), self.confidence)
        true_dist[:, self.padding_idx] = 0
        mask = torch.nonzero(target.data == self.padding_idx)
        if mask.dim() > 0:
            true_dist.index_fill_(0, mask.squeeze(), 0.0)
        self.true_dist = true_dist
        return self.criterion(x, Variable(true_dist, requires_grad=False))




# from torch.autograd import Variable
# import matplotlib.pyplot as plt
# import seaborn
# seaborn.set_context(context="talk")
#
# # Example of label smoothing.
# crit = LabelSmoothing(5, 0, 0.4)
# predict = torch.FloatTensor([[0, 0.2, 0.7, 0.1, 0],
#                              [0, 0.2, 0.7, 0.1, 0],
#                              [0, 0.2, 0.7, 0.1, 0]])
# v = crit(Variable(predict.log()), Variable(torch.LongTensor([2, 1, 0])))
#
# # Show the target distributions expected by the system.
# plt.imshow(crit.true_dist)
# plt.show()




# import numpy as np
# from torch.autograd import Variable
# import matplotlib.pyplot as plt
# import seaborn
# #seaborn.set_context(context="talk")
#
# crit = LabelSmoothing(5, 0, 0.1)
# def loss(x):
#     d = x + 3 * 1
#     predict = torch.FloatTensor([[0, x / d, 1 / d, 1 / d, 1 / d],])
#     #print(predict)
#     return crit(Variable(predict.log()), Variable(torch.LongTensor([1])))#.data[0]
# plt.plot(np.arange(1, 100), [loss(x) for x in range(1, 100)])
# plt.show()
