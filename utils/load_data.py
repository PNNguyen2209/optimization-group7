import pandas as pd
from gerrychain import Graph


def read_matrix(path):
    df = pd.read_csv(f'{path}_distances.csv', index_col=0)
    distances = df.values

    k = 0
    edges = []

    with open(f'{path}.dimacs', 'r') as file:
        lines = file.readlines()

    for line in lines:
        parts = line.strip().split()
        if len(parts) == 3:
            if parts[0] == 'e':
                # Add a tuple for each edge
                edges.append((int(parts[1]), int(parts[2]), distances[int(parts[1]), int(parts[2])]))
            elif parts[1] == 'k':
                # Update k_value with the last 'k' command value
                k = int(parts[2])

    return edges, k


def read_population(path):
    with open(f'{path}.population', 'r') as file:
        total_population = int(file.readline().strip().split('=')[-1])
        data = []
        for line in file:
            parts = line.strip().split()
            if len(parts) == 2:
                identifier, population = int(parts[0]), int(parts[1])
                data.append((identifier, population))
            else:
                print(f"Unexpected line format: {line}")
    return total_population, data


def load_data(path):
    edges, k = read_matrix(path)
    total_population, population = read_population(path)
    G = Graph()
    G.add_weighted_edges_from(edges)
    for (node, pop) in population:
        G.nodes[node]['pop'] = pop
        G.nodes[node]['name'] = node

    return G, total_population, k
