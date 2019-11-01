import json
from csv import reader
from math import sqrt


# Загрузка файла
def load(filename: str, valueType: type) -> dict:
    result = dict()
    with open(filename, newline='') as file:
        read = reader(file)
        next(read)
        filel = list(read)
        for line in filel:
            values = list()
            for value in line[1:len(line)]:
                values.append(valueType(value))
            result[line[0]] = values
        return result



# подсчет метрики сходства для пользователей c rates1 и rates2(по формуле)
def sim(rates1: list, rates2: list) -> float:
    sum1 = sum2 = sum3 = 0
    for i in range(len(rates1)):
        if int(rates1[i]) != -1 and int(rates2[i]) != -1:
            sum1 += int(rates1[i]) * int(rates2[i])
            sum2 += int(rates1[i]) ** 2
            sum3 += int(rates2[i]) ** 2
    cos = sum1 / (sqrt(sum2) * sqrt(sum3))
    return cos


# подсчет средней оценки для пользователя
def avg(u: list) -> float:
    sum1 = i = 0
    for rate in u:
        if int(rate) != -1:
            sum1 += int(rate)
            i += 1
    return sum1 / i


data = load("data/data.csv", int)
days = load("data/context_day.csv", str)
places = load("data/context_place.csv", str)
# kNN
k = 4
user_id ='User 5'


# словарь метрик для всех пользователей
simm = {}
user_r = data[user_id]
for user in data:
    if user == user_id:
        continue
    user_rates = data[user]
    simm[user] = sim(user_r, data[user])
# сортированный список метрик
sorted_sims = list(map(lambda x: x[0], sorted(simm.items(), key=lambda kv: kv[1], reverse=True)))
prediction = {}
for i in range(len(user_r)):
    if user_r[i] != -1:
        continue
    nearest = []
    count = 0
    for n in sorted_sims:
        # условие, чтобы сумма считалась по k
        if count >= k:
            break
        if data[n][i] != -1:
            nearest.append(n)
        count += 1
    sum1 = sum2 = 0
    for v in nearest:
        sum1 += simm[v] * (data[v][i] - avg(data[v]))
        sum2 += abs(simm[v])
    prediction[i+1] = round(avg(user_r) + sum1/ sum2, 3)

"""
Алгоритм рекомендации: проходим всех пользователей и находим у них фильм, который не смотрел нащ пользователь,
был просмотрен в выходные и был просмотрен дома
Если такой фильм найден, то метрика сходства умножается на оценку пользователя об этом фильме (simm[user]*rates[i])
Получаем ценность фильма, если словаре есть рекомендация с меньшей ценностью, то заменяем.
После всего сортируем и рекомендуем фильм, которые имеет саму большую ценность
"""
reclist = dict()
recmovie = dict()
for user in data.keys():
    for rates in data.values():
        if user != user_id:
            for i in range(30):
                if user_r[i] == -1 and data[user][i] != -1 and (days[user][i] == " Sat" or days[user][i] == " Sun") \
                        and places[user][i] == " h":
                    rec= float(simm[user]) * int(rates[i])
                    if i not in reclist.keys() or reclist[i] < rec:
                        reclist[i] = rec
sorted_rec = list(reclist.items())
sorted_rec.sort(key=lambda value: value[1], reverse=True)
recmovie["Movie " + str(sorted_rec[0][0] + 1)] = round(sorted_rec[0][1], 3)


res = {
    "User": user_id,
    "Rates": prediction,
    "Recommed": recmovie
}

print(res)
with open(user_id + '.json', 'w') as outfile:
    json.dump(obj=res, fp=outfile, indent=4)














