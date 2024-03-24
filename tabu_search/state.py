class State:
    def __init__(self, districts=None, k=1):
        self.districts = districts
        self.k = k

    def add_district(self, district):
        self.districts.append(district)
        self.k = len(self.districts)


class District:
    def __init__(self, first_node):
        self.nodes = [first_node]
        self.boundary = []
        self.cocycle = []

    def add_node(self, node):
        self.nodes.append(node)
