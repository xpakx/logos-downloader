from typing import Union
import requests
import json
import time
import argparse

from requests import Response

headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding' : 'gzip, deflate, br',
    'Accept-language' : 'pl,en-US;q=0.7,en;q=0.3',
    'Connection' : 'keep-alive',
    'Cookie' : '',
    'DNT' : '1',
    'Host' : 'app.logos.com',
    'Upgrade-Insecure-Requests' : '1',
    'User-Agent' : 'Mozilla/5.0 (X11; Ubuntu, Linux x86_64; rv:75.0) Gecko/20100101 Firefox/75.o'
}
"""
request:
facetFilterQuery	""
getStoreResults	false
includeUnlicensed	false
offset	null // 50
query	""
selectedFacets	[]
sortField	"title"
userLanguage	"en-GB"


response 
XHRPOSThttps://app.logos.com/api/app/library/facetedResults
[HTTP/2 200 OK 502ms]

	
total	92
items	[ {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, {…}, … ]
facets	[ {…}, {…}, {…}, {…}, {…}, {…} ]
"""

def download_books_list(offset: Union[int, None] = None) -> None:
    url = 'https://app.logos.com/api/app/library/facetedResults'
    response: Response = requests.post(url, json="", headers=headers)
    data = json.loads(response.text)