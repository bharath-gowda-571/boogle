import re

def count_words(s):
    return len(re.findall(r'\w+',s))