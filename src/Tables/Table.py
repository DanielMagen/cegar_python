from src.Nodes.Node import Node


class AbstractTable:
    NO_NODE_IS_CURRENTLY_BEING_REMOVED = None

    def __init__(self, layer_number, table_number, layer_is_inner, global_data_manager):
        """
        :param table_number: the number of the table in the overall table order.
        :param layer_is_inner: a boolean which should be true if the layer this table resides in is an inner layer
        (not the first or the last layer)
        """
        self.layer_number = layer_number
        self.table_number = table_number

        self.layer_is_inner = layer_is_inner

        self.global_data_manager = global_data_manager

        # this would help us make sure that moving nodes between tables would never be done without notifying the
        # current parent table
        self.key_of_node_currently_being_removed_from_table = AbstractTable.NO_NODE_IS_CURRENTLY_BEING_REMOVED

    def get_arguments_to_create_table_below(self):
        """
        :return: a tuple of arguments needed to create a table below this table
        """
        return self.layer_number, self.table_number + 1, self.layer_is_inner, self.global_data_manager

    def create_table_below_of_same_type(self):
        """
        creates a new table which would have a table_number bigger by one
        :return: the table created
        """
        raise NotImplemented("this is an abstract class")

    def get_number_of_nodes_in_table(self):
        raise NotImplemented("this is an abstract class")

    def get_node_by_key(self, node_key):
        raise NotImplemented("this is an abstract class")

    def get_iterator_for_all_nodes(self):
        raise NotImplemented("this is an abstract class")

    def get_iterator_for_all_keys(self):
        raise NotImplemented("this is an abstract class")

    def get_list_of_all_keys(self):
        return list(self.get_iterator_for_all_keys())

    def get_list_of_all_nodes(self):
        return list(self.get_iterator_for_all_nodes())

    def _reset_key_of_node_currently_being_removed_from_table(self):
        self.key_of_node_currently_being_removed_from_table = AbstractTable.NO_NODE_IS_CURRENTLY_BEING_REMOVED

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
        :param node_key:
        """
        raise NotImplementedError("this is an abstract class")

    def remove_node_from_table_and_relocate_to_other_table(self, node_key, new_table_manager):
        """
        :param node_key:
        :param new_table_manager:
        :return: the new node key in the table it was moved to
        """
        raise NotImplementedError("this is an abstract class")

    def _add_node_to_table_without_checking(self, node):
        """
        this helper function would be implemented by the subclasses
        it simply adds the node to the table and returns the key of the new node.
        it does not check or change anything about the node
        :param node:
        :return the key of the node inserted
        """
        raise NotImplementedError("this is an abstract class")

    def _get_ids_for_new_node(self, global_data_manager):
        """
        :param global_data_manager:
        :return: a pair of global_incoming_id, global_outgoing_id for a new node,
        those ids would be extracted from the given global_data_manager
        """
        global_incoming_id = global_data_manager.get_new_id()
        global_outgoing_id = global_incoming_id
        if self.layer_is_inner:
            global_outgoing_id = global_data_manager.get_new_id()

        return global_incoming_id, global_outgoing_id

    def create_new_node_and_add_to_table(self,
                                         number_of_tables_in_previous_layer,
                                         number_of_tables_in_next_layer,
                                         bias_for_node,
                                         global_data_manager):
        """
        :param bias_for_node:
        :param number_of_tables_in_previous_layer:
        :param number_of_tables_in_next_layer:
        :param global_data_manager:
        :return: the node created
        """
        # we need to give the node a global id. we first check if the table is in an inner or and outer layer
        # if the table is in an inner layer the node needs 2 different ids otherwise it needs only 1
        global_incoming_id, global_outgoing_id = self._get_ids_for_new_node(global_data_manager)

        new_node = Node(number_of_tables_in_previous_layer,
                        number_of_tables_in_next_layer,
                        self.layer_number,
                        Node.NO_TABLE_NUMBER, Node.NO_KEY_IN_TABLE,
                        bias_for_node,
                        global_incoming_id, global_outgoing_id, global_data_manager)

        node_key = self._add_node_to_table_without_checking(new_node)
        # change the inserted node location_data so that its table number and index would correspond to its new location
        # no need to notify_neighbors since this node has no neighbors since it was just created
        new_node.set_new_location(self.table_number, node_key, notify_neighbors_that_location_changed=False)

        return new_node

    def add_existing_node_to_table(self, previous_table_manager, node):
        """
        notifies the previous_table_manager that its node is being removed from it, and adds it to this table
        :param previous_table_manager: the current table manager of the given node
        :param node:
        :return: the new key of the node
        """
        # first remove the node from its previous table
        previous_table_manager.get_notified_node_is_being_removed_from_table(node.get_key_in_table())

        new_node_key = self._add_node_to_table_without_checking(node)

        # change the inserted node location_data so that its table number and index would correspond to its new location
        node.set_new_location(self.table_number, new_node_key, notify_neighbors_that_location_changed=True)

        return new_node_key

    def delete_node(self, node_key):
        """
        deletes the given node from the table
        notifies lower tables that this table size has changed.
        :param node_key:
        """
        # check that the node belongs to this table
        # assumes that the layers are correct
        node_to_remove = self.get_node_by_key(node_key)
        assert node_to_remove.get_table_number() == self.table_number

        node_to_remove.destructor()
        self._remove_node_from_table_without_affecting_the_node(node_key)

    def add_or_edit_neighbor_to_node(self, node_key, direction_of_connection, connection_data):
        node_to_add_connection_to = self.get_node_by_key(node_key)
        node_to_add_connection_to.add_or_edit_neighbor(direction_of_connection, connection_data)

    def add_or_edit_connection_to_node_by_bulk(self, node_key, direction_of_connection, list_of_connection_data):
        node_to_add_connection_to = self.get_node_by_key(node_key)
        node_to_add_connection_to.add_or_edit_neighbors_by_bulk(direction_of_connection, list_of_connection_data)

    def calculate_equation_and_constraint_for_all_nodes_in_table(self):
        for node in self.get_iterator_for_all_nodes():
            node.calculate_equation_and_constraint()

    def calculate_equation_and_constraint_for_a_specific_node(self, key_in_table):
        self.get_node_by_key(key_in_table).calculate_equation_and_constraint()

    def __str__(self):
        to_return = ''
        to_return += f'table number {self.table_number}'
        to_return += '\n'
        for node in self.get_iterator_for_all_nodes():
            to_return += str(node)
            to_return += '\n'

        return to_return
