class ARNetwork:
    def __init__(self, network):
        number_of_layers_in_network = len(network)
        # will probably be converted into a vector
        self.layers_tables = []

        for i in range(number_of_layers_in_network):
            tables_for_this_layer = [ARTable(0,
                                             ARTable.NO_PREVIOUS_TABLE,
                                             ARTable.NO_NEXT_TABLE)]

            for _ in range(4):
                tables_for_this_layer.append(tables_for_this_layer[-1].create_table_below())
            self.layers_tables.append(tables_for_this_layer)

        # TODO go over all nodes in the network and add them
        #  to table 5 (the unprocessed nodes) in their corresponding layers
        pass

    @staticmethod
    def type_to_number_of_map(type_of_node):
        """
        :param type_of_node: (pos,inc), (pos,dec), (neg,inc), (neg,dec), (unprocessed)
        :return: the number of table corresponding to the type given in the list of 5 tables
        """
        return [('pos', 'inc'), ('pos', 'dec'), ('neg', 'inc'), ('neg', 'dec'), 'unprocessed'].index(type_of_node)

