import torch

x = torch.ones(2, 2, requires_grad=True)
y = x + 2
z = y * y * 3
out = z.mean()
y.register_hook(print)

out.backward()

print(x.grad)
print(y.grad)

