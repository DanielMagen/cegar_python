class TableAbstract:
    # the table_starting_index that should be given if there are no nodes in table
    INDEX_OF_START_IF_NO_NODES_IN_TABLE = -1

    NO_NEXT_TABLE = None

    NO_PREVIOUS_TABLE = None

    NO_NODE_IS_CURRENTLY_BEING_REMOVED = None

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
        self.table_starting_index = TableAbstract.INDEX_OF_START_IF_NO_NODES_IN_TABLE

        self.previous_table = previous_table
        self.next_table = next_table

        # this variable would allow us to track which nodes we are currently changing ourselves, so that for example if
        # we get a notification from a node that its being destroyed and we are the ones deleting it, we can simply
        # ignore this notification.
        self.key_of_node_currently_being_removed_from_table = TableAbstract.NO_NODE_IS_CURRENTLY_BEING_REMOVED

    def create_table_below_of_same_type(self):
        raise NotImplemented("this is an abstract class")

    def get_number_of_nodes_in_table(self):
        raise NotImplemented("this is an abstract class")

    def decrease_starting_node_index(self):
        """
        decreases the starting index of the table and all the tables under it.
        should have no effect for empty tables.
        i.e. if the table current table_starting_index is ARTable.INDEX_OF_START_IF_NO_NODES_IN_TABLE
        it ignores the request but passes it on to lower level tables.

        this function is used to propagate the fact that a node was removed above without affecting the tables which
        have no nodes in them
        """
        if self.table_starting_index != TableAbstract.INDEX_OF_START_IF_NO_NODES_IN_TABLE:
            self.table_starting_index -= 1

        if self.next_table is not TableAbstract.NO_NEXT_TABLE:
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
        if self.table_starting_index != TableAbstract.INDEX_OF_START_IF_NO_NODES_IN_TABLE:
            self.table_starting_index += 1

        if self.next_table is not TableAbstract.NO_NEXT_TABLE:
            self.next_table.increase_starting_node_index()

    def get_number_of_nodes_after_table_ends(self):
        """
        :return: how many nodes there are in the layer after we finish going through the entire table and all the tables
        before it
        """
        how_many_nodes_before_table = 0
        if self.previous_table is not TableAbstract.NO_PREVIOUS_TABLE:
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
        if self.previous_table is TableAbstract.NO_PREVIOUS_TABLE:
            self.table_starting_index = 0
        else:
            # the indices start with 0, so the count of how many nodes are before the table is equal to the
            # table_starting_index of the table
            self.table_starting_index = \
                self.previous_table.get_number_of_nodes_after_table_ends()

    def _add_node_to_table_helper(self, node):
        """
        this helper function would be implemented by the subclasses
        it simply adds the node to the table and returns the key of the new node
        :param node:
        :return the key of the node inserted
        """
        raise NotImplemented("this is an abstract class")

    def add_node_to_table(self, node):
        if self.get_number_of_nodes_in_table() == 0:
            # the table is currently empty, use the initialize_table_starting_index_based_on_previous_tables to
            # initialize its table_starting_index
            self.initialize_table_starting_index_based_on_previous_tables()

        new_node_key = self._add_node_to_table_helper(node)

        # change the inserted node location_data so that its table number and index would correspond to its new location
        node.set_new_table_without_checking(self, self.table_number, new_node_key)

        # now notify all bottom tables that their table_starting_index has increased
        if self.next_table is not TableAbstract.NO_NEXT_TABLE:
            self.next_table.increase_starting_node_index()

    def get_node_by_key(self, node_key):
        raise NotImplemented("this is an abstract class")

    def get_notified_node_wants_to_remove_itself_from_table(self, node_key):
        """
        notify this table that the given node wants to remove itself from this table
        :param node_key:
        """
        if self.key_of_node_currently_being_removed_from_table == node_key:
            # we are the ones who are removing this node, take no further action
            return

        # else simply remove the node from the table. the one who changes the node values should take responsibility
        # for cleaning after the node.
        self._remove_node_from_table_without_affecting_the_node(node_key)

    def _remove_node_from_table_without_affecting_the_node_helper(self, node_key):
        """
        this helper function would be implemented by the subclasses
        simply remove the node from the table.
        does not try to change anything in the node itself or its neighbors, however it does free up the node location
        in the table
        :param node_key:
        """
        raise NotImplemented("this is an abstract class")

    def _remove_node_from_table_without_affecting_the_node(self, node_key):
        """
        calls _remove_node_from_table_without_affecting_the_node_helper
        and notifies lower tables that this table size has changed.

        :param node_key:
        """
        self._remove_node_from_table_without_affecting_the_node_helper(node_key)

        # now notify all bottom tables that their table_starting_index has decreased
        if self.next_table is not TableAbstract.NO_NEXT_TABLE:
            self.next_table.decrease_starting_node_index()

    def delete_node(self, node_key):
        # check that the node belongs to this table
        # assumes that the layers are correct
        node_to_remove = self.get_node_by_key(node_key)
        assert node_to_remove.get_table_number() == self.table_number

        self.key_of_node_currently_being_removed_from_table = node_key

        node_to_remove.destructor()
        self._remove_node_from_table_without_affecting_the_node(node_key)

        self.key_of_node_currently_being_removed_from_table = TableAbstract.NO_NODE_IS_CURRENTLY_BEING_REMOVED

    def claim_node_as_your_own(self, node_object):
        """
        notifies the current table manager of the node that the node should be removed from it
        and adds the node to itself
        :param node_object:
        """
        current_node_table_manager = node_object.get_table_manager()
        _, node_key = node_object.get_location()
        current_node_table_manager.get_notified_node_wants_to_remove_itself_from_table(node_key)
        self.add_node_to_table(node_object)

    def move_node_to_new_table(self, node_key, table_to_move_node_to):
        node_to_relocate = self.get_node_by_key(node_key)
        node_to_relocate.move_node_to_new_table(table_to_move_node_to)


class TableDoesntSupportsDeletion(TableAbstract):
    def __init__(self, table_number, previous_table, next_table):
        super().__init__(table_number, previous_table, next_table)
        self.nodes = []

    def create_table_below_of_same_type(self):
        assert self.next_table == TableAbstract.NO_NEXT_TABLE

        table_to_return = TableDoesntSupportsDeletion(self.table_number + 1, self, TableAbstract.NO_NEXT_TABLE)
        self.next_table = table_to_return

        return table_to_return

    def get_number_of_nodes_in_table(self):
        return len(self.nodes)

    def _add_node_to_table_helper(self, node):
        self.nodes.append(node)
        return len(self.nodes) - 1

    def get_node_by_key(self, node_key):
        return self.nodes[node_key]


class TableSupportsDeletion(TableAbstract):
    def __init__(self, table_number, previous_table, next_table):
        super().__init__(table_number, previous_table, next_table)
        self.nodes = {}
        self.number_of_nodes = 0

    def create_table_below_of_same_type(self):
        assert self.next_table == TableAbstract.NO_NEXT_TABLE

        table_to_return = TableSupportsDeletion(self.table_number + 1, self, TableAbstract.NO_NEXT_TABLE)
        self.next_table = table_to_return

        return table_to_return

    def get_number_of_nodes_in_table(self):
        return self.number_of_nodes

    def _add_node_to_table_helper(self, node):
        new_key_for_node = self.number_of_nodes
        self.nodes[new_key_for_node] = node
        self.number_of_nodes += 1
        return new_key_for_node

    def get_node_by_key(self, node_key):
        return self.nodes[node_key]