from src.Tables.Table import AbstractTable


class TableSupportsDeletion(AbstractTable):
    def __init__(self, layer_number, table_number, layer_is_inner, global_data_manager):
        super().__init__(layer_number, table_number, layer_is_inner, global_data_manager)
        self.nodes = {}
        self.key_for_new_node = 0  # this would serve as the key of the next node that would be added to the table
        # later if someone could fix the id manager to support infinite numbers of ids, or to at least support reaching
        # the end of the possible ids range, then we could use this id manager to make sure that the keys wont increase
        # too much

    def create_table_below_of_same_type(self):
        table_to_return = TableSupportsDeletion(*self.get_arguments_to_create_table_below())

        return table_to_return

    def get_iterator_for_all_nodes(self):
        for key in self.nodes:
            yield self.nodes[key]

    def get_iterator_for_all_keys(self):
        for key in self.nodes:
            yield key

    def get_number_of_nodes_in_table(self):
        return len(self.nodes)

    def _add_node_to_table_without_checking(self, node):
        new_key_for_node = self.key_for_new_node
        self.nodes[new_key_for_node] = node
        self.key_for_new_node += 1
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

    def remove_node_from_table_and_relocate_to_other_table(self, node_key, new_table_manager):
        node_to_relocate = self.get_node_by_key(node_key)
        node_to_relocate.check_if_killed_and_raise_error_if_is()

        self.key_of_node_currently_being_removed_from_table = node_key

        self._remove_node_from_table_without_affecting_the_node(node_key)
        new_node_key = new_table_manager.add_existing_node_to_table(self, node_to_relocate)

        self._reset_key_of_node_currently_being_removed_from_table()

        return new_node_key
