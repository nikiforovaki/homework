import io
import collections
from surprise import KNNBaseline
from surprise import Dataset
from surprise import get_dataset_dir

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


print('User {user}:')
for movie, rating in top[user]:
    print(movie, str(name[movie]), rating)