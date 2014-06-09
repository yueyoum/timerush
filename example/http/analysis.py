import sys
from collections import Counter

name = sys.argv[1]

with open(name, 'r') as f:
    lines = f.readlines()

amount = len(lines)
print "amount =", amount

values = []
for line in lines:
    line.rstrip('\n')
    a, b = line.split('=')
    values.append(int(b))

c = Counter(values)
result = c.items()
result.sort(key=lambda item: item[0])
print result

for a, b in result:
    print a, b, b / float(amount)





