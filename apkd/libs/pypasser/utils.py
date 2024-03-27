import re

def parse_url(anchor_url: str) -> dict:
    regex = '(?P<endpoint>[api2|enterprise]+)\/anchor\?(?P<params>.*)'
    for match in re.finditer(regex, anchor_url):
        return match.groupdict()