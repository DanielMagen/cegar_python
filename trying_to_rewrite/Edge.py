from trying_to_rewrite.GLOBAL_CONSTANTS import VERBOSE


class Edge:
    def __init__(self, source_node_id, dest_node_id, weight):
        self.source_node_id = source_node_id
        self.dest_node_id = dest_node_id
        self.weight = weight

    def get_source_node_id(self):
        return self.source_node_id

    def get_dest_node_id(self):
        return self.dest_node_id

    def get_weight_of_edge(self):
        return self.weight

    def __eq__(self, other, verbose=VERBOSE):
        if self.source_node_id != other.get_source_node_id():
            if verbose:
                print("self.source_node_id ({}) != other.src ({})".format(self.source_node_id,
                                                                          other.get_source_node_id()))
            return False
        if self.dest_node_id != other.get_dest_node_id():
            if verbose:
                print("self.dest_node_id ({}) != other.dest ({})".format(self.dest_node_id, other.get_dest_node_id()))
            return False
        if self.weight != other.get_weight_of_edge():
            if verbose:
                print("self.weight ({}) != other.weight ({})".format(self.weight, other.get_weight_of_edge()))
            return False
        return True

    def __str__(self):
        return "{}--({})-->{}".format(self.source_node_id, self.weight, self.dest_node_id)
