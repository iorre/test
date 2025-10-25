import sys
from collections import defaultdict
from math import inf
from queue import PriorityQueue
from itertools import count
#Чупров Вячеслав

def solve(lines: list[str]) -> int:

    # Парсим исходные данные: состояние коридора и комнат
    hallway, rooms = parse_input(lines)
    
    # Целевое состояние: все комнаты заполнены амфиподами своего типа,
    # коридор — полностью пуст.
    final_hallway = tuple([None] * 11)
    final_rooms = tuple([
        tuple([0] * len(rooms[0])),  # Комната A заполнена типом 0 (A)
        tuple([1] * len(rooms[1])),  # Комната B заполнена типом 1 (B)
        tuple([2] * len(rooms[2])),  # Комната C заполнена типом 2 (C)
        tuple([3] * len(rooms[3]))   # Комната D заполнена типом 3 (D)
    ])
    
    # Поиск минимальной энергии с помощью алгоритма Дейкстры
    return dijkstra(hallway, rooms, final_hallway, final_rooms)


def parse_input(lines: list[str]) -> tuple:

    room_lines = []
    # Извлекаем только те строки, где видны амфиподы (символы A–D)
    for line in lines:
        if '#' in line and any(char in line for char in 'ABCD'):
            room_lines.append(line.strip())
    
    room_depth = len(room_lines)  # глубина комнаты (число амфиподов в каждой)
    rooms = [[None] * room_depth for _ in range(4)]  # заготовка под 4 комнаты

    # Определяем позиции амфиподов в строках ввода (зависит от формата)
    for i, line in enumerate(room_lines):
        if i == 0:  # первая строка с верхними амфиподами
            amphipod_positions = [3, 5, 7, 9]
        else:        # нижняя строка
            amphipod_positions = [1, 3, 5, 7]
            
        # Заполняем комнаты типами амфиподов
        for room_idx, pos in enumerate(amphipod_positions):
            if pos < len(line) and line[pos] in 'ABCD':
                amphipod_type = ord(line[pos]) - ord('A')  # A=0, B=1, C=2, D=3
                rooms[room_idx][i] = amphipod_type

    hallway = tuple([None] * 11)  # коридор всегда начинается пустым
    rooms = tuple(tuple(room) for room in rooms)  # замораживаем структуры для хеширования
    
    return hallway, rooms


# Расстояния от каждой позиции в коридоре до каждой комнаты (используются для расчёта шагов)
distance = {
    (0, 0): 3, (0, 1): 5, (0, 2): 7, (0, 3): 9,
    (1, 0): 2, (1, 1): 4, (1, 2): 6, (1, 3): 8,
    (2, 0): 2, (2, 1): 2, (2, 2): 4, (2, 3): 6,
    (3, 0): 4, (3, 1): 2, (3, 2): 2, (3, 3): 4,
    (4, 0): 6, (4, 1): 4, (4, 2): 2, (4, 3): 2,
    (5, 0): 8, (5, 1): 6, (5, 2): 4, (5, 3): 2,
    (6, 0): 9, (6, 1): 7, (6, 2): 5, (6, 3): 3,
    (7, 0): 7, (7, 1): 5, (7, 2): 3, (7, 3): 3,
    (8, 0): 5, (8, 1): 3, (8, 2): 3, (8, 3): 5,
    (9, 0): 3, (9, 1): 3, (9, 2): 5, (9, 3): 7,
    (10, 0): 3, (10, 1): 5, (10, 2): 7, (10, 3): 9
}


def move_cost(amphipod_type: int, steps: int) -> int:
    # Вычисление энергетической стоимости перемещения амфипода.
    return steps * (10 ** amphipod_type)


def hall_to_room(amphipod_type: int, hallway_pos: int, hallway: tuple, rooms: tuple) -> tuple | None:
    #Попытка переместить амфипода из коридора в его целевую комнату.
    
    # Комната, соответствующая типу амфипода (A->2, B->4, C->6, D->8)
    room_pos = {0: 2, 1: 4, 2: 6, 3: 8}[amphipod_type]
    new_hallway = list(hallway)
    new_rooms = [list(r) for r in rooms]

    # Если в целевой комнате есть чужие амфиподы — вход запрещён
    if any(x is not None and x != amphipod_type for x in rooms[amphipod_type]):
        return None

    # Проверяем, что путь в коридоре свободен
    step = 1 if hallway_pos < room_pos else -1
    for pos in range(hallway_pos + step, room_pos + step, step):
        if hallway[pos] is not None:
            return None

    # Находим самую глубокую свободную позицию в комнате
    for depth in range(len(rooms[amphipod_type]) - 1, -1, -1):
        if new_rooms[amphipod_type][depth] is None:
            new_rooms[amphipod_type][depth] = amphipod_type
            break

    # Обновляем состояние и считаем затраты
    new_hallway[hallway_pos] = None
    steps = abs(room_pos - hallway_pos) + depth + 1
    cost = move_cost(amphipod_type, steps)
    return (tuple(new_hallway), tuple(tuple(r) for r in new_rooms), cost)


def room_to_hall(room_idx: int, hallway_pos: int, hallway: tuple, rooms: tuple) -> tuple | None:
    # Попытка переместить верхнего амфипода из комнаты в указанную позицию коридора
    
    # Позиция выхода из комнаты в коридор
    room_pos = {0: 2, 1: 4, 2: 6, 3: 8}[room_idx]
    new_hallway = list(hallway)
    new_rooms = [list(r) for r in rooms]

    # Находим самого верхнего амфипода (ближе к выходу)
    for depth, amphipod in enumerate(rooms[room_idx]):
        if amphipod is not None:
            break
    else:
        return None  # Комната пуста

    amphipod_type = amphipod

    # Если в комнате только свои амфиподы — двигаться не нужно
    if all(x == room_idx or x is None for x in rooms[room_idx]):
        return None

    # Проверка свободного пути из комнаты в коридор
    step = 1 if room_pos < hallway_pos else -1
    for pos in range(room_pos + step, hallway_pos + step, step):
        if hallway[pos] is not None:
            return None

    # Совершаем перемещение и рассчитываем стоимость
    new_rooms[room_idx][depth] = None
    new_hallway[hallway_pos] = amphipod_type
    steps = abs(room_pos - hallway_pos) + depth + 1
    cost = move_cost(amphipod_type, steps)
    return (tuple(new_hallway), tuple(tuple(r) for r in new_rooms), cost)


def get_neighbors(hallway: tuple, rooms: tuple) -> list:
    # Генерация всех возможных следующих состояний
    
    neighbors = []
    
    # Ходы из коридора в комнаты (если возможно)
    for h, amphipod in enumerate(hallway):
        if amphipod is not None:
            result = hall_to_room(amphipod, h, hallway, rooms)
            if result:
                neighbors.append(result)
    
    # Ходы из комнат в коридор (на свободные позиции)
    for h in range(11):
        # В эти позиции вставать нельзя (входы в комнаты)
        if h in [2, 4, 6, 8]:
            continue

        for r in range(4):
            result = room_to_hall(r, h, hallway, rooms)
            if result:
                neighbors.append(result)
    
    return neighbors


def dijkstra(start_hallway: tuple, start_rooms: tuple, final_hallway: tuple, final_rooms: tuple) -> int:
    # Реализация Дейкстры
    
    # Стоимость каждого состояния (по умолчанию бесконечность)
    costs = defaultdict(lambda: inf)
    costs[(start_hallway, start_rooms)] = 0
    
    # Очередь с приоритетом для выбора состояния с минимальной текущей стоимостью
    unique = count()
    visit = PriorityQueue()
    visit.put((0, next(unique), (start_hallway, start_rooms)))
    
    # Основной цикл алгоритма
    while not visit.empty():
        cost, _, (hallway, rooms) = visit.get()
        
        # Проверка на достижение целевого состояния
        if hallway == final_hallway and rooms == final_rooms:
            return cost
        
        # Перебираем все возможные ходы
        neighbors = get_neighbors(hallway, rooms)
        
        for neighbor in neighbors:
            new_cost = cost + neighbor[2]
            state = (neighbor[0], neighbor[1])
            
            # Если нашли более дешёвый путь до состояния — обновляем
            if new_cost < costs[state]:
                costs[state] = new_cost
                visit.put((new_cost, next(unique), state))
    
    return -1


def main():
    lines = []
    for line in sys.stdin:
        lines.append(line.rstrip('\n'))

    result = solve(lines)
    print(result)


if __name__ == "__main__":
    main()