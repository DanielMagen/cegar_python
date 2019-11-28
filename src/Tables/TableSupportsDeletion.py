from src.Tables.Table import AbstractTable


class TableSupportsDeletion(AbstractTable):
    def __init__(self, table_number, previous_table, next_table):
        super().__init__(table_number, previous_table, next_table)
        self.nodes = {}
        self.number_of_nodes = 0

    def create_table_below_of_same_type(self):
        assert self.next_table == AbstractTable.NO_NEXT_TABLE

        table_to_return = TableSupportsDeletion(*self.get_arguments_to_create_table_below())
        self.next_table = table_to_return

        return table_to_return

    def get_iterator_for_all_nodes(self):
        for node in self.nodes:
            yield node

    def get_iterator_for_all_keys(self):
        for key in self.nodes:
            return key

    def get_number_of_nodes_in_table(self):
        return self.number_of_nodes

    # maybe add an id system so that the ids won't increase too much
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
        if self.next_table is not AbstractTable.NO_NEXT_TABLE:
            self.next_table.decrease_starting_node_index()

    def remove_node_from_table_and_relocate_to_other_table(self, node_key, new_table_manager):
        node_to_relocate = self.get_node_by_key(node_key)
        node_to_relocate.check_if_killed_and_raise_error_if_is()

        self.key_of_node_currently_being_removed_from_table = node_key

        self._remove_node_from_table_without_affecting_the_node(node_key)
        new_node_key = new_table_manager.add_existing_node_to_table(node_to_relocate)

        self._reset_key_of_node_currently_being_removed_from_table()

        return new_node_key
