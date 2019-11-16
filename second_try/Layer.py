from second_try.Table import *
from second_try.NodeEdges import *


class Layer:
    NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION = 4

    INDEX_OF_POS_INC_TABLE = 0
    INDEX_OF_POS_DEC_TABLE = 1
    INDEX_OF_NEG_INC_TABLE = 2
    INDEX_OF_NEG_DEC_TABLE = 3

    # the unprocessed_table would be added after all the tables which do not support deletion
    INDEX_OF_UNPROCESSED_TABLE = NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION

    def __init__(self, number_of_tables_in_previous_layer, number_of_tables_in_next_layer):
        # to preserve assumption (1) and (2)
        self.regular_node_tables = []
        self.arnode_tables = []

        self.number_of_tables_in_previous_layer = number_of_tables_in_previous_layer
        self.number_of_tables_in_next_layer = number_of_tables_in_next_layer

        # first initialize the regular_node_tables
        # to preserve assumption (2) the first 4 tables must have indices of 0-3 in order, as such give the first table
        # an index of 0 and the create_table_below_of_same_type function of the table class would take care of
        # increasing the index by 1 each turn
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

    def create_new_node(self):
        """
        :return: creates a new node and returns it location. i.e. table number and key in table
        """
        # when new nodes are created they are inserted into the unprocessed table
        new_node = self.regular_node_tables[Layer.INDEX_OF_UNPROCESSED_TABLE].create_new_node_and_add_to_table(
            self.number_of_tables_in_previous_layer,
            self.number_of_tables_in_next_layer)

        return new_node.get_location()

    def split_unprocessed_node_to_tables(self, node_key_in_unprocessed_table):
        """
        :param node_key_in_unprocessed_table:
        would remove the the node from the unprocessed table and replace it with nodes in the
        other tables
        it assumes that all the nodes that this node is connected to by an outgoing connection have been preprocessed

        for each node it would insert into a regular table, it would create a corresponding arnode
        """
        unprocessed_table = self.regular_node_tables[Layer.INDEX_OF_UNPROCESSED_TABLE]
        node = unprocessed_table.get_node_by_key(node_key_in_unprocessed_table)

        if node.get_number_of_connections(Node.OUTGOING_EDGE_DIRECTION) == 0:
            # this node is the output node, simply move it to the POS_INC_TABLE
            table_to_move_to = self.regular_node_tables[Layer.INDEX_OF_POS_INC_TABLE]

            new_node_key = unprocessed_table.remove_node_from_table_and_relocate_to_other_table(
                node_key_in_unprocessed_table,
                table_to_move_to)

            node = table_to_move_to.get_node_by_key(new_node_key)

            # now create a corresponding arnode for the node
            new_arnode = self.arnode_tables[Layer.INDEX_OF_POS_INC_TABLE].create_new_arnode_and_add_to_table([node])
            return

        weight_location_in_data = NodeEdges.INDEX_OF_WEIGHT_IN_DATA

        data_for_nodes_we_are_pos_linked_to = []
        data_for_nodes_we_are_neg_linked_to = []

        for outgoing_edges_data in node.get_iterator_for_edges_data(Node.OUTGOING_EDGE_DIRECTION):
            weight_of_connection = outgoing_edges_data[weight_location_in_data]
            if weight_of_connection >= 0:
                data_for_nodes_we_are_pos_linked_to.append(outgoing_edges_data)
            else:
                data_for_nodes_we_are_neg_linked_to.append(outgoing_edges_data)

        # data_for_nodes_we_are_pos_inc_linked_to would be the list at location 0
        # data_for_nodes_we_are_pos_dec_linked_to would be the list at location 1
        # data_for_nodes_we_are_neg_inc_linked_to would be the list at location 2
        # data_for_nodes_we_are_neg_dec_linked_to would be the list at location 3
        split_data_by_types = [[] for _ in range(Layer.NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION)]

        # according to assumption (2) the table number would correspond to the type of nodes they contain
        table_number_location_in_data = NodeEdges.INDEX_OF_TABLE_NUMBER_IN_DATA
        inc_table_numbers = [Layer.INDEX_OF_POS_INC_TABLE, Layer.INDEX_OF_NEG_INC_TABLE]
        dec_table_numbers = [Layer.INDEX_OF_POS_DEC_TABLE, Layer.INDEX_OF_NEG_DEC_TABLE]

        for outgoing_edges_data in data_for_nodes_we_are_pos_linked_to:
            table_number = outgoing_edges_data[table_number_location_in_data]
            if table_number in inc_table_numbers:
                split_data_by_types[0].append(outgoing_edges_data)
            elif table_number in dec_table_numbers:
                split_data_by_types[1].append(outgoing_edges_data)
            else:
                raise Exception("some of the nodes that this node is connected to by an outgoing connection were not"
                                "preprocessed")

        for outgoing_edges_data in data_for_nodes_we_are_neg_linked_to:
            table_number = outgoing_edges_data[table_number_location_in_data]
            if table_number in inc_table_numbers:
                split_data_by_types[3].append(outgoing_edges_data)
            elif table_number in dec_table_numbers:
                split_data_by_types[2].append(outgoing_edges_data)
            else:
                raise Exception("some of the nodes that this node is connected to by an outgoing connection were not"
                                "preprocessed")

        # now create a new node for each list which isn't empty and insert the node in the right table
        nodes_created = [None for _ in range(Layer.NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION)]

        for i in range(len(split_data_by_types)):
            if len(split_data_by_types[i]) != 0:
                current_table = self.regular_node_tables[i]
                new_node = current_table.create_new_node_and_add_to_table(
                    self.number_of_tables_in_previous_layer,
                    self.number_of_tables_in_next_layer)

                nodes_created[i] = new_node

                # now add all outgoing edges to the node
                new_node_key = new_node.get_key_in_table()
                current_table.add_or_edit_connection_to_node_by_bulk(new_node_key, Node.OUTGOING_EDGE_DIRECTION,
                                                                     split_data_by_types[i],
                                                                     add_this_node_to_given_node_neighbors=True)
        # now add all the incoming edges to all the nodes created
        incoming_edges_data = node.get_a_list_of_all_incoming_connections_data(Node.INCOMING_EDGE_DIRECTION)
        for new_node in nodes_created:
            if new_node is not None:
                new_node_key = new_node.get_key_in_table()
                current_table.add_or_edit_connection_to_node_by_bulk(new_node_key, Node.INCOMING_EDGE_DIRECTION,
                                                                     incoming_edges_data,
                                                                     add_this_node_to_given_node_neighbors=True)

        # now delete the node from the unprocessed table
        unprocessed_table.delete_node(node.get_key_in_table())

        # now create an arnode for all the nodes created
        for i in range(len(nodes_created)):
            if nodes_created[i] is not None:
                self.arnode_tables[i].create_new_arnode_and_add_to_table([nodes_created[i]])

    def preprocess_entire_layer(self):
        unprocessed_table = self.regular_node_tables[Layer.INDEX_OF_UNPROCESSED_TABLE]
        for node_key in unprocessed_table.get_iterator_for_all_keys():
            self.split_unprocessed_node_to_tables(node_key)

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
