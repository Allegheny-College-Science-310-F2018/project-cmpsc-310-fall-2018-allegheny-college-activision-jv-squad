import matplotlib.pyplot as plt

data = None
with open("state_changes.txt",'r') as f:
    data = f.readlines()

x = []
y = []
for d in data:
    s = d.split(",")
    x.append(s[0])
    y.append(s[1])

plt.plot(x, y, 'b-')
plt.show()
