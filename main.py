import random
import load_data
import networkx as nx
from state import State, District
import copy


def extend_cluster(G, state):
    # Select a random district
    random_district = random.choice(state.districts)
    random.shuffle(random_district.nodes)
    for node in random_district.nodes:
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

    state = State(districts=[District(nodes[i]) for i in range(k)], k=k)

    # Repeat until all nodes have been assigned to a district
    while any(node not in (n for district in state.districts for n in district.nodes) for node in nodes):
        extend_cluster(G, state)

    update_all_boundaries(G, state)
    return state


def is_connected(district):
    #TODO: check if district is not cut
    return True


def generate_new_states(G, current_state):
    new_states = []

    for origin_district_index, origin_district in enumerate(current_state.districts):

        for node in origin_district.boundary:

            for neighbor in G.neighbors(node):

                for destination_district_index, destination_district in enumerate(current_state.districts):

                    if destination_district_index != origin_district_index and neighbor in destination_district.nodes:

                        new_state = copy.deepcopy(current_state)
                        new_state.districts[origin_district_index].delete_node(node)
                        new_state.districts[destination_district_index].add_node(node)

                        # Update boundaries for the new state
                        update_all_boundaries(G, new_state)

                        # new_states.append(new_state)
                        # Add the new state to the list of new states if it maintains connectivity
                        if is_connected(new_state.districts[origin_district_index]) and is_connected(
                                new_state.districts[destination_district_index]):
                            new_states.append(new_state)
    return new_states


def evaluate(state):
    return 1


def oba_search(G, initial_solution, thresh=0.5, iterations=100):
    current_solution = initial_solution
    current_value = evaluate(initial_solution)
    best_solution = current_solution
    best_value = current_value
    # careful with pass by value/reference, maybe need to make copies
    for iter in range(iterations):
        neighbours = generate_new_states(G, current_solution)
        new_solution = random.choice(neighbours)
        new_value = evaluate(new_solution)
        delta = new_value - current_value
        if delta < thresh:
            current_solution = new_solution

            if new_value < best_value:
                best_solution = new_solution
                best_value = new_value
            if delta < 0:
                thresh = 1 - (iter / iterations)
        else:
            thresh = 1 + (iter / iterations)

    return best_solution


if __name__ == '__main__':
    G, total_population, k = load_data.load_data('data/RI')
    if not nx.is_connected(G):
        # If the graph is not connected, consider the largest connected component.
        G = G.subgraph(max(nx.connected_components(G), key=len))

    initial_state = generate_initial_state(G, k)

    new_states = generate_new_states(G, initial_state)
    print("1")
