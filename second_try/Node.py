from second_try.NodeEdges import *


class Node:
    """
    this class would represent a node that would work under the assumptions detailed in
    the ASSUMPTIONS file
    """
    INCOMING_EDGE_DIRECTION = -1
    OUTGOING_EDGE_DIRECTION = 1

    NO_AR_NODE_CONTAINER = None

    def __init__(self,
                 number_of_tables_in_previous_layer,
                 number_of_tables_in_next_layer,
                 number_of_tables_in_previous_layer_that_support_deletion,
                 number_of_tables_in_next_layer_that_support_deletion,
                 layer_number, table_number, index_in_table):
        """

        note that from assumption (3) we do need to care about tables in the current layer
        since we have no connections to nodes in the current layer

        the following arguments given are explained in assumption (4)

        :param number_of_tables_in_previous_layer:
        :param number_of_tables_in_next_layer:
        :param number_of_tables_in_previous_layer_that_support_deletion:
        :param number_of_tables_in_next_layer_that_support_deletion:


        :param layer_number:
        :param table_number:
        :param index_in_table:
        """

        self.layer_number = layer_number  # use assumption (2) and do not create a set_layer_number function
        self.table_number = table_number
        self.index_in_table = index_in_table
        self.location_can_not_be_changed = False
        self.location_of_ar_node_nested_in = Node.NO_AR_NODE_CONTAINER

        if number_of_tables_in_previous_layer_that_support_deletion < number_of_tables_in_previous_layer:
            self.incoming_edges_manager = NodeEdgesForNonDeletionTables(
                number_of_tables_in_previous_layer,
                number_of_tables_in_previous_layer_that_support_deletion)
        else:
            self.incoming_edges_manager = NodeEdges(number_of_tables_in_previous_layer)

        if number_of_tables_in_next_layer_that_support_deletion < number_of_tables_in_next_layer:
            self.outgoing_edges_manager = NodeEdgesForNonDeletionTables(
                number_of_tables_in_next_layer,
                number_of_tables_in_next_layer_that_support_deletion)
        else:
            self.outgoing_edges_manager = NodeEdges(number_of_tables_in_next_layer)

    def set_location_of_ar_node_nested_in(self, ar_node_location):
        self.location_of_ar_node_nested_in = ar_node_location

    def get_location_of_ar_node_nested_in(self):
        return self.location_of_ar_node_nested_in

    def is_nested_in_ar_node(self):
        return self.location_of_ar_node_nested_in is not Node.NO_AR_NODE_CONTAINER

    def set_in_stone(self):
        """
        removes the ability to change the node location
        """
        self.location_can_not_be_changed = True

    def is_the_node_set_in_stone(self):
        return self.location_can_not_be_changed

    def get_location(self):
        """
        :return: [table_number, index_in_table]
        """
        # using assumption (2), since the node can not be moved to another layer we do not include the layer number
        # in the id. hence the node id is unique only in the preview of the layer its in
        return [self.table_number, self.index_in_table]

    def _check_if_location_can_be_changed(self):
        """
        if the node location can not be changed it raises an error
        otherwise it does nothing
        """
        if self.location_can_not_be_changed:
            raise Exception("the node location cannot be changed")

    def add_neighbor(self, direction_of_connection, weight, node, add_this_node_to_given_node_neighbors=False):
        """

        :param direction_of_connection:
        :param weight:
        :param node:
        :param add_this_node_to_given_node_neighbors: if true would add this node to the given node neighbors
        (from the right direction of course)
        :return:
        """
        if direction_of_connection == Node.INCOMING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.incoming_edges_manager
        elif direction_of_connection == Node.OUTGOING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.outgoing_edges_manager
        else:
            raise Exception("invalid direction_of_connection")

        table_number, index_in_table = node.get_location()
        edges_manager_to_work_with.add_connection(table_number, index_in_table, weight, node)

        if add_this_node_to_given_node_neighbors:
            node.add_neighbor(-direction_of_connection, weight, self, add_this_node_to_given_node_neighbors=False)

    def delete_neighbor(self, direction_of_connection, neighbor_location_data,
                        delete_this_node_to_given_node_neighbors=False):
        """
        :param direction_of_connection:
        :param neighbor_location_data:
        :param delete_this_node_to_given_node_neighbors: if true would delete this node from the given node neighbors
        (from the right direction of course)
        :return:
        """
        if direction_of_connection == Node.INCOMING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.incoming_edges_manager
        elif direction_of_connection == Node.OUTGOING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.outgoing_edges_manager
        else:
            raise Exception("invalid direction_of_connection")

        table_number, index_in_table = neighbor_location_data
        _, node_connected_to = edges_manager_to_work_with.delete_connection(table_number, index_in_table)

        if delete_this_node_to_given_node_neighbors:
            node_connected_to.delete_neighbor(-direction_of_connection, self.get_location(),
                                              delete_this_node_to_given_node_neighbors=False)

    def get_notified_that_neighbor_location_changed(self, direction_of_connection, previous_location, new_location):
        """

        :param direction_of_connection: if direction_of_connection == Node.INCOMING_EDGE_DIRECTION it means that
        for us this node is an incoming connection, i.e. its in the self.incoming_edges_manager. exactly the same
        for Node.OUTGOING_EDGE_DIRECTION

        :param previous_location: the previous location of the node that was changed

        :param new_location: the new location of the node that was changed
        :return:
        """
        if direction_of_connection == Node.INCOMING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.incoming_edges_manager
        elif direction_of_connection == Node.OUTGOING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.outgoing_edges_manager
        else:
            raise Exception("invalid direction_of_connection")

        previous_table_number = previous_location[0]
        previous_index_in_table = previous_location[1]
        new_table_number = new_location[0]
        new_index_in_table = new_location[1]

        edges_manager_to_work_with.move_connection(previous_table_number, previous_index_in_table, new_table_number,
                                                   new_index_in_table)

    def _notify_all_neighbors_that_my_location_changed(self, previous_location):
        """
        :param previous_location:
        goes over all neighbors of the node and notifies them that this node has been moved to another location
        within the layer (using assumption (2))
        """
        new_location = self.get_location()

        # first go over all incoming edges
        # if an node is connected to us by an edge that is incoming to us it means that for him we are
        # an outgoing connection
        direction_of_connection = Node.OUTGOING_EDGE_DIRECTION
        for connection_data in self.incoming_edges_manager.iterate_over_connections():
            reference_to_node_connected_to = connection_data[3]
            reference_to_node_connected_to.get_notified_that_neighbor_location_changed(direction_of_connection,
                                                                                       previous_location,
                                                                                       new_location)

        direction_of_connection = Node.INCOMING_EDGE_DIRECTION
        for connection_data in self.outgoing_edges_manager.iterate_over_connections():
            reference_to_node_connected_to = connection_data[3]
            reference_to_node_connected_to.get_notified_that_neighbor_location_changed(direction_of_connection,
                                                                                       previous_location,
                                                                                       new_location)

    def change_location(self, table_number, index_in_table):
        self._check_if_location_can_be_changed()

        previous_location = self.get_location()
        self.table_number = table_number
        self.index_in_table = index_in_table

        self._notify_all_neighbors_that_my_location_changed(previous_location)


class ARNode(Node):
    """
    this class would represent a ARNode that would work under the assumptions detailed in
    the ASSUMPTIONS file.
    """

    def __init__(self,
                 number_of_tables_in_previous_layer,
                 number_of_tables_in_next_layer,
                 layer_number, table_number, index_in_table):
        super().__init__(
            number_of_tables_in_previous_layer,
            number_of_tables_in_next_layer,
            number_of_tables_in_previous_layer,
            number_of_tables_in_next_layer,
            layer_number, table_number, index_in_table)

        self.location_of_ar_node_nested_in = self.get_location()

        self.inner_nodes = set([])

    def set_location_of_ar_node_nested_in(self, ar_node_location):
        raise NotImplementedError("can not change")

    def get_location_of_ar_node_nested_in(self):
        return self.get_location()

    def is_nested_in_ar_node(self):
        return True

    def set_in_stone(self):
        # from assumption (3)
        raise NotImplementedError("can not set arnode location in stone")

    def is_the_node_set_in_stone(self):
        return False
