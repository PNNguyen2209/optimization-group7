import networkx as nx
import numpy as np


class State:
    def __init__(self, G, districts=None, k=1):
        self.G = G
        self.districts = districts
        self.k = k

    def add_district(self, district):
        self.districts.append(district)
        self.k = len(self.districts)

    def fitness(self):
        inertia_term = self.node_distances()
        balance_term = self.population_imbalance()
        # fitness = 0.5 * (1 / (inertia_term + 1)) + 0.5 * (1 / (balance_term + 1))
        fitness = 0.65 * balance_term
        return fitness

    def population_imbalance(self):
        populations = []

        for district in self.districts:
            district_population = sum([self.G.nodes[node]['pop'] for node in district.nodes])
            populations.append(district_population)

        variance = np.var(populations)

        return variance

    def node_distances(self):
        """
        Compute the average of the average distances between all nodes in each district
        :return:
        """
        avg_distances = []
        for district in self.districts:

            path_lengths = dict(nx.all_pairs_shortest_path_length(district.spanning_tree))

            # Flatten the list of lengths to a single list containing all lengths
            lengths = [length for target_lengths in path_lengths.values() for length in target_lengths]

            # Compute the average distance
            avg_distance = sum(lengths) / len(lengths)
            avg_distances.append(avg_distance)

        mean_distance = sum(avg_distances) / len(avg_distances)
        variance = sum((dist - mean_distance) ** 2 for dist in avg_distances) / len(avg_distances)
        return variance

    def moment_of_inertia(self):
        inertias = []
        for district in self.districts:
            centroid = district.calculate_centroid()
            inertia = sum(nx.shortest_path_length(self.G, centroid, node) ** 2 for node in district.nodes)
            inertias.append(inertia)
        return sum(inertias) / len(inertias)


class District:
    def __init__(self, first_node, G):
        self.nodes = {first_node}
        self.boundary = {first_node}
        self.cocycle = []
        self.G = G
        self.spanning_tree = None

    def add_node(self, node):
        self.nodes.add(node)

        if any(neighbor not in self.nodes for neighbor in self.G.neighbors(node)):
            self.boundary.add(node)

        for neighbor in self.G.neighbors(node):
            if neighbor in self.nodes and all(n in self.nodes for n in self.G.neighbors(neighbor)):
                self.boundary.discard(neighbor)

    def delete_node(self, node):
        self.nodes.remove(node)
        self.boundary.remove(node)

        for neighbor in self.G.neighbors(node):
            if neighbor in self.nodes and any(n not in self.nodes for n in self.G.neighbors(neighbor)):
                self.boundary.add(neighbor)

    def update_spanning_tree(self, G):
        self.spanning_tree = G

    def calculate_centroid(self):
        min_distance_sum = float('inf')
        centroid = None
        for node in self.nodes:
            distance_sum = sum(nx.shortest_path_length(self.G, node, other) for other in self.nodes)
            if distance_sum < min_distance_sum:
                min_distance_sum = distance_sum
                centroid = node
        return centroid

    def calculate_population(self):
        return sum([self.G.nodes[node]['pop'] for node in self.nodes])

    def calculate_distances(self):
        path_lengths = dict(nx.all_pairs_shortest_path_length(self.spanning_tree))

        # Flatten the list of lengths to a single list containing all lengths
        lengths = [length for target_lengths in path_lengths.values() for length in target_lengths]

        return sum(lengths) / len(lengths)
