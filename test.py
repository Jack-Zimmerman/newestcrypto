import requests
import urllib.parse
import json


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36',
}


print(requests.get("http://172.20.56.146:8282/test").text)