import re

def cleanString(string):
    new_string = string
    new_string = new_string.strip()
    new_string = re.sub(r'(?:\s|&nbsp;|\x7F)+', ' ', new_string)
    new_string = re.sub(r'\s+,', ',', new_string)
    return new_string
