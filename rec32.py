import io
import collections
from surprise import KNNBaseline
from surprise import Dataset
from surprise import get_dataset_dir
import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import pandas as pd


# форматирование названия фильма под wikidata
def films_for_wiki(films: list) -> list:
    for i in range(len(films)):
        if (',' in films[i]):
            temp = films[i].split(',')
            films[i] = temp[1] + temp[0]
        films[i] = films[i].strip()
    return films


# получение Q для наших фильмов (нужно для запроса)
def quary(f:list) ->list:
    q = list()
    for query in f:
        par = {
            'action': 'wbsearchentities',
            'format': 'json',
            'language': 'en',
            'search': query
        }
        res = requests.get("https://www.wikidata.org/w/api.php", params=par)
        result = res.json()['search']
        for j in result:
            if ('film' in j['description']):
                q.append((query, j['id']))
                break
    return q

k = 4
top_n = 5
user = input('Enter user ID:')
# загрузка встроенного набора данных
data = Dataset.load_builtin('ml-100k')
# создание класса
train = data.build_full_trainset()
# использование алгоритма для прогноза
algorithm = KNNBaseline(k, sim_options={'name': 'cosine', 'min_support': 5})
algorithm.fit(train)


# чтение файла в словарь
def read():
    file_name = get_dataset_dir() + '/ml-100k/ml-100k/u.item'
    rid_name = {}
    with io.open(file_name, 'r', encoding='ISO-8859-1') as file:
        for line in file:
            line = line.split('|')
            rid_name[line[0]] = (line[1], line[2])
    return rid_name


# оценка с наилучшими параметрами(test)
test = train.build_anti_testset()
test = filter(lambda x: x[0] == user, test)
pr = algorithm.test(test)
name = read()


# формируем список для пользователей(uid)
top = collections.defaultdict(list)
for uid, iid, _, est, _ in pr:
    top[uid].append((iid, round(est, 3)))


# сортируем и добавляем только top_n
for uid, ratings in top.items():
    ratings.sort(key=lambda x: x[1], reverse=True)
    top[uid] = ratings[:top_n]


print('User :'+user)
for movie, rating in top[user]:
    print(movie, str(name[movie]), rating)


# список названия фильмов, которые мы получили
films = list()
for movie, rating in top[user]:
    films.append(name[movie][0][:-6])

films = films_for_wiki(films)
qq = quary(films)
#print(qq)
sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
# выполнение запроса для каждого фильма
for id in qq:
    spaqrql_query = """SELECT ?actor ?actorLabel WHERE {
    wd:"""+id[1]+""" wdt:P577 ?publication_data.
    {
       SELECT ?actor (MIN(?publication_data) as ?first_date) WHERE {
          wd:"""+id[1]+""" wdt:P161 ?actor.
          ?movie wdt:P31 wd:Q11424.
          ?movie wdt:P161 ?actor.
          ?movie wdt:P577 ?publication_date.
       SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
       }
       GROUP BY ?actor ?actorLabel
    }
    FILTER (?first_data = ?publication_date)
    SERVICE wikibase:label { bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". }
    }
    """
    sparql.setQuery(spaqrql_query)
    sparql.setReturnFormat(JSON)
    answer = sparql.query().convert()
    res = pd.io.json.json_normalize(answer['results']['bindings'])
    if len(res.columns) <= 0:
        print(id[0], " :ничего не найдено ")
    else:
        print(id[0] +' ' + res[['actor.value', 'actorLabel.value']].head())

#print(answer)

