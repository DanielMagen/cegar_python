""""
fix

"""



class ARNode:
    def __init__(self, name, ar_type, in_edges, out_edges,
                 bias=0.0, activation_func=relu):
        self.name = name
        self.ar_type = ar_type
        self.activation_func = activation_func
        self.in_edges = in_edges
        self.out_edges = out_edges
        self.bias = bias

    def __eq__(self, other, verbose=VERBOSE):
        if self.name != other.name:
            if verbose:
                print("self.name ({}) != other.name ({})".format(self.name, other.name))
            return False
        if self.ar_type != other.ar_type:
            if verbose:
                print("self.ar_type ({}) != other.ar_type ({})".format(self.ar_type, other.ar_type))
            return False
        if self.activation_func != other.activation_func:
            if verbose:
                print("self.activation_func ({}) != other.activation_func ({})".format(self.activation_func,
                                                                                       other.activation_func))
            return False
        if self.bias != other.bias:
            if verbose:
                print("self.bias ({}) != other.bias ({})".format(self.bias, other.bias))
            return False
        if len(self.in_edges) != len(other.in_edges):
            if verbose:
                print("len(self.in_edges) ({}) != len(other.in_edges) ({})".format(len(self.in_edges),
                                                                                   len(other.in_edges)))
            return False
        other_in_edges_sorted = sorted(other.in_edges, key=lambda edge: (edge.src, edge.dest))
        for i, edge in enumerate(sorted(self.in_edges, key=lambda edge: (edge.src, edge.dest))):
            if edge != other_in_edges_sorted[i]:
                if verbose:
                    print("self.in_edges[{}] ({}) != other.in_edges[{}] ({})".format(i, self.in_edges[i], i,
                                                                                     other.in_edges[i]))
                return False
        if len(self.out_edges) != len(other.out_edges):
            if verbose:
                print("len(self.out_edges) ({}) != len(other.out_edges) ({})".format(len(self.out_edges),
                                                                                     len(other.out_edges)))
            return False
        other_out_edges_sorted = sorted(other.out_edges, key=lambda edge: (edge.src, edge.dest))
        for i, edge in enumerate(sorted(self.out_edges, key=lambda edge: (edge.src, edge.dest))):
            if edge != other_out_edges_sorted[i]:
                if verbose:
                    print("self.out_edges[{}] ({}) != other.out_edges[{}] ({})".format(i, self.out_edges[i], i,
                                                                                       other.out_edges[i]))
                return False
        return True

    def get_positivity(self):
        if self.out_edges:
            is_positive = any([e.weight < 0 for e in self.out_edges])
        else:
            is_positive = True
        return "pos" if is_positive else "neg"

    def split_pos_neg(self, name2node_map):
        node_pos = ARNode(name=self.name + "_pos",
                          ar_type="",
                          activation_func=self.activation_func,
                          in_edges=[],
                          out_edges=[],
                          bias=self.bias
                          )
        node_neg = ARNode(name=self.name + "_neg",
                          ar_type="",
                          activation_func=self.activation_func,
                          in_edges=[],
                          out_edges=[],
                          bias=self.bias
                          )
        for edge in self.out_edges:
            if edge.weight >= 0:
                src_node = node_pos
                src_suffix = "_pos"
            else:
                src_node = node_neg
                src_suffix = "_neg"
            # flag to validate that at least one edge is generated from original
            at_least_one_edge_flag = False
            for dest_suffix in ["", "_pos", "_neg"]:  # "" if next layer is output
                dest_node = name2node_map.get(edge.dest + dest_suffix, None)
                if dest_node is not None:
                    new_edge = Edge(src=edge.src + src_suffix,
                                    dest=edge.dest + dest_suffix,
                                    weight=edge.weight)
                    src_node.out_edges.append(new_edge)
                    dest_node.in_edges.append(new_edge)
                    at_least_one_edge_flag = True
            assert at_least_one_edge_flag
        # add splitted node to result if it has out edges
        splitted_nodes = []
        if node_pos.out_edges:
            splitted_nodes.append(node_pos)
        if node_neg.out_edges:
            splitted_nodes.append(node_neg)
        # print(node_inc)
        # print(node_dec)
        # print("+"*30)
        return splitted_nodes

    def split_inc_dec(self, name2node_map):
        node_inc = ARNode(name=self.name + "_inc",
                          ar_type="inc",
                          activation_func=self.activation_func,
                          in_edges=[],
                          out_edges=[],
                          bias=self.bias
                          )
        node_dec = ARNode(name=self.name + "_dec",
                          ar_type="dec",
                          activation_func=self.activation_func,
                          in_edges=[],
                          out_edges=[],
                          bias=self.bias
                          )

        for edge in self.out_edges:
            # print(edge)
            if edge.dest + "_inc" in name2node_map.keys():
                dest_node = name2node_map[edge.dest + "_inc"]
                # print("edge to inc")
                if edge.weight >= 0:
                    # print("edge>=0")
                    new_edge = Edge(src=edge.src + "_inc",
                                    dest=edge.dest + "_inc",
                                    weight=edge.weight)
                    node_inc.out_edges.append(new_edge)
                else:
                    # print("edge<0")
                    new_edge = Edge(src=edge.src + "_dec",
                                    dest=edge.dest + "_inc",
                                    weight=edge.weight)
                    node_dec.out_edges.append(new_edge)
                dest_node.in_edges.append(new_edge)
            # not "elif" but "if". both conditions can hold simultaneously
            if edge.dest + "_dec" in name2node_map.keys():
                dest_node = name2node_map[edge.dest + "_dec"]
                # print("edge to dec")
                if edge.weight >= 0:
                    # print("edge>=0")
                    new_edge = Edge(src=edge.src + "_dec",
                                    dest=edge.dest + "_dec",
                                    weight=edge.weight)
                    node_dec.out_edges.append(new_edge)
                else:
                    # print("edge<0")
                    new_edge = Edge(src=edge.src + "_inc",
                                    dest=edge.dest + "_dec",
                                    weight=edge.weight)
                    node_inc.out_edges.append(new_edge)
                dest_node.in_edges.append(new_edge)

        # add splitted node to result if it has out edges
        splitted_nodes = []
        if node_inc.out_edges:
            splitted_nodes.append(node_inc)
        if node_dec.out_edges:
            splitted_nodes.append(node_dec)
        # print(node_inc)
        # print(node_dec)
        # print("+"*30)
        return splitted_nodes

    def update_in_edges(self, updated_names_map):
        # update in_edges to include new_in_edges
        # e.g. after split a node, the edges are updated
        # @updated_names_map maps old name to new name during update,
        # all in_edges with dest not in updated_names_map will be the same
        # all in_edges with dest in updated_names_map are replaced by new edge
        # print("update_in_edges()")
        if not hasattr(self, "new_in_edges"):
            return
        updated_in_edges = []
        # import IPython
        # IPython.embed()
        for nie in self.new_in_edges:
            for ie in self.in_edges:
                replace = False
                if ie.src in updated_names_map.keys():
                    if ie.dest == nie.dest and updated_names_map[ie.src] == nie.src:
                        replace = True
                if replace:
                    updated_in_edges.append(nie)
                else:
                    updated_in_edges.append(ie)
            # print("replace={}".format(replace))
        self.in_edges = updated_in_edges
        del self.new_in_edges

    def update_out_edges(self, updated_names_map):
        # update out_edges to include new_out_edges
        # print("update_out_edges({})".format(updated_names_map.items()))
        if not hasattr(self, "new_out_edges") or self.new_out_edges == []:
            return
        updated_out_edges = []
        # updated_names_map include the source name of union node, new_union2new_split include the new node
        # e.g if updated_names_map={"a_b": "b"}, then new_union2new_split={"a":"b"}
        """
        new_union2new_split = {}
        for src_union, splitted_node in updated_names_map.items():
            parts = src_union.split("+")
            new_union_name = "+".join([p for p in parts if p !! splitted_node]) 
            new_union2new_split[new_union_name] = splitted_node
        """
        # if updated_names_map == {'x_3_22_pos_inc+x_3_27_pos_inc+x_3_41_pos_inc': 'x_3_27_pos_inc+x_3_41_pos_inc'} and self.name == "x_2_0_pos_inc":
        #    import IPython
        #    IPython.embed()
        for noe in self.new_out_edges:
            # print("noe={}".format(noe))
            # import IPython
            # IPython.embed()

            for oe in self.out_edges:
                replace = False
                if oe.dest in updated_names_map.keys():
                    if noe.src == oe.src and updated_names_map[oe.dest] == noe.dest:
                        # print("suitable oe = {}".format(oe))
                        replace = True
                #        break
                if replace:
                    updated_out_edges.append(noe)
                else:
                    updated_out_edges.append(oe)
            # print("replace={}".format(replace))
        self.out_edges = updated_out_edges
        del self.new_out_edges

    def __str__(self):
        return "\n\t\t".join(
            [
                "name={}".format(self.name),
                "ar_type={}".format(self.ar_type),
                "activation_func={}".format(self.activation_func),
                "in_edges={}".format(", ".join(e.__str__()
                                               for e in self.in_edges)),
                "out_edges={}".format(", ".join(e.__str__()
                                                for e in self.out_edges))
            ])
