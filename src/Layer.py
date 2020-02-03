from src.Nodes.GlobalNode import GlobalNode
from src.NodeEdges import NodeEdges
from src.Tables.TableDoesntSupportsDeletion import TableDoesntSupportsDeletion
from src.Tables.ARNodeTable import *


class Layer:
    NO_POINTER_TO_ADJACENT_LAYER = None

    NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION = 4

    # from assumption (1) all layers have the same number of layers
    NUMBER_OF_OVERALL_TABLES = 5

    # can not change do to assumption (2)
    INDEX_OF_POS_INC_TABLE = 0
    INDEX_OF_POS_DEC_TABLE = 1
    INDEX_OF_NEG_INC_TABLE = 2
    INDEX_OF_NEG_DEC_TABLE = 3

    OVERALL_ARNODE_TABLES = [INDEX_OF_POS_INC_TABLE, INDEX_OF_POS_DEC_TABLE, INDEX_OF_NEG_INC_TABLE,
                             INDEX_OF_NEG_DEC_TABLE]

    # the unprocessed_table would be added after all the tables which do not support deletion
    INDEX_OF_UNPROCESSED_TABLE = NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION

    # those must be multiple of -1 of one another
    INCOMING_LAYER_DIRECTION = GlobalNode.INCOMING_EDGE_DIRECTION
    OUTGOING_LAYER_DIRECTION = GlobalNode.OUTGOING_EDGE_DIRECTION

    def __init__(self, layer_number, global_data_manager, pointer_to_previous_layer=NO_POINTER_TO_ADJACENT_LAYER,
                 pointer_to_next_layer=NO_POINTER_TO_ADJACENT_LAYER):
        """
        :param pointer_to_previous_layer:
        :param pointer_to_next_layer:
        """
        # to preserve assumption (1) and (2)
        self.layer_number = layer_number
        self.global_data_manager = global_data_manager
        self.regular_node_tables = []
        self.arnode_tables = []

        self.previous_layer = pointer_to_previous_layer
        self.next_layer = pointer_to_next_layer

        self.layer_is_inner = False
        self._set_is_inner()

        # initialize the regular_node_tables
        # to preserve assumption (2) the first 4 tables must have indices of 0-3 in order, as such give the first table
        # an index of 0 and the create_table_below_of_same_type function of the table class would take care of
        # increasing the index by 1 each turn
        self.regular_node_tables.append(
            TableDoesntSupportsDeletion(self.layer_number, 0, self.layer_is_inner, self.global_data_manager))
        for i in range(1, Layer.NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION):
            self.regular_node_tables.append(self.regular_node_tables[i - 1].create_table_below_of_same_type())

        # now create the (unprocessed) table
        unprocessed_table = TableSupportsDeletion(*self.regular_node_tables[-1].get_arguments_to_create_table_below())
        self.regular_node_tables.append(unprocessed_table)

        # now initialize the arnode_tables
        self.arnode_tables.append(ARNodeTable(self.layer_number, 0, self.layer_is_inner, self.global_data_manager))
        for i in range(1, Layer.NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION):
            self.arnode_tables.append(self.arnode_tables[i - 1].create_table_below_of_same_type())

    def set_previous_layer(self, pointer_to_previous_layer):
        self.previous_layer = pointer_to_previous_layer

    def set_next_layer(self, pointer_to_next_layer):
        self.next_layer = pointer_to_next_layer

    def _set_is_inner(self):
        if self.previous_layer == Layer.NO_POINTER_TO_ADJACENT_LAYER or \
                self.next_layer == Layer.NO_POINTER_TO_ADJACENT_LAYER:
            self.layer_is_inner = False
        else:
            self.layer_is_inner = True

    def create_next_layer(self):
        """
        :return: creates a new layer which would be this layer "next layer"
        it connects this layer to the next layer

        if the layer already has a pointer to the next layer, it raises an exception
        """
        if self.next_layer != Layer.NO_POINTER_TO_ADJACENT_LAYER:
            raise Exception("Layer already has a pointer to the next layer")

        new_layer = Layer(self.layer_number + 1, self.global_data_manager, pointer_to_previous_layer=self,
                          pointer_to_next_layer=Layer.NO_POINTER_TO_ADJACENT_LAYER)
        self.next_layer = new_layer

        # check if your'e still an inner layer, and if not change it
        self._set_is_inner()

        return new_layer

    def create_previous_layer(self):
        """
        :return: creates a new layer which would be this layer "previous layer"
        it connects this layer to the previous layer

        if the layer already has a pointer to the previous layer, it raises an exception
        """
        if self.previous_layer != Layer.NO_POINTER_TO_ADJACENT_LAYER:
            raise Exception("Layer already has a pointer to the previous layer")

        new_layer = Layer(self.layer_number - 1, self.global_data_manager,
                          pointer_to_previous_layer=Layer.NO_POINTER_TO_ADJACENT_LAYER,
                          pointer_to_next_layer=self)
        self.previous_layer = new_layer

        # check if your'e still an inner layer, and if not change it
        self._set_is_inner()

        return new_layer

    def create_new_node(self, bias_for_node):
        """
        :return: creates a new node in the unprocessed table (to preserve assumption (4)) and returns it.
        """
        # when new nodes are created they are inserted into the unprocessed table
        # from assumption (1) all layers have the same number of tables
        new_node = self.regular_node_tables[Layer.INDEX_OF_UNPROCESSED_TABLE].create_new_node_and_add_to_table(
            Layer.NUMBER_OF_OVERALL_TABLES,
            Layer.NUMBER_OF_OVERALL_TABLES,
            bias_for_node,
            self.global_data_manager)

        return new_node.get_key_in_table()

    def get_iterator_for_all_nodes_for_table(self, is_arnode, table_number):
        """
        :param is_arnode: a boolean, if true would search for the node in the arnode tables
        :param table_number:
        """
        tables = self.regular_node_tables
        if is_arnode:
            tables = self.arnode_tables

        return tables[table_number].get_iterator_for_all_nodes()

    def get_list_of_all_nodes_for_table(self, is_arnode, table_number):
        """
        :param is_arnode: a boolean, if true would search for the node in the arnode tables
        :param table_number:
        """
        tables = self.regular_node_tables
        if is_arnode:
            tables = self.arnode_tables

        return tables[table_number].get_list_of_all_nodes()

    def get_number_of_nodes_in_table(self, is_arnode, table_number):
        tables = self.regular_node_tables
        if is_arnode:
            tables = self.arnode_tables

        return tables[table_number].get_number_of_nodes_in_table()

    def get_unprocessed_node_by_key(self, key_of_node_in_unprocessed_table):
        return self.regular_node_tables[Layer.INDEX_OF_UNPROCESSED_TABLE].get_node_by_key(
            key_of_node_in_unprocessed_table)

    def _create_arnode_for_node(self, node):
        node_table = node.get_table_number()
        if node_table == Layer.INDEX_OF_UNPROCESSED_TABLE or node.check_if_location_can_be_changed():
            raise Exception("can not create an arnode for a node which is not set in stone")

        self.arnode_tables[node_table].create_new_arnode_and_add_to_table([node])

    def add_or_edit_neighbor_to_node_in_unprocessed_table(self, node_key, direction_of_connection,
                                                          key_of_node_in_unprocessed_table_of_connected_layer,
                                                          weight):
        """
        to preserve assumption (3) we only allow edges to be added to the nodes in the unprocessed table.
        to preserve assumption (5) we only allow edges to be added between this layer and one of its adjacent layers

        :param node_key:
        :param direction_of_connection:
        :param key_of_node_in_unprocessed_table_of_connected_layer:
        :param weight:
        """
        if direction_of_connection == Layer.INCOMING_LAYER_DIRECTION:
            adjacent_layer = self.previous_layer
        elif direction_of_connection == Layer.OUTGOING_LAYER_DIRECTION:
            adjacent_layer = self.next_layer
        else:
            raise ValueError("direction given is not valid")

        # now create the connection_data
        node_in_adjacent_layer = adjacent_layer.get_unprocessed_node_by_key(
            key_of_node_in_unprocessed_table_of_connected_layer)
        connection_data = [*node_in_adjacent_layer.get_location(), weight, node_in_adjacent_layer]

        # finally, connect between the 2 nodes
        node_to_add_connection_to = self.get_unprocessed_node_by_key(node_key)
        node_to_add_connection_to.add_or_edit_neighbor(direction_of_connection, connection_data)

    def add_or_edit_neighbors_to_node_in_unprocessed_table_by_bulk(self, node_key, direction_of_connection,
                                                                   list_of_pairs_of_keys_and_weights):
        """
        to preserve assumption (3) we only allow edges to be added to the nodes in the unprocessed table
        to preserve assumption (5) we only allow edges to be added between this layer and one of its adjacent layers

        :param node_key:
        :param direction_of_connection:
        :param list_of_pairs_of_keys_and_weights: a list of pairs of the form
        (key_of_node_in_unprocessed_table_of_connected_layer, weight)
        """
        if direction_of_connection == Layer.INCOMING_LAYER_DIRECTION:
            adjacent_layer = self.previous_layer
        elif direction_of_connection == Layer.OUTGOING_LAYER_DIRECTION:
            adjacent_layer = self.next_layer
        else:
            raise ValueError("direction given is not valid")

        # now create the list_of_connection_data
        list_of_connection_data = []
        for pair in list_of_pairs_of_keys_and_weights:
            key_of_node_in_unprocessed_table_of_connected_layer, weight = pair

            node_in_adjacent_layer = adjacent_layer.get_unprocessed_node_by_key(
                key_of_node_in_unprocessed_table_of_connected_layer)

            connection_data = [*node_in_adjacent_layer.get_location(), weight, node_in_adjacent_layer]

            list_of_connection_data.append(connection_data)

        node_to_add_connection_to = self.get_unprocessed_node_by_key(node_key)
        node_to_add_connection_to.add_or_edit_neighbors_by_bulk(direction_of_connection, list_of_connection_data)

    @staticmethod
    def get_split_edge_data_by_types(node):
        """
        this is the function that should be given to the split_unprocessed_node_to_tables function

        :param node:
        :return:
        we want to split a node into 4 types of nodes:
        pos-inc, pos-dec, neg-inc, neg-dec
        to do so we need to split the given node outgoing edges between those 4 new nodes we want to create
        this function returns a list of size 4 (NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION)
        so that list[i] would contain all the connection data for outgoing edges that should go to the node we will
        create in regular_node_tables[i].
        """
        data_for_nodes_we_are_pos_linked_to = []
        data_for_nodes_we_are_neg_linked_to = []

        for outgoing_edges_data in node.get_iterator_for_connections_data(GlobalNode.OUTGOING_EDGE_DIRECTION):
            weight_of_connection = outgoing_edges_data[NodeEdges.INDEX_OF_WEIGHT_IN_DATA]
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
                raise Exception("some of the nodes that this node is connected to by an outgoing connection were not "
                                "preprocessed")

        for outgoing_edges_data in data_for_nodes_we_are_neg_linked_to:
            table_number = outgoing_edges_data[table_number_location_in_data]
            if table_number in inc_table_numbers:
                split_data_by_types[3].append(outgoing_edges_data)
            elif table_number in dec_table_numbers:
                split_data_by_types[2].append(outgoing_edges_data)
            else:
                raise Exception("some of the nodes that this node is connected to by an outgoing connection were not "
                                "preprocessed")

        return split_data_by_types

    def split_unprocessed_node_to_tables(self,
                                         node_key_in_unprocessed_table,
                                         function_to_split_edges_data):
        """
        :param node_key_in_unprocessed_table:
        this method would remove the the node from the unprocessed table and replace it with nodes in the
        other tables
        it assumes that all the nodes that this node is connected to by an outgoing connection have been preprocessed
        and also that all the nodes that should be connected to this node by an incoming connection, have been
        connected to it (the node is going to die and in its stead 4 new nodes would appear)


        :param function_to_split_edges_data:
        we want to split a node into 4 types of nodes:
        pos-inc, pos-dec, neg-inc, neg-dec
        to do so we need to split the given node outgoing edges between those 4 new nodes we want to create
        this function would receive the node we wish to split and
        return a list of size 4 (NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION)
        so that list[i] would contain all the connection data for outgoing edges that should go to the node we will
        create in regular_node_tables[i].

        for each node it would insert into a regular table, it would create a corresponding arnode in the arnodes table
        """
        if not self.layer_is_inner:
            raise Exception("input or output layers nodes cannot be split, "
                            "call preprocess_entire_layer to prepare the layer for further actions")

        unprocessed_table = self.regular_node_tables[Layer.INDEX_OF_UNPROCESSED_TABLE]
        node = unprocessed_table.get_node_by_key(node_key_in_unprocessed_table)
        original_node_bias = node.get_node_bias()

        # before continuing, since the node is about to be removed, we first remove the node global variables,
        # including the node global id. we do so at this stage to create as little gaps as possible in the id manager
        node.remove_id_equation_and_constraint()

        edge_data_split_by_type = function_to_split_edges_data(node)

        # now create a new node for each list which isn't empty and insert the node in the right table
        # we wish this list to be of length NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION,
        # so a None value would indicate if a list is empty at a specific location
        # we do so that we would know what type each new node created belongs to
        nodes_created = [None for _ in range(Layer.NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION)]

        for i in range(len(edge_data_split_by_type)):
            if len(edge_data_split_by_type[i]) != 0:
                current_table = self.regular_node_tables[i]
                # from assumption (1) all layers have the same number of layers
                new_node = current_table.create_new_node_and_add_to_table(
                    Layer.NUMBER_OF_OVERALL_TABLES,
                    Layer.NUMBER_OF_OVERALL_TABLES,
                    original_node_bias,
                    self.global_data_manager)

                nodes_created[i] = new_node

                # now add all outgoing edges to the node
                new_node_key = new_node.get_key_in_table()
                current_table.add_or_edit_connection_to_node_by_bulk(new_node_key,
                                                                     GlobalNode.OUTGOING_EDGE_DIRECTION,
                                                                     edge_data_split_by_type[i])
        # now add all the incoming edges to all the nodes created
        incoming_edges_data = node.get_a_list_of_all_connections_data(GlobalNode.INCOMING_EDGE_DIRECTION)
        for i in range(len(nodes_created)):
            if nodes_created[i] is not None:
                current_table = self.regular_node_tables[i]
                new_node_key = nodes_created[i].get_key_in_table()
                current_table.add_or_edit_connection_to_node_by_bulk(new_node_key, GlobalNode.INCOMING_EDGE_DIRECTION,
                                                                     incoming_edges_data)

        # now delete the node from the unprocessed table
        unprocessed_table.delete_node(node.get_key_in_table())

        # now calculate the equation and constraints for all nodes created
        for i in range(len(nodes_created)):
            if nodes_created[i] is not None:
                nodes_created[i].calculate_equation_and_constraint()

        # now create an arnode for all the nodes created to preserve assumption (1)
        for i in range(len(nodes_created)):
            if nodes_created[i] is not None:
                self._create_arnode_for_node(nodes_created[i])

    def _handle_preprocess_of_entire_outer_layers(self):
        # from assumption (9) we will simply move the nodes to the pos-inc table
        table_to_move_to = self.regular_node_tables[Layer.INDEX_OF_POS_INC_TABLE]

        unprocessed_table = self.regular_node_tables[Layer.INDEX_OF_UNPROCESSED_TABLE]
        for unprocessed_node_key in unprocessed_table.get_list_of_all_keys():
            # remove node from unprocessed table and move it to its new table
            new_node_key = unprocessed_table.remove_node_from_table_and_relocate_to_other_table(
                unprocessed_node_key,
                table_to_move_to)

            node = table_to_move_to.get_node_by_key(new_node_key)

            # now create a corresponding arnode for the node
            # note that from conclusion (2), even though its safe to create the arnode for now, it might
            # not be safe to forward activate or fully activate the arnode, since the node it surrounds might
            # still be connected to nodes in unprocessed tables
            self._create_arnode_for_node(node)

    # perhaps its inefficient, it might be more efficient to recalculate all the edges all at once and create
    # the nodeEdges object from scratch, than deleting all edges one by one
    def preprocess_entire_layer(self):
        """
        this function must be called before forward activating or fully activating the layer nodes
        (even if the layer is the input or output layer)
        :return:
        """
        if not self.layer_is_inner:
            # from assumption (9) we will simply move the nodes to the pos-inc table
            self._handle_preprocess_of_entire_outer_layers()

        else:
            unprocessed_table = self.regular_node_tables[Layer.INDEX_OF_UNPROCESSED_TABLE]
            for node_key in unprocessed_table.get_list_of_all_keys():
                self.split_unprocessed_node_to_tables(node_key, Layer.get_split_edge_data_by_types)

    def forward_activate_arnode_table(self,
                                      table_number,
                                      function_to_calculate_merger_of_outgoing_edges):

        arnode_iterator = self.arnode_tables[table_number].get_iterator_for_all_nodes()
        for arnode in arnode_iterator:
            if arnode.get_activation_status() != ARNode.FULLY_ACTIVATED_STATUS:
                arnode.forward_activate_arnode(function_to_calculate_merger_of_outgoing_edges)

    def fully_activate_table_by_recalculating_incoming_edges(self,
                                                             table_number,
                                                             function_to_calculate_merger_of_incoming_edges,
                                                             function_to_calculate_arnode_bias):
        """
        if the previous layer was entirely forward activated but you still want ot recalculate the incoming edges to
        this layer arnodes, use this function
        :param table_number:
        :param function_to_calculate_merger_of_incoming_edges:

        :param function_to_calculate_arnode_bias: this function would receive the list of inner nodes of the
        ar node, and return a new bias for this arnode.

        """
        if self.previous_layer == Layer.NO_POINTER_TO_ADJACENT_LAYER:
            # violation of assumption (11)
            raise Exception("can not fully activate input layer")

        # according to assumption (10) only outer layers nodes should have bounds
        # so no need to recalculate bounds if layer is inner
        should_recalculate_arnodes_bounds = True
        if self.layer_is_inner:
            should_recalculate_arnodes_bounds = False

        self.arnode_tables[table_number].fully_activate_table_by_recalculating_incoming_edges(
            function_to_calculate_merger_of_incoming_edges,
            should_recalculate_arnodes_bounds,
            function_to_calculate_arnode_bias)

    def fully_activate_table_without_changing_incoming_edges(self,
                                                             table_number,
                                                             function_to_calculate_arnode_bias,
                                                             check_validity_of_activation=True):
        """
        if the previous layer was entirely forward activated and you do not want ot recalculate the incoming edges to
        this layer arnodes, use this function
        :param table_number:
        :param check_validity_of_activation:

        :param function_to_calculate_arnode_bias: this function would receive the list of inner nodes of the
        ar node, and return a new bias for this arnode.
        """
        if self.previous_layer == Layer.NO_POINTER_TO_ADJACENT_LAYER:
            # violation of assumption (11)
            raise Exception("can not fully activate input layer")

        # according to assumption (10) only outer layers nodes should have bounds
        # so no need to recalculate bounds if layer is inner
        should_recalculate_arnodes_bounds = True
        if self.layer_is_inner:
            should_recalculate_arnodes_bounds = False

        self.arnode_tables[table_number].fully_activate_table_without_changing_incoming_edges(
            function_to_calculate_arnode_bias,
            should_recalculate_arnodes_bounds,
            check_validity_of_activation)

    def split_arnode(self, table_number, key_in_table, partition_of_arnode_inner_nodes,
                     function_to_calculate_merger_of_incoming_edges,
                     function_to_calculate_merger_of_outgoing_edges,
                     function_to_calculate_arnode_bias):

        # according to assumption (10) only outer layers nodes should have bounds
        # so no need to recalculate bounds if layer is inner
        should_recalculate_bounds = True
        if self.layer_is_inner:
            should_recalculate_bounds = False

        self.arnode_tables[table_number].split_arnode(key_in_table, partition_of_arnode_inner_nodes,
                                                      function_to_calculate_merger_of_incoming_edges,
                                                      function_to_calculate_merger_of_outgoing_edges,
                                                      should_recalculate_bounds,
                                                      function_to_calculate_arnode_bias)

    def merge_list_of_arnodes(self, table_number, list_of_keys_of_arnodes_to_merge,
                              function_to_calculate_merger_of_incoming_edges,
                              function_to_calculate_merger_of_outgoing_edges,
                              function_to_calculate_arnode_bias):
        """

        :param table_number:
        :param list_of_keys_of_arnodes_to_merge:
        :param function_to_calculate_merger_of_incoming_edges:
        :param function_to_calculate_merger_of_outgoing_edges:

        :param function_to_calculate_arnode_bias: this function would receive the list of inner nodes of the
        ar node, and return a new bias for this arnode.

        :return: the new merged arnode
        """
        # according to assumption (10) only outer layers nodes should have bounds
        # so no need to recalculate bounds if layer is inner
        should_recalculate_bounds = True
        if self.layer_is_inner:
            should_recalculate_bounds = False

        return self.arnode_tables[table_number].merge_list_of_arnodes(list_of_keys_of_arnodes_to_merge,
                                                                      function_to_calculate_merger_of_incoming_edges,
                                                                      function_to_calculate_merger_of_outgoing_edges,
                                                                      should_recalculate_bounds,
                                                                      function_to_calculate_arnode_bias)

    def set_lower_and_upper_bound_for_node(self, is_arnode, table_number, key_in_table, lower_bound, upper_bound):
        """
        :param is_arnode: a boolean, if true would search for the node in the arnode tables
        :param table_number:
        :param key_in_table:
        :param lower_bound:
        :param upper_bound:
        """
        if self.layer_is_inner:
            # violation of assumption 10
            raise Exception("can not set bounds on inner layer nodes, the bounds should only be set "
                            "on outer layers nodes, and marabou would propagate the bounds throughout the network")

        tables = self.regular_node_tables
        if is_arnode:
            tables = self.arnode_tables

        tables[table_number].get_node_by_key(key_in_table).set_lower_and_upper_bound(lower_bound, upper_bound)

    def calculate_equation_and_constraint_for_all_nodes_in_table(self, is_arnode, table_number):
        tables = self.regular_node_tables
        if is_arnode:
            tables = self.arnode_tables

        tables[table_number].calculate_equation_and_constraint_for_all_nodes_in_table()

    def calculate_equation_and_constraint_for_a_specific_node(self, is_arnode, table_number, key_in_table):
        tables = self.regular_node_tables
        if is_arnode:
            tables = self.arnode_tables

        tables[table_number].calculate_equation_and_constraint_for_a_specific_node(key_in_table)

    def __str__(self):
        to_return = ''
        to_return += '----------------'
        to_return += '\n'
        to_return += 'regular tables'
        to_return += '\n'
        for table in self.regular_node_tables:
            to_return += str(table)

        to_return += '\n'
        to_return += '****************'
        to_return += '\n'
        to_return += 'arnode tables'
        to_return += '\n'
        for table in self.arnode_tables:
            to_return += str(table)

        return to_return
