from src.Tables.TableSupportsDeletion import TableSupportsDeletion
from src.Nodes.ARNode import ARNode

class ARNodeTable(TableSupportsDeletion):
    def create_new_node_and_add_to_table(self,
                                         number_of_tables_in_previous_layer,
                                         number_of_tables_in_next_layer):
        raise NotImplemented("this class can only contain arnodes")

    def create_new_arnode_and_add_to_table(self, starting_nodes):
        """

        :param starting_nodes:
        :return: the arnode created
        """
        new_node = ARNode(starting_nodes, -1, -1)

        node_key = self._add_node_to_table_without_checking(new_node)
        new_node.set_new_location(self.table_number, node_key, notify_neighbors_that_location_changed=False)

        return new_node

    def split_arnode(self, arnodes_to_split,
                     partition_of_arnode_inner_nodes,
                     function_to_calculate_merger_of_incoming_edges,
                     function_to_calculate_merger_of_outgoing_edges
                     ):
        """
        :param arnodes_to_split:
        :param partition_of_arnode_inner_nodes: a list of lists which would be a valid partition of the
        arnode inner nodes.
        each sub list would contain a list of nodes references all of which are currently owned by
        the given arnodes_to_split

        those functions would be used to calculate the edges of each resulting arnode
        :param function_to_calculate_merger_of_incoming_edges:
        :param function_to_calculate_merger_of_outgoing_edges:

        removes the arnode from the table its in and inserts the new arnodes created
        """
        # maybe add a function to check that the partition is valid

        if arnodes_to_split.get_activation_status() != ARNode.FULLY_ACTIVATED_STATUS:
            raise Exception("can not split a non fully activated arnode")

        # before continuing, delete the arnode that needs to be split
        # this would also reset the nodes owner arnode
        arnodes_to_split.destructor()

        for node_list in partition_of_arnode_inner_nodes:
            # start node with bogus arguments and then add it to the table_manager which would give the node
            # real arguments
            new_arnode = self.create_new_arnode_and_add_to_table(node_list)
            new_arnode.forward_activate_arnode(function_to_calculate_merger_of_outgoing_edges)
            new_arnode.fully_activate_arnode_and_recalculate_incoming_edges(
                function_to_calculate_merger_of_incoming_edges)

    def merge_two_arnodes(self,
                          arnode1,
                          arnode2,
                          function_to_calculate_merger_of_incoming_edges,
                          function_to_calculate_merger_of_outgoing_edges):
        """
        this method merges the two arnodes given into a single arnode.
        the merged arnode would contain all the inner nodes that both arnodes contained.

        the 2 arnodes given are killed - i.e. they are removed from their neighbors and no action can be preformed on
        them from here on out.


        :param arnode1: a fully activated arnode
        :param arnode2: a fully activated arnode

        those functions would be used to calculate the edges of each resulting arnode
        :param function_to_calculate_merger_of_incoming_edges:
        :param function_to_calculate_merger_of_outgoing_edges:
        :return: the new merged arnode
        """
        for arnode in [arnode1, arnode2]:
            if arnode.get_activation_status() != ARNode.FULLY_ACTIVATED_STATUS:
                raise Exception("can not merge a non fully activated arnode")

        # from assumption (2) both arnodes have the same table_manager
        inner_nodes_for_new_arnode = arnode1.inner_nodes.union(arnode2.inner_nodes)

        # before continuing, delete the arnodes that needs to be merged
        # this would also reset the nodes owner arnode
        arnode1.destructor()
        arnode2.destructor()

        new_arnode = self.create_new_arnode_and_add_to_table(inner_nodes_for_new_arnode)
        new_arnode.forward_activate_arnode(function_to_calculate_merger_of_outgoing_edges)
        new_arnode.fully_activate_arnode_and_recalculate_incoming_edges(function_to_calculate_merger_of_incoming_edges)
