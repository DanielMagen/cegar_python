"""
the idea is to support a plethora of actions in a single united data structure
and to allow outer algorithms to determine which operations to take and in what order.
in other words, separate between the implementation and decisions making.


each network would be represented by both a real live network that can be used for computation and experiments,
and the inner representation which we would implement here

each network inner representation would be implemented as such:
1 - overall we would have a vector of layers
2 - in each layer we would have a vector of 5 "table objects" that would represent
nodes from all possible kinds in the following order:
(pos,inc), (pos,dec), (neg,inc), (neg,dec), (unprocessed)

each table object would contain the nodes in the network in a corresponding order to the one in the network.
also each table would contain the index in the layer of its starting node.
the tables in the same layer would be connected by their index values
such that changing the amount of nodes in a table would change the starting index of all the tables below it.

each node object would contain

- location_data of the form:
[the layer its in, the table its in in the layer (its classification), its index in the table]
(if the node is an inner node nested inside a merged node, its index in the table is irrelevant)

- a list of nodes that are connected to it(maybe have this list correspond to the 5 table structure of the previous
layer so for example we could say that we are connected to 5'th node in the 3rd table of the previous layer. this would
also allow better merging capabilities later on)

- a list of nodes it is connected to (again have this correspond to the 5 table structure of the next layer)

- a weight per edge

- a list of inner nodes : each with their own parameters

- the needed functions to calculate the relations between its inner nodes parameters and its parameters


TODO write down the list of assumptions that you have so that it would be easier to debug later
"""


# TODO BIG ONE : find a way to correspond each action here to an action in the real network
class ARNetwork:
    def __init__(self, network):
        number_of_layers_in_network = len(network)
        # will probably be converted into a vector
        self.layers_tables = []

        for i in range(number_of_layers_in_network):
            tables_for_this_layer = [ARTable(0,
                                             ARTable.NO_PREVIOUS_TABLE,
                                             ARTable.NO_NEXT_TABLE)]

            for _ in range(4):
                tables_for_this_layer.append(tables_for_this_layer[-1].create_table_below())
            self.layers_tables.append(tables_for_this_layer)

        # TODO go over all nodes in the network and add them
        #  to table 5 (the unprocessed nodes) in their corresponding layers
        pass

    @staticmethod
    def type_to_number_of_map(type_of_node):
        """
        :param type_of_node: (pos,inc), (pos,dec), (neg,inc), (neg,dec), (unprocessed)
        :return: the number of table corresponding to the type given in the list of 5 tables
        """
        return [('pos', 'inc'), ('pos', 'dec'), ('neg', 'inc'), ('neg', 'dec'), 'unprocessed'].index(type_of_node)


class ARTable:
    # the table_starting_index that should be given if there are no nodes in table
    INDEX_OF_START_IF_NO_NODES_IN_TABLE = -1

    NO_NEXT_TABLE = None

    NO_PREVIOUS_TABLE = None

    def __init__(self, table_number, previous_table, next_table):
        """

        :param table_number: the number of the table in the overall table order.

        :param previous_table:
        :param next_table:
        """
        self.table_number = table_number

        # the index of the first node in the table in the corresponding layer. for example if the table contains the
        # nodes in indices 2-10, then table_starting_index = 2. it simply states where in the layer the table starts
        # the table always starts empty so its set to INDEX_OF_START_IF_NO_NODES_IN_TABLE accordingly
        self.table_starting_index = ARTable.INDEX_OF_START_IF_NO_NODES_IN_TABLE

        self.previous_table = previous_table
        self.next_table = next_table
        self.ar_nodes = []

    def create_table_below(self):
        assert self.next_table == ARTable.NO_NEXT_TABLE

        table_to_return = ARTable(self.table_number + 1, self, ARTable.NO_NEXT_TABLE)
        self.next_table = table_to_return

        return table_to_return

    def get_number_of_nodes_in_table(self):
        return len(self.ar_nodes)

    def decrease_starting_node_index(self):
        """
        decreases the starting index of the table and all the tables under it.
        should have no effect for empty tables.
        i.e. if the table current table_starting_index is ARTable.INDEX_OF_START_IF_NO_NODES_IN_TABLE
        it ignores the request but passes it on to lower level tables.

        this function is used to propagate the fact that a node was removed above without affecting the tables which
        have no nodes in them
        """
        if self.table_starting_index != ARTable.INDEX_OF_START_IF_NO_NODES_IN_TABLE:
            self.table_starting_index -= 1

        if self.next_table is not ARTable.NO_NEXT_TABLE:
            self.next_table.decrease_starting_node_index()

    def increase_starting_node_index(self):
        """
        increases the starting index of the table and all the tables under it.
        should have no effect for empty tables.
        i.e. if the table current table_starting_index is ARTable.INDEX_OF_START_IF_NO_NODES_IN_TABLE
        it ignores the request but passes it on to lower level tables.

        this function is used to propagate the fact that a node was inserted above without affecting the tables which
        have no nodes in them
        """
        if self.table_starting_index != ARTable.INDEX_OF_START_IF_NO_NODES_IN_TABLE:
            self.table_starting_index += 1

        if self.next_table is not ARTable.NO_NEXT_TABLE:
            self.next_table.increase_starting_node_index()

    def get_number_of_nodes_after_table_ends(self):
        """
        :return: how many nodes there are in the layer after we finish going through the entire table and all the tables
        before it
        """
        how_many_nodes_before_table = 0
        if self.previous_table is not ARTable.NO_PREVIOUS_TABLE:
            how_many_nodes_before_table += self.previous_table.get_number_of_nodes_after_table_ends()

        return how_many_nodes_before_table + self.get_number_of_nodes_in_table()

    def initialize_table_starting_index_based_on_previous_tables(self):
        """
        sets the table table_starting_index to be the next available index.
        its main purpose is to initialize the table_starting_index when its currently set to
        ARTable.INDEX_OF_START_IF_NO_NODES_IN_TABLE.
        for example when we add the first node to the first table we interact with, it would set its
        table_starting_index to be 0.
        but is shouldn't do any harm if called during the run (although calling it on a non empty table
        should have no purpose)
        """
        if self.previous_table is ARTable.NO_PREVIOUS_TABLE:
            self.table_starting_index = 0
        else:
            # the indices start with 0, so the count of how many nodes are before the table is equal to the
            # table_starting_index of the table
            self.table_starting_index = \
                self.previous_table.get_number_of_nodes_after_table_ends()

    def add_node_to_table_end(self, ar_node):
        if len(self.ar_nodes) == 0:
            # the table is currently empty, use the initialize_table_starting_index_based_on_previous_tables to
            # initialize its table_starting_index
            self.initialize_table_starting_index_based_on_previous_tables()

        self.ar_nodes.append(ar_node)

        # change the inserted node location_data so that its table number and index would correspond to its new location
        ar_node.set_table(self.table_number, len(self.ar_nodes) - 1)

        # now notify all bottom tables that their table_starting_index has increased
        if self.next_table is not ARTable.NO_NEXT_TABLE:
            self.next_table.increase_starting_node_index()

    def remove_node_from_table(self, ar_node_to_remove, remove_node_from_its_neighbors=False):
        """
        this method removes the given node from the table and updates the table accordingly.
        it does not notify the node neighbors that its table has changed.
        however, if remove_node_from_all_of_its_neighbors is set to true, it will remove the node from its neighbors.

        :param ar_node_to_remove:

        :param remove_node_from_its_neighbors: if this is sets to true this method
        actually removes the node from existence because not only is the node removed from the table
        and hence from the entire layer, but it is also removed from all of its neighbors too.
        it should only be set to true if you are certain that the given node should be deleted and never used again.
        """
        # check that the node belongs to this table
        # assumes that the layers are correct
        assert ar_node_to_remove.get_table_number == self.table_number

        if remove_node_from_its_neighbors:
            ar_node_to_remove.remove_node_from_all_of_its_neighbors()

        index_in_table = ar_node_to_remove.get_index_in_table()
        del self.ar_nodes[index_in_table]

        # the index_in_table of all the nodes that came after the node that was removed has changed
        # so change them accordingly
        for i in range(index_in_table, len(self.ar_nodes)):
            self.ar_nodes[i].set_index_in_table(i)

        # now check if the table is empty again and if so set table_starting_index accordingly
        if len(self.ar_nodes) == 0:
            self.table_starting_index = ARTable.INDEX_OF_START_IF_NO_NODES_IN_TABLE

        # now notify all bottom tables that their table_starting_index has decreased
        if self.next_table is not ARTable.NO_NEXT_TABLE:
            self.next_table.decrease_starting_node_index()

    def move_node_to_other_table(self, ar_node, table_to_move_node_to):
        self.remove_node_from_table(ar_node, remove_node_from_its_neighbors=False)
        table_to_move_node_to.add_node_to_table_end(ar_node)

    def merge_nodes(self, list_of_indices_of_nodes_to_merge):
        """
        :param list_of_indices_of_nodes_to_merge: a list of indices
        will merge all nodes in the corresponding indices in self.ar_nodes
        and update the table accordingly
        """
        pass


class ARNode():
    ID_INDEX_OF_LAYER_NUMBER = 0
    ID_INDEX_OF_TABLE_NUMBER = 1
    ID_INDEX_OF_INDEX_IN_TABLE = 2

    def __init__(self, layer_number, table_number, index_in_table):
        self.location_data = [layer_number, table_number, index_in_table]

        ############################################## how should I represent the neighbors lists in a way that would
        ################################ enable efficient manipulation?

        self.nodes_connected_to = []
        self.nodes_that_are_connected_to_it = []
        pass

    def get_table_number(self):
        return self.location_data[ARNode.ID_INDEX_OF_TABLE_NUMBER]

    def get_index_in_table(self):
        return self.location_data[ARNode.ID_INDEX_OF_INDEX_IN_TABLE]

    def set_table(self, table_number, index_in_table):
        self.location_data[ARNode.ID_INDEX_OF_TABLE_NUMBER] = table_number
        self.location_data[ARNode.ID_INDEX_OF_INDEX_IN_TABLE] = index_in_table
        self.notify_all_neighbors_that_id_changed()

    def set_index_in_table(self, index_in_table):
        self.location_data[ARNode.ID_INDEX_OF_INDEX_IN_TABLE] = index_in_table
        self.notify_all_neighbors_that_id_changed()

    def notify_all_neighbors_that_id_changed(self, ):
        # TODO 'tell' all the nodes it has any connections to that its id has changed
        pass

    def remove_node_from_all_of_its_neighbors(self):
        """
        removes the node from all of its neighbors
        """
        pass
