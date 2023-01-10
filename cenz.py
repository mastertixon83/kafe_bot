import json

ar = []

with (open('cenz.txt', encoding='utf-8')) as r:
    for i in r:
        n = i.lower().split('\n')[0]
        if n != '':
            ar.append(n)
with (open('cenz.json', 'w')) as file:
    json.dump(ar, file, indent=4, ensure_ascii=False)
