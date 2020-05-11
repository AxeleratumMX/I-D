import torch
import torch.nn as nn
from Net import Net

net = Net()

input = torch.rand(1, 1, 32, 32)
output = net(input)
target = torch.randn(10)
#target = target.view(1, -1)
criterion = nn.MSELoss()

loss = criterion(output, target)
print(loss)

net.zero_grad()
output.backward(torch.randn(1, 10))

learning_rate = 0.01
for f in net.parameters():
    f.data.sub_(f.grad.data * learning_rate)



import torch.optim as optim

# create your optimizer
optimizer = optim.SGD(net.parameters(), lr=0.01)

# in your training loop:
optimizer.zero_grad()   # zero the gradient buffers
output = net(input)
loss = criterion(output, target)
loss.backward()
optimizer.step()    # Does the update