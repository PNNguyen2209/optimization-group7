import random
from utils import load_data
import networkx as nx
from state import State, District
import copy
import time


def extend_cluster(G, state):
    # Select a random district
    random_district = random.choice(list(state.districts))
    for node in list(random_district.boundary):
        neighbors = list(G.neighbors(node))
        random.shuffle(neighbors)
        for neighbor in neighbors:
            if not any(neighbor in district.nodes for district in state.districts):
                random_district.add_node(neighbor)
                return


def update_all_boundaries(G, state):
    for district in state.districts:
        for node in district.nodes:
            # Check if this node has neighbors in a different district
            for neighbor in G.neighbors(node):
                if not any(neighbor in d.nodes for d in state.districts if d != district):
                    if node not in district.boundary:
                        district.boundary.append(node)


def generate_initial_state(G, k):
    nodes = list(G.nodes)
    random.shuffle(nodes)  # Shuffle nodes to randomly pick initial district centers

    state = State(G=G, districts=[District(nodes[i], G) for i in range(k)], k=k)

    # Repeat until all nodes have been assigned to a district
    while any(node not in (n for district in state.districts for n in district.nodes) for node in nodes):
        extend_cluster(G, state)

    # update_all_boundaries(G, state)
    for district in state.districts:
        is_connected(district)
    return state


def is_connected(district: District):
    """
    Check if a subgraph of a district is connected - all nodes are reachable.
    """
    if district.spanning_tree is None:
        G_dis = nx.Graph()
        G_dis.add_nodes_from(district.nodes)
        for node in district.nodes:
            for neighbor in G.neighbors(node):
                if neighbor in district.nodes:
                    G_dis.add_edge(node, neighbor)
        district.update_spanning_tree(G_dis)
    return nx.is_connected(district.spanning_tree)


def generate_new_states(G, current_state):
    start = time.time()
    new_states = []

    for origin_district_index, origin_district in enumerate(current_state.districts):

        for node in origin_district.boundary:

            for neighbor in G.neighbors(node):

                for destination_district_index, destination_district in enumerate(current_state.districts):

                    if destination_district_index != origin_district_index and neighbor in destination_district.nodes:

                        new_state = copy.deepcopy(current_state)
                        new_state.districts[origin_district_index].delete_node(node)
                        new_state.districts[destination_district_index].add_node(node)

                        # Add the new state to the list of new states if it maintains connectivity
                        if is_connected(new_state.districts[origin_district_index]) and is_connected(
                                new_state.districts[destination_district_index]):
                            new_states.append(new_state)
    end = time.time()
    print(f"Time to generate all states: {end - start}")
    return new_states


def tabu_search(G, initial_solution, max_iterations, tabu_list_size):
    # TODO: Implement pseudocode
    best_solution = initial_solution
    best_solution_fitness = initial_solution.fitness()
    current_solution = initial_solution
    tabu_list = []

    for i in range(max_iterations):
        print(f"Iteration {i}")
        start = time.time()
        neighbors = generate_new_states(G, current_solution)
        best_neighbor = None
        best_neighbor_fitness = float('inf')

        for neighbor in neighbors:
            neighbor_fitness = neighbor.fitness()
            print(f"Neighbor fitness: {neighbor_fitness}")
            if neighbor not in tabu_list:
                if neighbor_fitness < best_neighbor_fitness:
                    best_neighbor = neighbor
                    best_neighbor_fitness = neighbor_fitness
            elif neighbor_fitness < best_solution_fitness:
                best_neighbor = neighbor
                best_neighbor_fitness = neighbor_fitness

        if best_neighbor is None:
            break

        # Update tabu list
        current_solution = best_neighbor
        tabu_list.append(best_neighbor)

        if len(tabu_list) > tabu_list_size:
            tabu_list.pop(0)

        if best_neighbor_fitness < best_solution_fitness:
            # Update the best solution if the
            # current neighbor is better
            best_solution = best_neighbor
            best_solution_fitness = best_neighbor_fitness

        end = time.time()
        print(f"Time per iteration: {end - start}")
    return best_solution


def print_solution(solution):
    print(f"Fitness: {solution.fitness()}")
    for district in solution.districts:
        print(f"District: {district.nodes}")
        print("")


if __name__ == '__main__':
    G, total_population, k = load_data.load_data('data/RI')
    if not nx.is_connected(G):
        # If the graph is not connected, consider the largest connected component.
        G = G.subgraph(max(nx.connected_components(G), key=len))

    initial_state = generate_initial_state(G, k)
    new_states = generate_new_states(G, initial_state)

    best_solution = tabu_search(G, initial_state, 20, 10)

    print(f"Initial solution fitness: {initial_state.fitness()}")
    print_solution(best_solution)
