from src.Tables.Table import AbstractTable


class TableDoesntSupportsDeletion(AbstractTable):
    def __init__(self, table_number, layer_is_inner, global_data_manager):
        super().__init__(table_number, layer_is_inner, global_data_manager)
        self.nodes = []

    def create_table_below_of_same_type(self):
        table_to_return = TableDoesntSupportsDeletion(*self.get_arguments_to_create_table_below())

        return table_to_return

    def get_iterator_for_all_nodes(self):
        for node in self.nodes:
            yield node

    def get_iterator_for_all_keys(self):
        for i in range(len(self.nodes)):
            yield i

    def get_list_of_all_keys(self):
        return list(self.get_iterator_for_all_keys())

    def get_number_of_nodes_in_table(self):
        return len(self.nodes)

    def _add_node_to_table_without_checking(self, node):
        # from assumption (4) we need to insert it to the end of the table
        self.nodes.append(node)
        # the key of the node is simply its index in the table
        return len(self.nodes) - 1

    def create_new_node_and_add_to_table(self,
                                         number_of_tables_in_previous_layer,
                                         number_of_tables_in_next_layer,
                                         node_bias,
                                         global_data_manager):
        """
        :param node_bias:
        :param number_of_tables_in_previous_layer:
        :param number_of_tables_in_next_layer:
        :param global_data_manager:
        :return: the node created
        """
        new_node = super().create_new_node_and_add_to_table(number_of_tables_in_previous_layer,
                                                            number_of_tables_in_next_layer,
                                                            node_bias,
                                                            global_data_manager)
        new_node.set_in_stone()
        return new_node

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
