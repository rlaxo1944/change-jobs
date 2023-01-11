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

intitle = '그림자괴물'
jsonObject = send_api("92V743541U6SVVRCJ8D6", "GET", intitle)
#print(jsonObject.get("KMAQuery"))
# data = pd.read_csv('movies.csv', encoding='cp949')
#data = pd.read_csv('C:/Users/'+getpass.getuser()+'/change-jobs/file/moviesInfo.csv', encoding='cp949')
#data = pd.read_json(send_api("92V743541U6SVVRCJ8D6", "POST"))
data = pd.DataFrame(jsonObject)
data.head(20)
#data = data.head(20)

okt = Okt()

DOCID = 0
main_plot = []
sub_plot = []
def cos_sim(a, b):
    return dot(a, b)/(norm(a)*norm(b))

def make_matrix(feats, list_data):
    freq_list = []
    for feat in feats:
        freq = 0
        for word in list_data:
            if feat == word:
                freq += 1
        freq_list.append(freq)
    return freq_list

for index, row in data.iterrows():
    #print(type(row)
    #print(row.Data)

    pdata = pd.DataFrame(row.Data)
    for row1 in pdata.iterrows():
        #print(okt.nouns(re.sub('!HS.*?!HE', intitle, row1[1].Result['keywords'])))

        #print(row1[1].Result['keywords'])
        t = re.sub('!HS', '', row1[1].Result['title']).replace(' ', '')
        t = re.sub('!HE', '', t)
        if intitle.replace(' ','') == t:
            DOCID = row1[1].Result['DOCID']
            if DOCID == 'K14428':
                print('DOCID : ' + DOCID)
                print(re.sub('!HS.*?!HE', intitle.replace(' ',''), row1[1].Result['title']).replace(' ', ''))
                print(row1[1].Result['plots']['plot'][0]['plotText'])
                print('형태소 명사 : ', set(okt.nouns(row1[1].Result['plots']['plot'][0]['plotText'])))
                mdata = pd.DataFrame(set(okt.nouns(row1[1].Result['plots']['plot'][0]['plotText'])))
                main_plot = np.array(mdata)


        if main_plot.size > 0:
            tt = re.sub('!HS', '', row1[1].Result['title']).replace(' ', '')
            tt = re.sub('!HE', '', t)
            sdata = pd.DataFrame(set(okt.nouns(row1[1].Result['plots']['plot'][0]['plotText'])))
            sub_plot = np.array(sdata)
            a = make_matrix(main_plot, main_plot)
            b = make_matrix(main_plot, sub_plot)

            #main_plot = main_plot.reshape(1, 84)

            # for row in main_plot:
            #     if sub_plot.size != main_plot.size:
            #         sdata = np.append(sdata, '')
            #         sub_plot = sdata
            #     else:
            #         print('종료')
            #         break

            # sub_plot = np.array(sdata).flatten()
            # main_plot = main_plot.flatten()
            # print(main_plot.size)
            # print(sub_plot.size)


            print(intitle , ' : ' , cos_sim(a, a) , ' , ' , tt , ' : ' , cos_sim(a, b))
            # test = np.array(np.r_[main_plot.reshape(1, 84), sub_plot.reshape(1, 84)])
            #
            #
            # tfidf_vect_simple = TfidfVectorizer()
            # feature_vect_simple = tfidf_vect_simple.fit_transform(test)
            #
            # print(cosine_similarity(feature_vect_simple[0], feature_vect_simple))
            #cos_sim(main_plot, sub_plot)
            #print(row1[1].Result['DOCID'])
            #print(re.sub('!HS.*?!HE', '괴물',row1[1].Result['title']).replace(' ',''))
            #print(row1[1].Result['plots']['plot'][0]['plotText'])
            # rdata = pd.DataFrame(row1.)
            # for row2 in

    #print(row.Data)
    #print("-----")

    # print(row['TotalCount'])
    # print(row[2])
    # print(row.TotalCount)
    # print("=====\n")

#print(data.to_string())
# data['줄거리'] = data['줄거리'].fillna('')
#
# # tfidf = TfidfVectorizer(stop_words=[])
# tfidf = TfidfVectorizer(stop_words='english')
# tfidf_matrix = tfidf.fit_transform(data['줄거리'])
# print('TF-IDF 행렬의 크기(shape) :', tfidf_matrix.shape)
#
# # okt = Okt()
# # corpus = [
# #     "철수는 통계학과에 다닌다.",
# #     "빅데이터 분석에 필요한 것은 통계학적 지식과 프로그래밍 능력이다.",
# #     "4차산업의 핵심기술로 인공지능과 빅데이터가 있다.",
# #     "텍스트자료는 빅데이터에서 중요한 재료이다."
# #     ]
# # oo = okt.pos(corpus[1],
# #         norm=True,   # 정규화(normalization)
# #         stem=True    # 어간추출(stemming)
# #         )
# # print(oo)
#
# cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
# print('코사인 유사도 연산 결과 :', cosine_sim.shape)
#
# title_to_index = dict(zip(data['제명'], data.index))
#
#
# # 영화 제목 Father of the Bride Part II의 인덱스를 리턴
#
# def get_recommendations(title, cosine_sim=cosine_sim):
#     # 선택한 영화의 타이틀로부터 해당 영화의 인덱스를 받아온다.
#     idx = title_to_index[title]
#
#     # 해당 영화와 모든 영화와의 유사도를 가져온다.
#     sim_scores = list(enumerate(cosine_sim[idx]))
#
#     # 유사도에 따라 영화들을 정렬한다.
#     sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
#
#     # 가장 유사한 10개의 영화를 받아온다.
#     sim_scores = sim_scores[1:11]
#
#     # 가장 유사한 10개의 영화의 인덱스를 얻는다.
#     movie_indices = [idx[0] for idx in sim_scores]
#
#     # 가장 유사한 10개의 영화의 제목을 리턴한다.
#     return data['제명'].iloc[movie_indices]
#
# str = get_recommendations('괴물')
# print(str)
