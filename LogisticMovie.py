import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from konlpy.tag import Okt
from numpy import dot
from numpy.linalg import norm

import requests
import json
import getpass
import re

def send_api(key, method, param):
    #API_HOST = "http://api.koreafilm.or.kr/openapi-data2/wisenut/search_api/search_json2.jsp?collection=kmdb_new2&detail=Y&director=%EB%B0%95%EC%B0%AC%EC%9A%B1&ServiceKey="
    API_HOST = "https://api.themoviedb.org/3/movie/popular?"
    param = "language=ko-KR&page=" + str(param)
    api_key = "&api_key=15a455541d3c99ede7cd13d87bc8f58d"
    url = API_HOST + param + api_key
    headers = {'Content-Type' : 'application/json', 'charset': 'UTF-8', 'Accept':'*/*'}

    body = {

    }
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=json.dumps(body, ensure_ascii=False))

        #print("response status %r" % response.status_code)
        #print("response text %r" % response.text)
        return json.loads(response.text)

    except Exception as ex:
        print(ex)

jsonObject = send_api("", "GET", 1)

def send_api(key, method, param):
    #API_HOST = "http://api.koreafilm.or.kr/openapi-data2/wisenut/search_api/search_json2.jsp?collection=kmdb_new2&detail=Y&director=%EB%B0%95%EC%B0%AC%EC%9A%B1&ServiceKey="
    API_HOST = "http://api.koreafilm.or.kr/openapi-data2/wisenut/search_api/search_json2.jsp?collection=kmdb_new2&detail=Y&ServiceKey="
    param = "&query=" + param;
    url = API_HOST + key + param;
    headers = {'Content-Type' : 'application/json', 'charset': 'UTF-8', 'Accept':'*/*'}

    body = {

    }
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers)
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=json.dumps(body, ensure_ascii=False))

        #print("response status %r" % response.status_code)
        #print("response text %r" % response.text)
        return json.loads(response.text)

    except Exception as ex:
        print(ex)


intitle = jsonObject.get("results")[0].get("title")
jsonObject1 = send_api("92V743541U6SVVRCJ8D6", "GET", intitle)
print(jsonObject1)