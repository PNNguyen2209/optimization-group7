import networkx as nx


class State:
    def __init__(self, G, districts=None, k=1):
        self.G = G
        self.districts = districts
        self.k = k

    def add_district(self, district):
        self.districts.append(district)
        self.k = len(self.districts)

    def fitness(self):
        imbalance = self.population_imbalance() + 1
        distances = self.node_distances() + 1
        fitness = 0.5 * (1 / imbalance) + 0.5 * (1 / distances)
        return fitness

    def population_imbalance(self):
        populations = []
        for district in self.districts:
            district_population = sum([self.G.nodes[node]['pop'] for node in district.nodes])
            populations.append(district_population)

        return max(populations) - min(populations)

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

        return sum(avg_distances) / len(avg_distances)


class District:
    def __init__(self, first_node):
        self.nodes = [first_node]
        self.boundary = []
        self.cocycle = []
        self.spanning_tree = None

    def add_node(self, node):
        self.nodes.append(node)

    def delete_node(self, node):
        self.nodes.remove(node)
        self.boundary.remove(node)

    def update_spanning_tree(self, G):
        self.spanning_tree = G