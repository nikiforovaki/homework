from pyeasyga import pyeasyga
import json

# данные и куда записывать результат
data = '13.txt'
result = 'result_task1.json'

# наш рюкзак
bag = {'max_weight': 0, 'max_volume': 0, 'items': []}

#загрузка данных из файла
def load_data():
    file = open(data)
    first_line = file.readline().split(' ')
    # первая строка, максимальный объем и вес рюкзака
    bag['max_weight'] = int(first_line[0])
    bag['max_volume'] = int(first_line[1])

    # вещи
    for i in file:
        values = [x for x in i.split(' ')]
        bag['items'].append({'weight': int(values[0]), 'volume': float(values[1]), 'price': int(values[2])})


load_data()
# print(bag)


# функция приспособленности
def fitness(individual, data):
    wei, vol, val = 0, 0, 0
    for (select, item) in zip(individual, data):
        if select:
            wei += item['weight']
            vol += item['volume']
            val += item['price']

    if wei > bag['max_weight'] or vol > bag['max_volume']:
        val = 0

    return val


# используем библиотеку
ga = pyeasyga.GeneticAlgorithm(bag['items'])
# количество особей
ga.population_size = 200
# приспособленность для особей
ga.fitness_function = fitness
ga.run()
# выбор лучших особей
res = ga.best_individual()


selected_items = [bag['items'][index] for index, bit in enumerate(res[1]) if bit == 1]

result_ga = {
    'weight': sum([item['weight'] for item in selected_items]),
    'volume': sum([item['volume'] for item in selected_items]),
    'price': sum([item['price'] for item in selected_items]),
    'items': selected_items
}

with open(result, 'w') as file:
    json.dump(result_ga, file, indent=2)


print(result_ga)