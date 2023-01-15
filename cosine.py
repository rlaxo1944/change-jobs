import DB.DBConn as DB
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from konlpy.tag import Okt
from numpy import dot
from numpy.linalg import norm

import getpass
data = pd.read_csv('C:/Users/rlaxo/change-jobs/file/movies_metadata.csv', low_memory=False)
#data = pd.read_csv('C:/Users/rlaxo/change-jobs/file/moviesInfo.csv', encoding='cp949')
#data = pd.read_csv('C:/Users/'+getpass.getuser()+'/change-jobs/file/moviesInfo.csv', encoding='cp949')

obj = DB.call_exec('이예인')
print(obj)
obj = DB.call_procedure_mssql('PY_CallTest %s', '김태형')
print(obj)

data = data.head(20000)
data['overview'] = data['overview'].fillna('')
#data['줄거리'] = data['줄거리'].fillna('')

# tfidf = TfidfVectorizer(stop_words=[])
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(data['overview'])
#tfidf_matrix = tfidf.fit_transform(data['줄거리'])
print('TF-IDF 행렬의 크기(shape) :', tfidf_matrix.shape)

# 형태소 분석 테스트
# okt = Okt()
# corpus = [
#     "철수는 통계학과에 다닌다.",
#     "빅데이터 분석에 필요한 것은 통계학적 지식과 프로그래밍 능력이다.",
#     "4차산업의 핵심기술로 인공지능과 빅데이터가 있다.",
#     "텍스트자료는 빅데이터에서 중요한 재료이다."
#     ]
# oo = okt.pos(corpus[1],
#         norm=True,   # 정규화(normalization)
#         stem=True    # 어간추출(stemming)
#         )
# print(oo)

cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)
print('코사인 유사도 연산 결과 :', cosine_sim.shape)

title_to_index = dict(zip(data['title'], data.index))

#dict1 = dict(zip(['a','b','c'], [1,2,3]))
#print(dict1)

# 영화 제목 Father of the Bride Part II의 인덱스를 리턴

def get_recommendations(title, cosine_sim=cosine_sim):
    # 선택한 영화의 타이틀로부터 해당 영화의 인덱스를 받아온다.
    idx = title_to_index[title]

    # 해당 영화와 모든 영화와의 유사도를 가져온다.
    sim_scores = list(enumerate(cosine_sim[idx]))

    # 유사도에 따라 영화들을 정렬한다.
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)

    # 가장 유사한 10개의 영화를 받아온다.
    sim_scores = sim_scores[1:11]

    # 가장 유사한 10개의 영화의 인덱스를 얻는다.
    movie_indices = [idx[0] for idx in sim_scores]

    # 가장 유사한 10개의 영화의 제목을 리턴한다.
    return data['title'].iloc[movie_indices]

str = get_recommendations('The Dark Knight Rises')
print(str)
