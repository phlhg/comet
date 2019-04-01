import json

d = b'"key": "value"'
s = "hello"
b = bytes(s, 'utf8')
s2 = str(b, 'utf8')

print(s2)
