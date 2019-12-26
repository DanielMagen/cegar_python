# maybe make this an inner class inside the node class

class NodeEdges:
    """
    this class would be used to hold and manage 1-sided node edges
    i.e. it will only hold either outgoing or incoming edges
    it would work under the assumptions detailed in the ASSUMPTIONS file
    """
    LOCATION_OF_WEIGHT_IN_MAP = 0
    LOCATION_OF_REFERENCE_IN_MAP = 1

    INDEX_OF_TABLE_NUMBER_IN_DATA = 0
    INDEX_OF_KEY_IN_TABLE_IN_DATA = 1
    INDEX_OF_WEIGHT_IN_DATA = 2
    INDEX_OF_REFERENCE_TO_NODE_CONNECTED_TO_IN_DATA = 3

    def __init__(self, number_of_tables_in_layer_connected_to):
        self.number_of_tables_in_layer_connected_to = number_of_tables_in_layer_connected_to

        # for tables which support deletion, we will use a list of unordered maps
        # such that map[key_in_table] = (weight of edge, reference to the node connected to)
        self.list_of_tables = [{} for _ in range(number_of_tables_in_layer_connected_to)]

    def get_number_of_connections(self):
        number_of_connections = 0
        for table in self.list_of_tables:
            number_of_connections += len(table)
        return number_of_connections

    def get_number_of_tables_in_layer_connected_to(self):
        return self.number_of_tables_in_layer_connected_to

    def _check_valid_table_number_and_raise_error_if_not(self, table_number):
        if not 0 <= table_number < self.number_of_tables_in_layer_connected_to:
            raise Exception("there is no such table")

    def check_if_connection_exist(self, table_number, key_in_table):
        self._check_valid_table_number_and_raise_error_if_not(table_number)

        return key_in_table in self.list_of_tables[table_number]

    def _check_if_connection_exist_and_raise_error_if_not(self, table_number, key_in_table):
        if not self.check_if_connection_exist(table_number, key_in_table):
            raise Exception("no such connection")

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
        self._check_valid_table_number_and_raise_error_if_not(table_number)

        self.list_of_tables[table_number][key_in_table] = (weight, node_connected_to)

    def find_weight_of_connection(self, table_number, key_in_table):
        self._check_valid_table_number_and_raise_error_if_not(table_number)
        self._check_if_connection_exist_and_raise_error_if_not(table_number, key_in_table)

        return self.list_of_tables[table_number][key_in_table][NodeEdges.LOCATION_OF_WEIGHT_IN_MAP]

    def get_connection_data_for_neighbor(self, table_number, key_in_table):
        self._check_if_connection_exist_and_raise_error_if_not(table_number, key_in_table)

        data = self.list_of_tables[table_number][key_in_table]
        weight = data[NodeEdges.LOCATION_OF_WEIGHT_IN_MAP]
        reference_to_node_connected_to = data[NodeEdges.LOCATION_OF_REFERENCE_IN_MAP]

        return [table_number, key_in_table, weight, reference_to_node_connected_to]

    def delete_connection(self, table_number, key_in_table):
        """
        :param table_number:
        :param key_in_table:
        :return: the (weight, node_connected_to) of the connection deleted
        """
        self._check_valid_table_number_and_raise_error_if_not(table_number)
        self._check_if_connection_exist_and_raise_error_if_not(table_number, key_in_table)

        weight, node_connected_to = self.list_of_tables[table_number][key_in_table]
        del self.list_of_tables[table_number][key_in_table]
        return weight, node_connected_to

    def move_connection(self, previous_table_number, previous_key_in_table, new_table_number, new_key_in_table,
                        override_existing_connection=False):
        """
        it could override existing connections so be careful when using this method

        :param previous_table_number:
        :param previous_key_in_table:
        :param new_table_number:
        :param new_key_in_table:
        :param override_existing_connection: if true would override an existing connection if it meets it
        """
        # no need to check that the new location is valid, it would be checked by the add_or_edit_connection method
        # self._check_valid_table_number_and_raise_error_if_not(new_table_number)

        # no need to check that the previous location is valid, it would be checked by the delete_connection method
        # self._check_valid_table_number_and_raise_error_if_not(previous_table_number)
        # self._check_if_connection_exist_and_raise_error_if_not(previous_table_number, previous_key_in_table)

        if self.check_if_connection_exist(new_table_number, new_key_in_table) and not override_existing_connection:
            if self.check_if_connection_exist(new_table_number, new_key_in_table):
                raise Exception("tried to override existing connection")

        weight, node_connected_to = self.delete_connection(previous_table_number, previous_key_in_table)
        self.add_or_edit_connection(new_table_number, new_key_in_table, weight, node_connected_to)

    def get_iterator_over_connections(self):
        """
        :return: an iterator on the connections data which is of the form
        [table_number, key_in_table, weight, reference_to_node_connected_to]

        the iterator guarantees order in increasing table_number but does not guarantee order in key_in_table
        """
        for current_table_number in range(len(self.list_of_tables)):
            for key_in_table, data in self.list_of_tables[current_table_number].items():
                weight = data[NodeEdges.LOCATION_OF_WEIGHT_IN_MAP]
                reference_to_node_connected_to = data[NodeEdges.LOCATION_OF_REFERENCE_IN_MAP]
                yield [current_table_number, key_in_table, weight, reference_to_node_connected_to]

    def get_a_list_of_all_connections(self):
        to_return = []
        for data in self.get_iterator_over_connections():
            to_return.append(data)

        return to_return

    def get_a_list_of_all_neighbors_pointers(self):
        to_return = []
        for data in self.get_iterator_over_connections():
            to_return.append(data[NodeEdges.INDEX_OF_REFERENCE_TO_NODE_CONNECTED_TO_IN_DATA])

        return to_return

