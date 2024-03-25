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

    state = State(G=G, districts=[District(nodes[i]) for i in range(k)], k=k)

    # Repeat until all nodes have been assigned to a district
    while any(node not in (n for district in state.districts for n in district.nodes) for node in nodes):
        extend_cluster(G, state)

    update_all_boundaries(G, state)
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


def generate_random_neighbour(G, current_state):
    # Shuffle the list of districts to get random neighbouring state
    #shuffled_districts = current_state.districts.copy()
    random.shuffle(current_state.districts)
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
                            return new_state
    print("nothing was found")





#iterations seem to go from 20 to 80k
#threshold seems to be in range 10^-7 to 10^-2 depending on target objective (compactness/population etc)
def oba_search(G, initial_solution, thresh=0.1, iterations=100):
    current_solution = initial_solution
    current_cost = initial_solution.fitness()
    best_solution = current_solution
    best_cost = current_cost
    # careful with pass by value/reference, maybe need to make copies
    for iter in range(iterations):
        new_solution = generate_random_neighbour(G,current_solution)
        #print(new_solution.node_distances())
        new_cost = new_solution.fitness()
        delta = new_cost - current_cost
        if delta < thresh:
            current_solution = new_solution

            if new_cost < best_cost:
                best_solution = new_solution
                best_cost = new_cost
            if delta < 0:
                thresh = thresh - (1 - (iter / iterations))
        else:
            thresh = thresh + (1 - (iter / iterations))
        #print(best_cost)

    return best_solution


if __name__ == '__main__':
    G, total_population, k = load_data.load_data('data/RI') #state initials
    if not nx.is_connected(G):
        # If the graph is not connected, consider the largest connected component.
        G = G.subgraph(max(nx.connected_components(G), key=len))

    initial_state = generate_initial_state(G, k)
    print(initial_state.fitness())
    print(initial_state.population_imbalance())
    print(initial_state.node_distances())
    solution = oba_search(G, initial_state)
    print(solution.fitness())
    print(solution.population_imbalance())
    print(solution.node_distances())
