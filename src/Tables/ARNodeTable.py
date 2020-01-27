from src.Tables.TableSupportsDeletion import TableSupportsDeletion
from src.Nodes.ARNode import ARNode


class ARNodeTable(TableSupportsDeletion):
    def create_new_node_and_add_to_table(self,
                                         number_of_tables_in_previous_layer,
                                         number_of_tables_in_next_layer,
                                         node_bias,
                                         global_data_manager):
        raise NotImplemented("this class can only contain arnodes")

    def create_table_below_of_same_type(self):
        table_to_return = ARNodeTable(*self.get_arguments_to_create_table_below())

        return table_to_return

    def create_new_arnode_and_add_to_table(self, starting_nodes):
        """

        :param starting_nodes:
        :return: the arnode created
        """
        new_node = ARNode(starting_nodes, self.layer_number, -1, -1)

        node_key = self._add_node_to_table_without_checking(new_node)
        # change the inserted node location_data so that its table number and index would correspond to its new location
        # no need to notify_neighbors since this arnode has no neighbors since it was just created.
        # this is a consequence of the arnode assumptions. all the details are in the arnode assumptions
        # and arnode class.
        # in short, later when we would activate him and his neighbors all the necessary connections between this node
        # and his neighbors would be added.
        new_node.set_new_location(self.table_number, node_key, notify_neighbors_that_location_changed=False)

        return new_node

    def fully_activate_table_by_recalculating_incoming_edges(self,
                                                             function_to_calculate_merger_of_incoming_edges,
                                                             should_recalculate_arnodes_bounds,
                                                             function_to_calculate_arnode_bias):
        """
        if the previous layer was entirely forward activated but you want ot recalculate the incoming edges to
        this layer arnodes, use this function
        :param function_to_calculate_merger_of_incoming_edges:

        :param should_recalculate_arnodes_bounds: if true it would calculate new bounds to each arnode based on
        the bounds of their inner nodes

        :param function_to_calculate_arnode_bias: this function would receive the list of inner nodes of the
        ar node, and return a new bias for this arnode.
        """
        for arnode in self.get_iterator_for_all_nodes():
            if arnode.get_activation_status() != ARNode.FULLY_ACTIVATED_STATUS:
                arnode.fully_activate_arnode_and_recalculate_incoming_edges(
                    function_to_calculate_merger_of_incoming_edges,
                    should_recalculate_arnodes_bounds,
                    function_to_calculate_arnode_bias)

    def fully_activate_table_without_changing_incoming_edges(self,
                                                             function_to_calculate_arnode_bias,
                                                             should_recalculate_arnodes_bounds,
                                                             check_validity_of_activation=True):
        """
        if the previous layer was entirely forward activated and you do not want ot recalculate the incoming edges to
        this layer arnodes, use this function

        :param function_to_calculate_arnode_bias: this function would receive the list of inner nodes of the
        ar node, and return a new bias for this arnode.

        :param should_recalculate_arnodes_bounds: if true it would recalculate the arnodes bounds based on its inner
        nodes.

        :param check_validity_of_activation:
        """
        for arnode in self.get_iterator_for_all_nodes():
            if arnode.get_activation_status() != ARNode.FULLY_ACTIVATED_STATUS:
                arnode.fully_activate_arnode_without_changing_incoming_edges(
                    function_to_calculate_arnode_bias,
                    should_recalculate_arnodes_bounds,
                    check_validity_of_activation)

    def split_arnode(self, key_of_arnode_to_split,
                     partition_of_arnode_inner_nodes,
                     function_to_calculate_merger_of_incoming_edges,
                     function_to_calculate_merger_of_outgoing_edges,
                     should_recalculate_bounds,
                     function_to_calculate_arnode_bias):
        """
        :param key_of_arnode_to_split:
        :param partition_of_arnode_inner_nodes: a list of lists which would be a valid partition of the
        arnode inner nodes. (each inner list would be a list of nodes)
        each sub list would contain a list of nodes references all of which are currently owned by
        the given arnodes_to_split

        those functions would be used to calculate the edges of each resulting arnode
        :param function_to_calculate_merger_of_incoming_edges:
        :param function_to_calculate_merger_of_outgoing_edges:
        :param should_recalculate_bounds:
        :param function_to_calculate_arnode_bias: this function would receive the list of inner nodes of the
        ar node, and return a new bias for this arnode.

        removes the arnode from the table its in and inserts the new arnodes created
        """
        # maybe add a function to check that the partition is valid

        arnode_to_split = self.get_node_by_key(key_of_arnode_to_split)

        if arnode_to_split.get_activation_status() != ARNode.FULLY_ACTIVATED_STATUS:
            raise Exception("can not split a non fully activated arnode")

        # before continuing, delete the arnode that needs to be split
        # this would also reset the nodes owner arnode
        self.delete_node(key_of_arnode_to_split)

        for node_list in partition_of_arnode_inner_nodes:
            # start node with bogus arguments and then add it to the table_manager which would give the node
            # real arguments
            new_arnode = self.create_new_arnode_and_add_to_table(node_list)
            # preserve arnode assumption (7)
            new_arnode.forward_activate_arnode(function_to_calculate_merger_of_outgoing_edges)
            new_arnode.fully_activate_arnode_and_recalculate_incoming_edges(
                should_recalculate_bounds,
                function_to_calculate_arnode_bias,
                function_to_calculate_merger_of_incoming_edges)

    def merge_list_of_arnodes(self,
                              list_of_keys_of_arnodes_to_merge,
                              function_to_calculate_merger_of_incoming_edges,
                              function_to_calculate_merger_of_outgoing_edges,
                              should_recalculate_bounds,
                              function_to_calculate_arnode_bias):
        """
        this method merges the two arnodes given into a single arnode.
        the merged arnode would contain all the inner nodes that both arnodes contained.

        the 2 arnodes given are killed - i.e. they are removed from their neighbors and no action can be preformed on
        them from here on out.


        :param list_of_keys_of_arnodes_to_merge: keys of fully activated arnodes which would be merged
        IMPORTANT:
        this function assumes that there are no duplicates in the given list

        those functions would be used to calculate the edges of each resulting arnode
        :param function_to_calculate_merger_of_incoming_edges:
        :param function_to_calculate_merger_of_outgoing_edges:
        :param should_recalculate_bounds:
        :param function_to_calculate_arnode_bias: this function would receive the list of inner nodes of the
        ar node, and return a new bias for this arnode.
        :return: the new merged arnode
        """
        list_of_arnodes = []
        for key in list_of_keys_of_arnodes_to_merge:
            list_of_arnodes.append(self.get_node_by_key(key))

        for arnode in list_of_arnodes:
            if arnode.get_activation_status() != ARNode.FULLY_ACTIVATED_STATUS:
                raise Exception("can not merge a non fully activated arnode")

        # from assumption (2) in arnodes, all those arnodes have the same table_manager
        # from assumption (10) in arnodes, all the arnodes would have a unique set of inner_nodes
        # since there are no duplicates in the list_of_arnodes, to get all the inner nodes, simply concatenate all
        # the inner nodes to one list
        inner_nodes_for_new_arnode = []
        for arnode in list_of_arnodes:
            inner_nodes_for_new_arnode.extend(arnode.inner_nodes)

        # before continuing, delete the arnodes that needs to be merged
        # this would also reset the nodes owner arnode
        for arnode_key in list_of_keys_of_arnodes_to_merge:
            self.delete_node(arnode_key)

        new_arnode = self.create_new_arnode_and_add_to_table(inner_nodes_for_new_arnode)
        # preserve arnode assumption (7)
        new_arnode.forward_activate_arnode(function_to_calculate_merger_of_outgoing_edges)
        new_arnode.fully_activate_arnode_and_recalculate_incoming_edges(function_to_calculate_merger_of_incoming_edges,
                                                                        should_recalculate_bounds,
                                                                        function_to_calculate_arnode_bias)

        return new_arnode
