import sys
from collections import deque, defaultdict
from typing import List, Tuple


def solve(edges: List[Tuple[str, str]]) -> List[str]:

    def make_graph(edge_list):
        #Создает граф и список шлюзов
        net = defaultdict(list)
        exits = set()

        for a, b in edge_list:
            net[a].append(b)
            net[b].append(a)
            if a.isupper():
                exits.add(a)
            if b.isupper():
                exits.add(b)
        return net, exits

    def bfs_to_gateways(start):
        #Поиск кратчайших расстояний до шлюзов
        dist = {}
        seen = {start}
        q = deque([(start, 0)])

        while q:
            node, d = q.popleft()
            if node in gateways:
                dist[node] = d
                continue

            for nxt in sorted(graph[node]):
                if nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, d + 1))
        return dist

    def nearest_gateway(pos):
        #Возвращает ближайший шлюз (лексикографически, если несколько)
        info = bfs_to_gateways(pos)
        if not info:
            return None

        min_d = min(info.values())
        best = sorted(g for g, d in info.items() if d == min_d)
        return best[0] if best else None

    def shortest_step(src, dest):
        #Возвращает первый шаг по кратчайшему пути до шлюза
        if dest in graph[src]:
            return dest

        parents = {}
        seen = {src}
        q = deque([src])

        while q:
            cur = q.popleft()
            if cur == dest:
                break
            for nxt in sorted(graph[cur]):
                if nxt not in seen:
                    seen.add(nxt)
                    parents[nxt] = cur
                    q.append(nxt)

        if dest not in parents:
            return None

        # восстановление пути
        path = []
        cur = dest
        while cur != src:
            path.append(cur)
            cur = parents[cur]
        path.reverse()
        return path[0] if path else None

    def direct_threats(pos):
        #Список прямых соединений вируса со шлюзами
        return [
            f"{gw}-{pos}"
            for gw in sorted(graph[pos])
            if gw in gateways
        ]

    def all_exit_links():
        #Все соединения со шлюзами (лексикографически)
        links = []
        for gw in sorted(gateways):
            for node in sorted(graph[gw]):
                links.append(f"{gw}-{node}")
        return links
    
    actions = []
    if not edges:
        return actions

    graph, gateways = make_graph(edges)
    virus = "a"

    while True:
        target = nearest_gateway(virus)
        if not target:
            break

        threat = direct_threats(virus)
        if threat:
            action = threat[0]
        else:
            step = shortest_step(virus, target)
            if not step:
                break
            links = all_exit_links()
            if not links:
                break
            action = links[0]

        actions.append(action)
        gw, node = action.split("-")
        graph[gw].remove(node)
        graph[node].remove(gw)

        # обновление позиции вируса
        new_target = nearest_gateway(virus)
        if new_target:
            nxt = shortest_step(virus, new_target)
            if nxt and nxt not in gateways:
                virus = nxt

    return actions


def main():
    edges = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            node1, sep, node2 = line.partition('-')
            if sep:
                edges.append((node1, node2))

    result = solve(edges)
    for edge in result:
        print(edge)


if __name__ == "__main__":
    main()