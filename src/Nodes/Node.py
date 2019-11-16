from src.NodeEdges import NodeEdges


class Node:
    """
    this class would represent a node that would work under the assumptions detailed in
    the ASSUMPTIONS file
    """
    # its important that they would be opposite to each other
    INCOMING_EDGE_DIRECTION = -1
    OUTGOING_EDGE_DIRECTION = 1

    NO_AR_NODE_CONTAINER = None

    def __init__(self,
                 number_of_tables_in_previous_layer,
                 number_of_tables_in_next_layer,
                 table_number, key_in_table):
        """

        note that from assumption (3) we do need to care about tables in the current layer
        since we have no connections to nodes in the current layer

        the following arguments given are explained in assumption (4)

        :param number_of_tables_in_previous_layer:
        :param number_of_tables_in_next_layer:


        :param table_number:
        :param key_in_table:
        """
        self.table_number = table_number
        self.key_in_table = key_in_table

        self.incoming_edges_manager = NodeEdges(number_of_tables_in_previous_layer)
        self.outgoing_edges_manager = NodeEdges(number_of_tables_in_next_layer)

        # when you implement this is cpp have this be a void* pointer to avoid circular dependencies
        self.pointer_to_ar_node_nested_in = Node.NO_AR_NODE_CONTAINER

        # later when we will wrap this node in an ar_node, this value would have to be false
        self.node_can_change_location = True

        # if this value is true then the node can not do any action
        # this value would be deprecated in the cpp implementation, as a call to the destructor would
        # make it unnecessary
        self.finished_lifetime = False

    def destructor(self):
        """
        removes the node from all of its neighbors,
        and sets the node finished_lifetime to True

        it then remove the node from its residing table
        """

        def remove_from_node_by_direction_and_data(direction_of_connection, connection_data):
            table_number, key_in_table, weight, neighbor = connection_data
            neighbor_location_data = [table_number, key_in_table]
            neighbor.remove_neighbor_from_neighbors_list(direction_of_connection,
                                                         neighbor_location_data,
                                                         remove_this_node_from_given_node_neighbors_list=True)

        # if an node is connected to us by an edge that is incoming to us it means that for him we are
        # an outgoing connection
        for data in self.get_iterator_for_edges_data(Node.INCOMING_EDGE_DIRECTION):
            remove_from_node_by_direction_and_data(Node.OUTGOING_EDGE_DIRECTION, data)

        for data in self.get_iterator_for_edges_data(Node.OUTGOING_EDGE_DIRECTION):
            remove_from_node_by_direction_and_data(Node.INCOMING_EDGE_DIRECTION, data)

        self.finished_lifetime = True

    ################ remove when transferring to cpp
    def check_if_killed_and_raise_error_if_is(self):
        if self.finished_lifetime:
            raise Exception("this node is dead and can not support any function")

    def set_in_stone(self):
        # from assumption (3)
        self.node_can_change_location = False

    def check_if_location_can_be_changed(self):
        return self.node_can_change_location

    def set_new_location(self, new_table_number, new_key_in_table, notify_neighbors_that_location_changed=True):
        if not self.node_can_change_location:
            raise Exception("node location can not be changed")

        previous_location = self.get_location()

        self.table_number = new_table_number
        self.key_in_table = new_key_in_table

        if notify_neighbors_that_location_changed:
            self.notify_all_neighbors_that_my_location_changed(previous_location)

    def get_key_in_table(self):
        return self.key_in_table

    def get_number_of_tables_in_previous_layer(self):
        return self.incoming_edges_manager.get_number_of_tables_in_layer_connected_to()

    def get_number_of_tables_in_next_layer(self):
        return self.outgoing_edges_manager.get_number_of_tables_in_layer_connected_to()

    def set_pointer_to_ar_node_nested_in(self, pointer_to_ar_node_nested_in):
        if self.is_nested_in_ar_node():
            raise Exception("node is already nested in another ar_node. call reset_ar_node_nested_in before"
                            " calling this method")
        self.pointer_to_ar_node_nested_in = pointer_to_ar_node_nested_in

    def get_pointer_to_ar_node_nested_in(self):
        return self.pointer_to_ar_node_nested_in

    # when you implement this in cpp have another way to check if the pointer is valid. I remember we saw some way to
    # have the pointer be null or 0 in cpp
    def reset_ar_node_nested_in(self):
        self.pointer_to_ar_node_nested_in = Node.NO_AR_NODE_CONTAINER

    def is_nested_in_ar_node(self):
        return self.pointer_to_ar_node_nested_in is not Node.NO_AR_NODE_CONTAINER

    def get_location(self):
        """
        :return: a tuple of (table_number, key_in_table)
        """
        self.check_if_killed_and_raise_error_if_is()

        # using assumption (2), since the node can not be moved to another layer we do not include the layer number
        # in the id. hence the node id is unique only in the preview of the layer its in
        return self.table_number, self.key_in_table

    def add_or_edit_neighbor(self, direction_of_connection, connection_data,
                             add_this_node_to_given_node_neighbors=True):
        """

        :param direction_of_connection:
        :param connection_data: a list as returned by the NodeEdges class
        :param add_this_node_to_given_node_neighbors: if true we would add ourselves to the given node neighbors
        (from the right direction of course)
        TAKE GREAT CARE WHEN YOU SET IT TO FALSE, IF YOU DO THAT YOU MUST NOT RELOCATE THIS NODE OR THE NODE YOU
        CONNECTED TO.
        :return:
        """
        self.check_if_killed_and_raise_error_if_is()

        if direction_of_connection == Node.INCOMING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.incoming_edges_manager
        elif direction_of_connection == Node.OUTGOING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.outgoing_edges_manager
        else:
            raise Exception("invalid direction_of_connection")

        table_number, key_in_table, weight, node_connected_to = connection_data
        edges_manager_to_work_with.add_or_edit_connection(table_number, key_in_table, weight, node_connected_to)

        if add_this_node_to_given_node_neighbors:
            # to avoid infinite loop set add_this_node_to_given_node_neighbors=False
            node_connected_to.add_or_edit_neighbor(-direction_of_connection,
                                                   [self.table_number, self.key_in_table, weight, self],
                                                   add_this_node_to_given_node_neighbors=False)

    def check_if_neighbor_exists(self, direction_of_connection, neighbor_location_data):
        """

        :param direction_of_connection: a direction of connection from our perspective
        :param neighbor_location_data:
        :return: true if the connection exist, false otherwise
        """
        table_number, key_in_table = neighbor_location_data
        if direction_of_connection == Node.INCOMING_EDGE_DIRECTION:
            return self.incoming_edges_manager.check_if_connection_exist(table_number, key_in_table)

        if direction_of_connection == Node.OUTGOING_EDGE_DIRECTION:
            return self.outgoing_edges_manager.check_if_connection_exist(table_number, key_in_table)

    def get_connection_data_for_neighbor(self, direction_of_connection, neighbor_location_data):
        self.check_if_killed_and_raise_error_if_is()

        if direction_of_connection == Node.INCOMING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.incoming_edges_manager
        elif direction_of_connection == Node.OUTGOING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.outgoing_edges_manager
        else:
            raise Exception("invalid direction_of_connection")

        return edges_manager_to_work_with.get_connection_data_for_neighbor(*neighbor_location_data)

    def remove_neighbor_from_neighbors_list(self, direction_of_connection, neighbor_location_data,
                                            remove_this_node_from_given_node_neighbors_list=True):
        """
        :param direction_of_connection:
        :param neighbor_location_data:
        :param remove_this_node_from_given_node_neighbors_list: if true would delete this node from the given
        node neighbors (from the right direction of course)
        TAKE GREAT CARE WHEN YOU SET IT TO FALSE, IF YOU DO THAT YOU MUST NOT RELOCATE THIS NODE OR THE NODE YOU
        CONNECTED TO.
        :return:
        """
        self.check_if_killed_and_raise_error_if_is()

        if direction_of_connection == Node.INCOMING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.incoming_edges_manager
        elif direction_of_connection == Node.OUTGOING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.outgoing_edges_manager
        else:
            raise Exception("invalid direction_of_connection")

        table_number, key_in_table = neighbor_location_data
        _, node_connected_to = edges_manager_to_work_with.delete_connection(table_number, key_in_table)

        if remove_this_node_from_given_node_neighbors_list:
            node_connected_to.remove_neighbor_from_neighbors_list(-direction_of_connection, self.get_location(),
                                                                  remove_this_node_from_given_node_neighbors_list=False)

    def get_notified_that_neighbor_location_changed(self, direction_of_connection, previous_location, new_location):
        """

        :param direction_of_connection: if direction_of_connection == Node.INCOMING_EDGE_DIRECTION it means that
        for us this node is an incoming connection, i.e. its in the self.incoming_edges_manager. exactly the same
        for Node.OUTGOING_EDGE_DIRECTION

        :param previous_location: the previous location of the node that was changed

        :param new_location: the new location of the node that was changed
        :return:
        """
        self.check_if_killed_and_raise_error_if_is()

        if direction_of_connection == Node.INCOMING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.incoming_edges_manager
        elif direction_of_connection == Node.OUTGOING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.outgoing_edges_manager
        else:
            raise Exception("invalid direction_of_connection")

        previous_table_number = previous_location[0]
        previous_key_in_table = previous_location[1]
        new_table_number = new_location[0]
        new_key_in_table = new_location[1]

        edges_manager_to_work_with.move_connection(previous_table_number, previous_key_in_table, new_table_number,
                                                   new_key_in_table)

    def notify_all_neighbors_that_my_location_changed(self, previous_location):
        """
        :param previous_location:
        goes over all neighbors of the node and notifies them that this node has been moved to another location
        within the layer (using assumption (2))
        """
        self.check_if_killed_and_raise_error_if_is()

        new_location = self.get_location()

        # first go over all incoming edges
        # if an node is connected to us by an edge that is incoming to us it means that for him we are
        # an outgoing connection
        direction_of_connection = Node.OUTGOING_EDGE_DIRECTION
        for connection_data in self.incoming_edges_manager.get_iterator_over_connections():
            reference_to_node_connected_to = connection_data[3]
            reference_to_node_connected_to.get_notified_that_neighbor_location_changed(direction_of_connection,
                                                                                       previous_location,
                                                                                       new_location)

        direction_of_connection = Node.INCOMING_EDGE_DIRECTION
        for connection_data in self.outgoing_edges_manager.get_iterator_over_connections():
            reference_to_node_connected_to = connection_data[3]
            reference_to_node_connected_to.get_notified_that_neighbor_location_changed(direction_of_connection,
                                                                                       previous_location,
                                                                                       new_location)

    def get_number_of_connections(self, direction):
        if direction == Node.INCOMING_EDGE_DIRECTION:
            return self.incoming_edges_manager.get_number_of_connections()
        elif direction == Node.OUTGOING_EDGE_DIRECTION:
            return self.outgoing_edges_manager.get_number_of_connections()

    def get_iterator_for_edges_data(self, direction):
        self.check_if_killed_and_raise_error_if_is()

        if direction == Node.INCOMING_EDGE_DIRECTION:
            return self.incoming_edges_manager.get_iterator_over_connections()
        elif direction == Node.OUTGOING_EDGE_DIRECTION:
            return self.outgoing_edges_manager.get_iterator_over_connections()

    def get_a_list_of_all_incoming_connections_data(self, direction):
        if direction == Node.INCOMING_EDGE_DIRECTION:
            return self.incoming_edges_manager.get_a_list_of_all_connections()
        elif direction == Node.OUTGOING_EDGE_DIRECTION:
            return self.outgoing_edges_manager.get_a_list_of_all_connections()
