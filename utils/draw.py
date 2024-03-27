import networkx as nx
import matplotlib.pyplot as plt
import geopandas as gpd


def draw_graph(G, k, state, population, node_size=1100, node_label_font_size=9, show_districts=False):
    total_population = sum(G.nodes[i]['TOTPOP'] for i in G.nodes)
    ideal_population = total_population / k

    elarge = [(u, v) for (u, v, d) in G.edges(data=True)]

    pos = nx.spring_layout(G, seed=7, scale=0.01)

    if show_districts:
        # obtain districts
        distrs = [G.nodes[i]['DISTR'] for i in range(len(G.nodes))]
        if distrs[0] is not None:
            # nodes
            nx.draw_networkx_nodes(G, pos, node_size=1100, node_color=distrs, cmap='tab20c')
        else:
            nx.draw_networkx_nodes(G, pos, node_size=1100)

    else:
        nx.draw_networkx_nodes(G, pos, node_size=1100)

    # edges
    nx.draw_networkx_edges(G, pos, edgelist=elarge, width=5)

    pop_dict = {node: pop for node, pop in population}
    # node labels
    nx.draw_networkx_labels(G, pos, labels=pop_dict, font_size=9, font_family="sans-serif")
    # edge weight labels
    edge_labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels)

    ax = plt.gca()
    ax.margins(0.08)
    plt.title("State: {}".format(state))
    plt.axis("off")
    plt.tight_layout()
    plt.show()


def draw_map(G, k, gdf, districts=None):

    if districts is None:
        # Plot the Shapefile
        fig, ax = plt.subplots(figsize=(10, 10))
        my_fig = gdf.plot(ax=ax).get_figure()
        plt.show()
    else:  # draw districts
        # Which district is each county assigned to?
        labeling = {i: -1 for i in G.nodes}

        for i in range(k):
            district = districts[i]
            for j in district:
                labeling[j] = i

        # Store district info in nodes
        for node in G.nodes:
            G.nodes[node]['DISTR'] = labeling[node]

        geoid_to_district = {G.nodes[i]['GEOID20']: labeling[i] for i in G.nodes}

        assignments = []

        for i in range(len(gdf)):
            geoid = int(gdf['GEOID20'][i])
            assignments.append(geoid_to_district[geoid])

        gdf['assignment'] = assignments
        fig, ax = plt.subplots(figsize=(10, 10))
        my_fig = gdf.plot(column='assignment', ax=ax).get_figure()
        plt.show()
