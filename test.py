import codecs
te = ""
with codecs.open('filename.txt', 'w', encoding='utf-8-sig') as f:
    f.write('Hello, world!')