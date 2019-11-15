from second_try.Node import Node, ARNode


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

        self.previous_table = previous_table  # table above
        self.next_table = next_table  # table below

        # this would help us make sure that moving nodes between tables would never be done without notifying the
        # current parent table
        self.key_of_node_currently_being_removed_from_table = TableAbstract.NO_NODE_IS_CURRENTLY_BEING_REMOVED

    def create_table_below_of_same_type(self):
        """
        :return: the table created
        """
        raise NotImplemented("this is an abstract class")

    def get_arguments_to_create_table_below(self):
        return self.table_number + 1, self, TableAbstract.NO_NEXT_TABLE

    ######## might not need it
    def set_next_table(self, table, set_given_table_previous_table_as_this_table):
        """
        :param table:
        :param set_given_table_previous_table_as_this_table: if true would set the given table previous table to
        be this table. i.e. it would double link the tables
        """
        if self.next_table != TableAbstract.NO_NEXT_TABLE:
            raise Exception("next table is already set")

        self.next_table = table
        if set_given_table_previous_table_as_this_table:
            # to avoid infinite loop set_given_table_next_table_as_this_table would be false
            table.set_previous_table(self, False)

    ######## might not need it
    def set_previous_table(self, table, set_given_table_next_table_as_this_table):
        """
        :param table:
        :param set_given_table_next_table_as_this_table: if true would set the given table next table to
        be this table. i.e. it would double link the tables
        """
        if self.previous_table != TableAbstract.NO_NEXT_TABLE:
            raise Exception("previous table is already set")

        self.next_table = table
        if set_given_table_next_table_as_this_table:
            # to avoid infinite loop set_given_table_previous_table_as_this_table would be false
            table.set_next_table(self, False)

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

    def get_node_by_key(self, node_key):
        raise NotImplemented("this is an abstract class")

    def get_iterator_for_all_nodes(self):
        raise NotImplemented("this is an abstract class")

    def _reset_key_of_node_currently_being_removed_from_table(self):
        self.key_of_node_currently_being_removed_from_table = TableAbstract.NO_NODE_IS_CURRENTLY_BEING_REMOVED

    def get_notified_node_is_being_removed_from_table(self, node_key):
        """
        notifies this table that the given node is currently being removed from it
        :param node_key:
        """
        if self.key_of_node_currently_being_removed_from_table == node_key:
            # we are aware that this node is currently being removed
            return

        # else simply remove the node from the table. the one who changes the node values should take responsibility
        # for cleaning after the node.
        self._remove_node_from_table_without_affecting_the_node(node_key)

    def _remove_node_from_table_without_affecting_the_node(self, node_key):
        """
        removes the node from table without affecting the node at all
        notifies lower tables that this table size has changed.
        :param node_key:
        """
        raise NotImplemented("this is an abstract class")

    def remove_node_from_table_and_relocate_to_other_table(self, node_key, new_table_manager):
        """
        :param node_key:
        :param new_table_manager:
        :return: the new node key in the table it was moved to
        """
        raise NotImplemented("this is an abstract class")

    def _add_node_to_table_without_checking(self, node):
        """
        this helper function would be implemented by the subclasses
        it simply adds the node to the table and returns the key of the new node.
        it does not check or change anything about the node
        :param node:
        :return the key of the node inserted
        """
        raise NotImplemented("this is an abstract class")

    def create_new_node_and_add_to_table(self,
                                         number_of_tables_in_previous_layer,
                                         number_of_tables_in_next_layer):
        """
        :param number_of_tables_in_previous_layer:
        :param number_of_tables_in_next_layer:
        :return: the node created
        """
        new_node = Node(number_of_tables_in_previous_layer,
                        number_of_tables_in_next_layer,
                        -1, -1)

        node_key = self._add_node_to_table_without_checking(new_node)
        new_node.set_new_location(self.table_number, node_key)

        return new_node

    def add_existing_node_to_table(self, previous_table_manager, node):
        """
        notifies the previous_table_manager that its node is being removed from it, and adds it to this table
        :param previous_table_manager: the current table manager of the given node
        :param node:
        :return: the new key of the node
        """
        previous_table_manager.get_notified_node_is_being_removed_from_table(node.get_key_in_table())

        if self.get_number_of_nodes_in_table() == 0:
            # the table is currently empty, use the initialize_table_starting_index_based_on_previous_tables to
            # initialize its table_starting_index
            self.initialize_table_starting_index_based_on_previous_tables()

        previous_location = node.get_location()

        new_node_key = self._add_node_to_table_without_checking(node)

        # change the inserted node location_data so that its table number and index would correspond to its new location
        node.set_new_location(self.table_number, new_node_key)

        node.notify_all_neighbors_that_my_location_changed(previous_location)

        # now notify all bottom tables that their table_starting_index has increased
        if self.next_table is not TableAbstract.NO_NEXT_TABLE:
            self.next_table.increase_starting_node_index()

        return new_node_key

    def delete_node(self, node_key):
        # check that the node belongs to this table
        # assumes that the layers are correct
        node_to_remove = self.get_node_by_key(node_key)
        assert node_to_remove.get_table_number() == self.table_number

        node_to_remove.destructor()
        self._remove_node_from_table_without_affecting_the_node(node_key)


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

    def _add_node_to_table_without_checking(self, node):
        # from assumption (4) we need to insert it to the end of the table
        self.nodes.append(node)
        return len(self.nodes) - 1

    def add_existing_node_to_table(self, previous_table_manager, node):
        """
        override the super method so that the node which was inserted to the table would be set in stone.
        it does that since it was added to a table which does not support deletion
        """
        new_node_key = super().add_existing_node_to_table(previous_table_manager, node)
        node.set_in_stone()
        return new_node_key

    def get_node_by_key(self, node_key):
        return self.nodes[node_key]


class TableSupportsDeletion(TableAbstract):
    def __init__(self, table_number, previous_table, next_table):
        super().__init__(table_number, previous_table, next_table)
        self.nodes = {}
        self.number_of_nodes = 0

    def create_table_below_of_same_type(self):
        assert self.next_table == TableAbstract.NO_NEXT_TABLE

        table_to_return = TableSupportsDeletion(*self.get_arguments_to_create_table_below())
        self.next_table = table_to_return

        return table_to_return

    def get_iterator_for_all_nodes(self):
        for node in self.nodes:
            yield node

    def get_number_of_nodes_in_table(self):
        return self.number_of_nodes

    def _add_node_to_table_without_checking(self, node):
        new_key_for_node = self.number_of_nodes
        self.nodes[new_key_for_node] = node
        self.number_of_nodes += 1
        return new_key_for_node

    def get_node_by_key(self, node_key):
        return self.nodes[node_key]

    def _remove_node_from_table_without_affecting_the_node(self, node_key):
        """
        removes the node from table without affecting the node at all
        notifies lower tables that this table size has changed.
        :param node_key:
        """
        del self.nodes[node_key]

        # now notify all bottom tables that their table_starting_index has decreased
        if self.next_table is not TableAbstract.NO_NEXT_TABLE:
            self.next_table.decrease_starting_node_index()

    def remove_node_from_table_and_relocate_to_other_table(self, node_key, new_table_manager):
        node_to_relocate = self.get_node_by_key(node_key)
        node_to_relocate.check_if_killed_and_raise_error_if_is()

        self.key_of_node_currently_being_removed_from_table = node_key

        self._remove_node_from_table_without_affecting_the_node(node_key)
        new_node_key = new_table_manager.add_existing_node_to_table(node_to_relocate)

        self._reset_key_of_node_currently_being_removed_from_table()

        return new_node_key


class ARNodeTable(TableSupportsDeletion):
    def get_iterator_for_all_nodes(self):
        for node in self.nodes:
            yield node

    def create_new_node_and_add_to_table(self,
                                         number_of_tables_in_previous_layer,
                                         number_of_tables_in_next_layer):
        raise NotImplemented("this class can only contain arnodes")

    def create_new_arnode_and_add_to_table(self, starting_nodes):
        """

        :param starting_nodes:
        :return: the arnode created
        """
        new_node = ARNode(starting_nodes, -1, -1)

        node_key = self._add_node_to_table_without_checking(new_node)
        new_node.set_new_location(self.table_number, node_key)

        return new_node

    def split_arnode(self, arnodes_to_split,
                     partition_of_arnode_inner_nodes,
                     function_to_calculate_merger_of_incoming_edges,
                     function_to_calculate_merger_of_outgoing_edges
                     ):
        """
        :param arnodes_to_split:
        :param partition_of_arnode_inner_nodes: a list of lists which would be a valid partition of the
        arnode inner nodes.
        each sub list would contain a list of nodes references all of which are currently owned by
        the given arnodes_to_split

        those functions would be used to calculate the edges of each resulting arnode
        :param function_to_calculate_merger_of_incoming_edges:
        :param function_to_calculate_merger_of_outgoing_edges:

        removes the arnode from the table its in and inserts the new arnodes created
        """
        # maybe add a function to check that the partition is valid

        if arnodes_to_split.get_activation_status() != ARNode.FULLY_ACTIVATED_STATUS:
            raise Exception("can not split a non fully activated arnode")

        # before continuing, delete the arnode that needs to be split
        # this would also reset the nodes owner arnode
        arnodes_to_split.destructor()

        for node_list in partition_of_arnode_inner_nodes:
            # start node with bogus arguments and then add it to the table_manager which would give the node
            # real arguments
            new_arnode = self.create_new_arnode_and_add_to_table(node_list)
            new_arnode.forward_activate_arnode(function_to_calculate_merger_of_outgoing_edges)
            new_arnode.fully_activate_arnode_and_recalculate_incoming_edges(
                function_to_calculate_merger_of_incoming_edges)

    def merge_two_arnodes(self,
                          arnode1,
                          arnode2,
                          function_to_calculate_merger_of_incoming_edges,
                          function_to_calculate_merger_of_outgoing_edges):
        """
        this method merges the two arnodes given into a single arnode.
        the merged arnode would contain all the inner nodes that both arnodes contained.

        the 2 arnodes given are killed - i.e. they are removed from their neighbors and no action can be preformed on
        them from here on out.


        :param arnode1: a fully activated arnode
        :param arnode2: a fully activated arnode

        those functions would be used to calculate the edges of each resulting arnode
        :param function_to_calculate_merger_of_incoming_edges:
        :param function_to_calculate_merger_of_outgoing_edges:
        :return: the new merged arnode
        """
        for arnode in [arnode1, arnode2]:
            if arnode.get_activation_status() != ARNode.FULLY_ACTIVATED_STATUS:
                raise Exception("can not merge a non fully activated arnode")

        # from assumption (2) both arnodes have the same table_manager
        inner_nodes_for_new_arnode = arnode1.inner_nodes.union(arnode2.inner_nodes)

        # before continuing, delete the arnodes that needs to be merged
        # this would also reset the nodes owner arnode
        arnode1.destructor()
        arnode2.destructor()

        new_arnode = self.create_new_arnode_and_add_to_table(inner_nodes_for_new_arnode)
        new_arnode.forward_activate_arnode(function_to_calculate_merger_of_outgoing_edges)
        new_arnode.fully_activate_arnode_and_recalculate_incoming_edges(function_to_calculate_merger_of_incoming_edges)
