import pandas as pd
from gerrychain import Graph
from networkx import DiGraph


def read_matrix(filename):
    df = pd.read_csv(filename, index_col=0)
    edges = []
    for i, row in df.iterrows():
        for j, value in row.items():
            if value != 0:
                edges.append((i, j, value))

    return edges


def read_population(filename):
    with open(filename, 'r') as file:
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


if __name__ == '__main__':
    edges = read_matrix('data/AK_distances.csv')
    total_population, population = read_population('data/AK.population')
    G = Graph()
    G.add_weighted_edges_from(edges)
    for (node, pop) in population:
        G.nodes[node]['population'] = pop

    DG = DiGraph(G)

    print(DG.nodes[160]['population'])
    print(G.nodes[160]['population'])
