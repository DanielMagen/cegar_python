# TODO add checks for when connection is non existent

from copy import deepcopy


class NodeEdges:
    """
    this class would be used to hold and manage 1-sided node edges
    i.e. it will only hold either outgoing or incoming edges
    it would work under the assumptions detailed in the ASSUMPTIONS file
    """

    def __init__(self, number_of_tables_in_layer_connected_to):
        self.number_of_tables_in_layer_connected_to = number_of_tables_in_layer_connected_to

        # for tables which support deletion, we will use a list of unordered maps
        # such that map[index_in_table] = weight of edge
        self.list_of_tables = [{} for _ in range(number_of_tables_in_layer_connected_to)]

    def _check_valid_table_number(self, table_number):
        if not 0 <= table_number < self.number_of_tables_in_layer_connected_to:
            raise Exception("there is no such table")

    def add_connection(self, table_number, index_in_table, weight):
        self._check_valid_table_number(table_number)

        self.list_of_tables[table_number][index_in_table] = weight

    def find_weight_of_connection(self, table_number, index_in_table):
        self._check_valid_table_number(table_number)

        return self.list_of_tables[table_number][index_in_table]

    def delete_connection(self, table_number, index_in_table):
        del self.list_of_tables[table_number][index_in_table]


class NodeEdgesForNonDeletionTables(NodeEdges):
    """
    this class is an extension of the NodeEdges class to include a case where assumption (2) holds and
    that there are more than 0 tables which do not support deletion

    the idea behind this class is that a list is preferred to a map in the more restrictive case due to caching
    we will access the unchanging nodes quite a lot during the abstraction refinement process and as such
    faster access to the nodes connected to would help a lot
    """

    # this is the general form of the connection data that would be saved for any node
    FORM_OF_CONNECTION_DATA = ['index in table its in', 'weight of connection']  # not used, simply for visualization
    LOCATION_OF_INDEX_IN_TABLE = 0
    LOCATION_OF_WEIGHT = 1

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
        # search there for a pair of the form (3, weight) and return the weight if found
        self.list_of_tables_that_do_not_support_deletion = [[] for _ in
                                                            range(self.number_of_tables_that_do_not_support_deletion)]

    def _check_valid_table_number(self, table_number):
        if not 0 <= table_number < self.number_of_tables_in_layer_connected_to:
            raise Exception("there is no such table")

    def translate_table_number_to_manager_for_tables_that_support_deletion(self, table_number):
        """
        for example if we have 7 tables and the last 3 support deletion, then if we want to access table number 5
        we will need to access table 2 in the manager_for_tables_that_support_deletion
        this function converts the 7 to 2
        :param table_number:
        :return:
        """
        return table_number - self.number_of_tables_that_do_not_support_deletion

    def add_connection(self, table_number, index_in_table, weight):
        """

        :param table_number:
        :param index_in_table:
        :param weight:
        :return:
        """
        self._check_valid_table_number(table_number)

        if table_number < self.number_of_tables_that_do_not_support_deletion:
            # use assumption (3), nodes that are added, are added at the end of the table
            data_to_add = [index_in_table, weight]
            self.list_of_tables_that_do_not_support_deletion[table_number].append(data_to_add)

        else:
            super().add_connection(
                self.translate_table_number_to_manager_for_tables_that_support_deletion(table_number), index_in_table,
                weight)

    def find_weight_of_connection(self, table_number, index_in_table):
        self._check_valid_table_number(table_number)
        if table_number < self.number_of_tables_that_do_not_support_deletion:
            # first guess that the connection is at the location given
            current_table = self.list_of_tables_that_do_not_support_deletion[table_number]
            if len(current_table) > index_in_table and \
                    current_table[index_in_table][
                        NodeEdgesForNonDeletionTables.LOCATION_OF_INDEX_IN_TABLE] == index_in_table:
                return current_table[index_in_table][NodeEdgesForNonDeletionTables.LOCATION_OF_WEIGHT]
            # the guess did not work, use binary search to search to find the relevant index
            # for simplicity I only implemented linear search here
            for i in range(len(current_table)):
                if current_table[i][NodeEdgesForNonDeletionTables.LOCATION_OF_INDEX_IN_TABLE] == index_in_table:
                    return current_table[index_in_table][NodeEdgesForNonDeletionTables.LOCATION_OF_WEIGHT]
        else:
            return super().find_weight_of_connection(
                self.translate_table_number_to_manager_for_tables_that_support_deletion(table_number), index_in_table)

    def delete_connection(self, table_number, index_in_table):
        if not self.number_of_tables_that_do_not_support_deletion <= table_number < \
               self.number_of_tables_in_layer_connected_to:
            raise Exception("there is no such table which supports deletion")

        super().delete_connection(table_number, index_in_table)

    def get_copy_which_supports_deletion_in_all_tables(self):
        """
        :return: a copy of the current edges for a layer which supports deletion in all tables
        """
        to_return = NodeEdges(self.number_of_tables_in_layer_connected_to)
        for table_number, table in enumerate(self.list_of_tables_that_do_not_support_deletion):
            for entry in table:
                index_in_table = entry[NodeEdgesForNonDeletionTables.LOCATION_OF_INDEX_IN_TABLE]
                weight = entry[NodeEdgesForNonDeletionTables.LOCATION_OF_WEIGHT]
                to_return.add_connection(table_number, index_in_table, weight)

        for i in range(self.number_of_tables_that_do_not_support_deletion, self.number_of_tables_in_layer_connected_to):
            to_return.list_of_tables[i] = deepcopy(super().list_of_tables[i])

        return to_return
