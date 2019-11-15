from second_try.Table import *


class Layer:
    NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION = 4

    INDEX_OF_POS_INC_TABLE = 0
    INDEX_OF_POS_DEC_TABLE = 1
    INDEX_OF_NEG_INC_TABLE = 2
    INDEX_OF_NEG_DEC_TABLE = 3

    # the unprocessed_table would be added after all the tables which do not support deletion
    INDEX_OF_UNPROCESSED_TABLE = NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION

    def __init__(self):
        # to preserve assumption (1) and (2)
        self.regular_node_tables = []
        self.arnode_tables = []

        # first initialize the regular_node_tables
        self.regular_node_tables.append(
            TableDoesntSupportsDeletion(0, TableAbstract.NO_PREVIOUS_TABLE, TableAbstract.NO_NEXT_TABLE))
        for i in range(1, Layer.NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION):
            self.regular_node_tables.append(self.regular_node_tables[i - 1].create_table_below_of_same_type())

        # now create the (unprocessed) table
        unprocessed_table = TableSupportsDeletion(*self.regular_node_tables[-1].get_arguments_to_create_table_below())
        self.regular_node_tables.append(unprocessed_table)

        # now initialize the arnode_tables
        self.arnode_tables.append(
            ARNodeTable(0, TableAbstract.NO_PREVIOUS_TABLE, TableAbstract.NO_NEXT_TABLE))
        for i in range(1, Layer.NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION):
            self.arnode_tables.append(self.arnode_tables[i - 1].create_table_below_of_same_type())

    @staticmethod
    def type_to_number_of_map(type_of_node):
        """
        :param type_of_node: (pos,inc), (pos,dec), (neg,inc), (neg,dec), (unprocessed)
        :return: the number of table corresponding to the type given in the list of 5 tables
        """
        return [('pos', 'inc'), ('pos', 'dec'), ('neg', 'inc'), ('neg', 'dec'), 'unprocessed'].index(type_of_node)

    def create_new_node(self,
                        number_of_tables_in_previous_layer,
                        number_of_tables_in_next_layer):
        """
        :return: creates a new node and returns it location. i.e. table number and key in table
        """
        # when new nodes are created they are inserted into the unprocessed table
        new_node = self.regular_node_tables[Layer.INDEX_OF_UNPROCESSED_TABLE].create_new_node_and_add_to_table(
            number_of_tables_in_previous_layer,
            number_of_tables_in_next_layer)

        return new_node.get_location()

    def move_unprocessed_node_to_table(self, node_key_in_unprocessed_table, index_of_table_to_move_to):
        """

        :param node_key_in_unprocessed_table:
        :param index_of_table_to_move_to: one of
        INDEX_OF_POS_INC_TABLE
        INDEX_OF_POS_DEC_TABLE
        INDEX_OF_NEG_INC_TABLE
        INDEX_OF_NEG_DEC_TABLE

        it moves the node into the given table. it then creates a corresponding arnode for the node
        :return: the location of the arnode created
        """
        unprocessed_table = self.regular_node_tables[Layer.INDEX_OF_UNPROCESSED_TABLE]
        table_to_move_to = self.regular_node_tables[index_of_table_to_move_to]

        new_node_key = unprocessed_table.remove_node_from_table_and_relocate_to_other_table(
            node_key_in_unprocessed_table,
            table_to_move_to)

        node = table_to_move_to.get_node_by_key(new_node_key)

        # now create a corresponding arnode for the node
        new_arnode = self.arnode_tables[index_of_table_to_move_to].create_new_arnode_and_add_to_table([node])

        # finally, return the location of the arnode created
        return new_arnode.get_location()

    def move_unprocessed_node_to_table_by_function(self, node_key_in_unprocessed_table,
                                                   function_to_decide_which_table_to_move_node_to):
        """

        :param node_key_in_unprocessed_table:
        :param function_to_decide_which_table_to_move_node_to: the function returns the index_of_table_to_move_to
        as should be given to the move_unprocessed_node_to_table method

        :return: the location of the arnode created
        """
        unprocessed_table = self.regular_node_tables[Layer.INDEX_OF_UNPROCESSED_TABLE]
        node = unprocessed_table.get_node_by_key(node_key_in_unprocessed_table)

        index_of_table_to_move_to = function_to_decide_which_table_to_move_node_to(node)

        return self.move_unprocessed_node_to_table(node_key_in_unprocessed_table, index_of_table_to_move_to)

    def preprocess_entire_layer(self, function_to_decide_which_table_to_move_node_to):
        unprocessed_table = self.regular_node_tables[Layer.INDEX_OF_UNPROCESSED_TABLE]
        for node in unprocessed_table.get_iterator_for_all_nodes():
            node_key_in_unprocessed_table = node.get_key_in_table()
            index_of_table_to_move_to = function_to_decide_which_table_to_move_node_to(node)
            self.move_unprocessed_node_to_table(node_key_in_unprocessed_table, index_of_table_to_move_to)

    ################################### create more functions to enable finer control over activation
    def forward_activate_arnode_table(self,
                                      table_index,
                                      function_to_calculate_merger_of_outgoing_edges):
        arnode_iterator = self.arnode_tables[table_index].get_iterator_for_all_nodes()
        for arnode in arnode_iterator:
            if arnode.get_activation_status() != ARNode.FULLY_ACTIVATED_STATUS:
                arnode.forward_activate_arnode(function_to_calculate_merger_of_outgoing_edges)

    def fully_activate_layer_by_recalculating_incoming_edges(self,
                                                             table_index,
                                                             function_to_calculate_merger_of_incoming_edges):
        """
        if the previous layer was entirely forward activated but you want ot recalculate the incoming edges to
        this layer arnodes, use this function
        :param table_index:
        :param function_to_calculate_merger_of_incoming_edges:
        :return:
        """
        arnode_iterator = self.arnode_tables[table_index].get_iterator_for_all_nodes()
        for arnode in arnode_iterator:
            if arnode.get_activation_status() != ARNode.FULLY_ACTIVATED_STATUS:
                arnode.fully_activate_arnode_and_recalculate_incoming_edges(
                    function_to_calculate_merger_of_incoming_edges)

    def fully_activate_layer_without_changing_incoming_edges(self,
                                                             table_index,
                                                             check_validity_of_activation=True):
        """
        if the previous layer was entirely forward activated and you do not want ot recalculate the incoming edges to
        this layer arnodes, use this function
        :param table_index:
        :param check_validity_of_activation:
        :return:
        """
        arnode_iterator = self.arnode_tables[table_index].get_iterator_for_all_nodes()
        for arnode in arnode_iterator:
            if arnode.get_activation_status() != ARNode.FULLY_ACTIVATED_STATUS:
                arnode.fully_activate_arnode_without_changing_incoming_edges(check_validity_of_activation)
