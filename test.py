import re

url_pattern = re.compile(r'(http|ftp|https)://([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:/~+#-]*[\w@?^=%&/~+#-])?')

def find_urls(string):
    return re.findall(url_pattern, string)


print(find_urls('https://www.youtube.com/watch?v=7NtjxiPiJxE'))

