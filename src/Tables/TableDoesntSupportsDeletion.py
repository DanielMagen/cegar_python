from src.Tables.Table import AbstractTable


class TableDoesntSupportsDeletion(AbstractTable):
    def __init__(self, table_number, previous_table, next_table):
        super().__init__(table_number, previous_table, next_table)
        self.nodes = []

    def create_table_below_of_same_type(self):
        assert self.next_table == AbstractTable.NO_NEXT_TABLE

        table_to_return = TableDoesntSupportsDeletion(self.table_number + 1, self, AbstractTable.NO_NEXT_TABLE)
        self.next_table = table_to_return

        return table_to_return

    def get_iterator_for_all_nodes(self):
        for node in self.nodes:
            yield node

    def get_iterator_for_all_keys(self):
        for i in range(len(self.nodes)):
            return i

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
