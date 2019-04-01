import json

d = {"key": "value"}
s = str(d)
print(s)
b = bytes(d, 'utf8')
s2 = str(b)

print(s2)
