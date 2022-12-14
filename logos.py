from base64 import encode
from optparse import Option
from typing import List, Union
from typing import Optional
from urllib import response
import requests
import json
import time
import argparse
from io import BytesIO
from PIL import Image
from bs4 import BeautifulSoup
import os

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

def download_books_list(offset: Union[int, None] = None) -> List[dict[str,str]]:
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
    result: List[dict[str,str]] = []
    for book in data['items']: 
        result.append({
            'title' : book['title'],
            'id' : book['resourceId'],
            'coverUrl' : book['coverUrl']
        })
    return result

def load_cookie_from_file(filename: str) -> None:
    with open(filename, 'r', encoding='latin-1') as myfile:
        file = myfile.read()
        data = json.loads(file)
        json_headers['Cookie'] = data['cookie']
        headers['Cookie'] = data['cookie']

def get_first_article_id(book_id: str) -> Optional[str]:
    url = "https://app.logos.com/api/app/books/"+book_id
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    article_id: Optional[str]  = data['nextArticleId']
    return article_id

def get_book_by_id(book_id: str) -> str:
    content = ''
    list =  get_book_articles_by_id(book_id)
    for article in list:
        content += '\n\n' + article
    return content

def get_book_articles_by_id(book_id: str) -> List[str]:
    article_id: Optional[str] = get_first_article_id(book_id)
    content = []
    while(article_id != None):
        print(article_id)
        result = download_article_by_id(book_id, article_id if article_id else '')
        article, article_id = result['content'], result['next']
        content.append(article if article else '')
        time.sleep(0.05)
    return content

def download_article_by_id(book_id: str, article_id: str) -> dict[str,Optional[str]]:
    url = 'https://app.logos.com/api/app/books/'+book_id+'/articles/'+article_id
    print(url)
    response = requests.get(url, headers=headers)
    data = json.loads(response.text)
    if 'article' not in data:
        raise ValueError('No article')
    result: dict[str,Optional[str]] = {}
    if 'nextArticleId' not in data:
        result = {'content' : data['article']['content'], 'next': None}
    else:
        result = {'content' : data['article']['content'], 'next': data['nextArticleId']}
    return result

def download_images(book_text: str) -> str:
    soup = BeautifulSoup(book_text, 'html.parser')
    imgs = soup.findAll('img')
    i: int = 0
    directory = "img/"
    if not os.path.exists(directory):
        os.mkdir(directory)
    for img in imgs:
        i+=1
        print('{}/{}...'.format(i, len(imgs)))
        link: str = 'https://app.logos.com' + img['src']
        name: str = link.split("/")[-1]
        image = requests.get(link, headers=headers)
        image_file = Image.open(BytesIO(image.content))
        image_file.save(directory+name)
        img['src'] = directory + name
    return str(soup)

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--cookie', type=str)
parser.add_argument('-d', '--download', type=str)
parser.add_argument('-a', '--article', type=str)
parser.add_argument('-s', '--separate', action="store_true")
parser.add_argument('-b', '--books', action="store_true")
parser.add_argument('-o', '--out', type=str)
args = parser.parse_args()

logged: bool = False;
if(args.cookie):
    load_cookie_from_file(args.cookie)
    logged = True

if(args.books and logged):
    books = download_books_list()
    for entry in books:
        print(entry['title'] + "\t" + entry['id'])

if(args.download and not args.article and logged):
    if(not args.separate):
        book: str = get_book_by_id(args.download)
        book = download_images(book)
        with open(args.out if args.out else 'book.html', 'w') as html_file:
            html_file.write(book)
    else:
        articles: List[str] = get_book_articles_by_id(args.download)
        i: int = 1
        for art in articles:
            art = download_images(art)
            with open('{}.html'.format(i), 'w') as html_file:
                html_file.write(art)
            i += 1

if(args.article and logged):
    if(not args.download):
        raise ValueError("Cannot download article without book's ID!")
    article: Optional[str] = download_article_by_id(args.download, args.article)['content']
    if(article is not None):
        article = download_images(article)
        with open(args.out if args.out else 'article.html', 'w') as html_file:
            html_file.write(article)

