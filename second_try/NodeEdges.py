# TODO add checks for when connection is non existent

from copy import deepcopy


class NodeEdges:
    """
    this class would be used to hold and manage 1-sided node edges
    i.e. it will only hold either outgoing or incoming edges
    it would work under the assumptions detailed in the ASSUMPTIONS file
    """
    LOCATION_OF_WEIGHT_IN_MAP = 0
    LOCATION_OF_REFERENCE_IN_MAP = 1

    def __init__(self, number_of_tables_in_layer_connected_to):
        self.number_of_tables_in_layer_connected_to = number_of_tables_in_layer_connected_to

        # for tables which support deletion, we will use a list of unordered maps
        # such that map[key_in_table] = (weight of edge, reference to the node connected to)
        self.list_of_tables = [{} for _ in range(number_of_tables_in_layer_connected_to)]

    def get_number_of_tables_in_layer_connected_to(self):
        return self.number_of_tables_in_layer_connected_to

    def _check_valid_table_number(self, table_number):
        if not 0 <= table_number < self.number_of_tables_in_layer_connected_to:
            raise Exception("there is no such table")

    def check_if_connection_exist(self, table_number, key_in_table):
        self._check_valid_table_number(table_number)

        return key_in_table in self.list_of_tables[table_number]

    # when translating this function to cpp, have the node_connected_to be of type void* to avoid circular dependencies
    def add_or_edit_connection(self, table_number, key_in_table, weight, node_connected_to):
        """
        if a connection already exist between a node and the node we are given it overrides its data with the
        given data. otherwise it simply adds the connection data
        :param table_number:
        :param key_in_table:
        :param weight:
        :param node_connected_to:
        """
        self._check_valid_table_number(table_number)

        self.list_of_tables[table_number][key_in_table] = (weight, node_connected_to)

    def find_weight_of_connection(self, table_number, key_in_table):
        self._check_valid_table_number(table_number)

        return self.list_of_tables[table_number][key_in_table][0]

    def delete_connection(self, table_number, key_in_table):
        """
        :param table_number:
        :param key_in_table:
        :return: the (weight, node_connected_to) of the connection deleted
        """
        weight, node_connected_to = self.list_of_tables[table_number][key_in_table]
        del self.list_of_tables[table_number][key_in_table]
        return weight, node_connected_to

    def move_connection(self, previous_table_number, previous_key_in_table, new_table_number, new_key_in_table):
        """

        :param previous_table_number:
        :param previous_key_in_table:
        :param new_table_number:
        :param new_key_in_table:
        """
        weight, node_connected_to = self.delete_connection(previous_table_number, previous_key_in_table)
        self.add_or_edit_connection(new_table_number, new_key_in_table, weight, node_connected_to)

    def get_iterator_over_connections(self):
        """
        :return: an iterator of the form
        [table_number, key_in_table, weight, reference_to_node_connected_to]

        the iterator guarantees order in increasing table_number but does not guarantee order in key_in_table
        """
        for current_table_number in range(len(self.list_of_tables)):
            for key_in_table, data in self.list_of_tables[current_table_number].items():
                weight = data[NodeEdges.LOCATION_OF_WEIGHT_IN_MAP]
                reference_to_node_connected_to = data[NodeEdges.LOCATION_OF_REFERENCE_IN_MAP]
                yield [current_table_number, key_in_table, weight, reference_to_node_connected_to]

