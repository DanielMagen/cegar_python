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
        # such that map[index_in_table] = (weight of edge, reference to the node connected to)
        self.list_of_tables = [{} for _ in range(number_of_tables_in_layer_connected_to)]

    def get_number_of_tables_in_layer_connected_to(self):
        return self.number_of_tables_in_layer_connected_to

    def _check_valid_table_number(self, table_number):
        if not 0 <= table_number < self.number_of_tables_in_layer_connected_to:
            raise Exception("there is no such table")

    # when translating this function to cpp, have the node_connected_to be void* or Node to enable it to contain
    # both arnodes and nodes
    def add_connection(self, table_number, index_in_table, weight, node_connected_to):
        self._check_valid_table_number(table_number)

        self.list_of_tables[table_number][index_in_table] = (weight, node_connected_to)

    def find_weight_of_connection(self, table_number, index_in_table):
        self._check_valid_table_number(table_number)

        return self.list_of_tables[table_number][index_in_table][0]

    def delete_connection(self, table_number, index_in_table):
        """
        :param table_number:
        :param index_in_table:
        :return: the (weight, node_connected_to) of the connection deleted
        """
        weight, node_connected_to = self.list_of_tables[table_number][index_in_table]
        del self.list_of_tables[table_number][index_in_table]
        return weight, node_connected_to

    def move_connection(self, previous_table_number, previous_index_in_table, new_table_number, new_index_in_table):
        """

        :param previous_table_number:
        :param previous_index_in_table:
        :param new_table_number:
        :param new_index_in_table:
        """
        weight, node_connected_to = self.delete_connection(previous_table_number, previous_index_in_table)
        self.add_connection(new_table_number, new_index_in_table, weight, node_connected_to)

    def get_iterator_over_connections(self):
        """
        :return: an iterator of the form
        [table_number, index_in_table, weight, reference_to_node_connected_to]

        the iterator guarantees order in increasing table_number but does not guarantee order in index_in_table
        """
        for current_table_number in range(len(self.list_of_tables)):
            for index_in_table, data in self.list_of_tables[current_table_number].items():
                weight = data[NodeEdges.LOCATION_OF_WEIGHT_IN_MAP]
                reference_to_node_connected_to = data[NodeEdges.LOCATION_OF_REFERENCE_IN_MAP]
                yield [current_table_number, index_in_table, weight, reference_to_node_connected_to]

    def get_copy_which_supports_deletion_in_all_tables(self):
        """
        :return: a copy of the current edges for a layer which supports deletion in all tables
        for this class, this is simply a copy of the object
        """
        return deepcopy(self)


class NodeEdgesForNonDeletionTables(NodeEdges):
    """
    this class is an extension of the NodeEdges class to include a case where assumption (2) holds and
    that there are more than 0 tables which do not support deletion (or moving which needs deletion to occur).

    the idea behind this class is that a list is preferred to a map in the more restrictive case due to caching
    we will access the unchanging nodes quite a lot during the abstraction refinement process and as such
    faster access to the nodes connected to would help a lot
    """

    # this is the general form of the connection data that would be saved for any node
    # not used, simply for visualization
    FORM_OF_CONNECTION_DATA = ['index in table its in', 'weight of connection', 'reference to the node connected to']
    LOCATION_OF_INDEX_IN_TABLE = 0
    LOCATION_OF_WEIGHT_IN_TABLE = 1
    LOCATION_OF_REFERENCE_IN_TABLE = 2

    def __init__(self, number_of_tables_in_layer_connected_to, number_of_tables_that_support_deletion):
        """
        the following arguments given are explained in assumption (2)

        :param number_of_tables_in_layer_connected_to: the number of tables in the adjacent layer
        :param number_of_tables_that_support_deletion:
        """
        super().__init__(number_of_tables_that_support_deletion)

        self.number_of_tables_in_layer_connected_to = number_of_tables_in_layer_connected_to
        self.number_of_tables_that_do_not_support_deletion = number_of_tables_in_layer_connected_to - \
                                                             number_of_tables_that_support_deletion

        # now we will create a list of inner matrices such that
        # 1) if a node is in matrix k then its table k
        # 2) for each node we will save both its index in the table its in and the weight of the connection
        # for example if we will search for the weight of the connection between this node and the node
        # in table 5 in index 3 in the adjacent layer, we will go list_of_tables_that_do_not_support_deletion[5],
        # search there for a triplet of the form (3, weight, node_reference) and return the weight if found
        self.list_of_tables_that_do_not_support_deletion = [[] for _ in
                                                            range(self.number_of_tables_that_do_not_support_deletion)]

    def _check_valid_table_number(self, table_number):
        if not 0 <= table_number < self.number_of_tables_in_layer_connected_to:
            raise Exception("there is no such table")

    def _translate_table_number_to_manager_for_tables_that_support_deletion(self, table_number):
        """
        :param table_number:
        :return:
        for example if we have 7 tables and the last 3 support deletion, then if we want to access table number 5
        we will need to access table 2 in the manager_for_tables_that_support_deletion
        this function converts the 7 to 2
        """
        return table_number - self.number_of_tables_that_do_not_support_deletion

    def _translate_from_table_number_of_manager_to_real_table_number(self, table_number_from_manager):
        """
        the exact opposite of the _translate_table_number_to_manager_for_tables_that_support_deletion function
        :param table_number_from_manager:
        :return:
        """
        return table_number_from_manager + self.number_of_tables_that_do_not_support_deletion

    def add_connection(self, table_number, index_in_table, weight, node_connected_to):
        self._check_valid_table_number(table_number)

        if table_number < self.number_of_tables_that_do_not_support_deletion:
            # use assumption (3), nodes that are added, are added at the end of the table
            data_to_add = [index_in_table, weight, node_connected_to]
            self.list_of_tables_that_do_not_support_deletion[table_number].append(data_to_add)

        else:
            super().add_connection(
                self._translate_table_number_to_manager_for_tables_that_support_deletion(table_number), index_in_table,
                weight, node_connected_to)

    def find_weight_of_connection(self, table_number, index_in_table):
        self._check_valid_table_number(table_number)
        if table_number < self.number_of_tables_that_do_not_support_deletion:
            # the requested node must be in the index given
            # proof:
            # assume towards contradiction it is not in the index it is saved in
            # if its actual index is bigger, it means that either
            # a) the node was given false information about its location - in contradiction to the program instructions
            # b) a node was inserted between this node and the start of the table - in contradiction to assumption (3)
            # if the actual index is smaller, it means that either
            # a) the node was given false information about its location - in contradiction to the program instructions
            # b) a node that lies between this node and the start of the table was deleted from the table - in
            # contradiction to the fact that this table does not support deletion
            current_table = self.list_of_tables_that_do_not_support_deletion[table_number]
            return current_table[index_in_table][NodeEdgesForNonDeletionTables.LOCATION_OF_WEIGHT_IN_TABLE]
        else:
            return super().find_weight_of_connection(
                self._translate_table_number_to_manager_for_tables_that_support_deletion(table_number), index_in_table)

    def delete_connection(self, table_number, index_in_table):
        if not self.number_of_tables_that_do_not_support_deletion <= table_number < \
               self.number_of_tables_in_layer_connected_to:
            raise Exception("there is no such table which supports deletion")

        return super().delete_connection(table_number, index_in_table)

    def get_copy_which_supports_deletion_in_all_tables(self):
        """
        :return: a copy of the current edges for a layer which supports deletion in all tables
        """
        to_return = NodeEdges(self.number_of_tables_in_layer_connected_to)
        for table_number, table in enumerate(self.list_of_tables_that_do_not_support_deletion):
            for entry in table:
                index_in_table = entry[NodeEdgesForNonDeletionTables.LOCATION_OF_INDEX_IN_TABLE]
                weight = entry[NodeEdgesForNonDeletionTables.LOCATION_OF_WEIGHT_IN_TABLE]
                node_connected_to = entry[NodeEdgesForNonDeletionTables.LOCATION_OF_REFERENCE_IN_TABLE]
                to_return.add_connection(table_number, index_in_table, weight, node_connected_to)

        for i in range(self.number_of_tables_that_do_not_support_deletion, self.number_of_tables_in_layer_connected_to):
            to_return.list_of_tables[i] = deepcopy(super().list_of_tables[i])

        return to_return

    def get_iterator_over_connections(self):
        """
        :return: an iterator of the form
        [table_number, index_in_table, weight, reference_to_node_connected_to]

        the iterator guarantees order in increasing table_number but does not guarantee order in index_in_table
        """
        # using assumption (2) the tables which support deletion come first

        for i in range(self.number_of_tables_that_do_not_support_deletion):
            for current_table_number, data in enumerate(self.list_of_tables_that_do_not_support_deletion):
                index_in_table = data[NodeEdgesForNonDeletionTables.LOCATION_OF_INDEX_IN_TABLE]
                weight = data[NodeEdgesForNonDeletionTables.LOCATION_OF_WEIGHT_IN_TABLE]
                reference_to_node_connected_to = data[NodeEdgesForNonDeletionTables.LOCATION_OF_REFERENCE_IN_TABLE]
                yield [current_table_number, index_in_table, weight, reference_to_node_connected_to]

        iterator_for_delete_supporting_tables = super().get_iterator_over_connections()
        for data in iterator_for_delete_supporting_tables:
            # add self.number_of_tables_that_do_not_support_deletion to align the table numbers accordingly
            data[0] += self._translate_from_table_number_of_manager_to_real_table_number(data[0])
            yield data
