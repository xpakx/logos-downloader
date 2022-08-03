from base64 import encode
from typing import Union
import requests
import json
import time
import argparse

from requests import Response

headers: dict[str,str] = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding' : 'gzip, deflate, br',
    'Accept-language' : 'en-GB,en;q=0.5',
    'Connection' : 'keep-alive',
    'Cookie' : '',
    'DNT' : '1',
    'Host' : 'app.logos.com',
    'Upgrade-Insecure-Requests' : '1',
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0'
}

json_headers: dict[str,str] = {
    'Accept' : 'application/json',
    'Accept-Encoding' : 'gzip, deflate, br',
    'Accept-Language' : 'en-GB,en;q=0.5',
    'Connection' : 'keep-alive',
    'Cookie' : '',
    'Content-Length' : '106',
    'content-type' : 'application/json',
    'Host' : 'app.logos.com',
    'Origin' : 'https://app.logos.com',
    'Referer' : 'https://app.logos.com',
    'Sec-Fetch-Dest' : 'empty',
    'Sec-Fetch-Mode' : 'cors',
    'Sec-Fetch-Site' : 'same-origin',
    'TE' : "trailers",
    'x-requested-with' : 'fetch',
    'User-Agent' : 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0'
}

def download_books_list(offset: Union[int, None] = None) -> None:
    url = 'https://app.logos.com/api/app/library/facetedResults'
    request = {
        'facetFilterQuery' : "",
        'getStoreResults' : False,
        'includeUnlicensed' : False,
        'offset' : offset,
        'query' : "",
        'selectedFacets' : [],
        'sortField' : "title",
        'userLanguage' : "en-GB"
    }
    response: Response = requests.post(url, json=request, headers=json_headers)
    data = json.loads(response.text)
    print(data)

def load_cookie_from_file(filename: str) -> None:
    with open(filename, 'r', encoding='latin-1') as myfile:
        file = myfile.read()
        data = json.loads(file)
        json_headers['Cookie'] = data['cookie']
        headers['Cookie'] = data['cookie']


load_cookie_from_file('login-data.json')
print(headers['Cookie'])
download_books_list()
