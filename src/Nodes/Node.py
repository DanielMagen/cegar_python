from src.NodeEdges import NodeEdges


class Node:
    """
    this class would represent a node that would work under the assumptions detailed in
    the ASSUMPTIONS file
    """
    # its important that they would be opposite to each other
    INCOMING_EDGE_DIRECTION = -1
    OUTGOING_EDGE_DIRECTION = 1

    NO_TABLE_NUMBER = -1
    NO_KEY_IN_TABLE = -1

    NO_REFERENCE = None

    def __init__(self,
                 number_of_tables_in_previous_layer,
                 number_of_tables_in_next_layer,
                 layer_number,
                 table_number, key_in_table):
        """

        note that from assumption (3) we do need to care about tables in the current layer
        since we have no connections to nodes in the current layer

        :param number_of_tables_in_previous_layer:
        :param number_of_tables_in_next_layer:

        :param table_number:
        :param key_in_table:

        each node which is not an input or and output node would be represented by 2 system nodes, which would be
        connected by a relu activation function. those nodes ids are given to the node as incoming_id and outgoing_id.
        if a node is an input or output node, the incoming_id should be equal to the outgoing_id
        """
        self.layer_number = layer_number
        self.table_number = table_number
        self.key_in_table = key_in_table

        self.incoming_edges_manager = NodeEdges(number_of_tables_in_previous_layer)
        self.outgoing_edges_manager = NodeEdges(number_of_tables_in_next_layer)

        # when you implement this is cpp have this be a void* pointer to avoid circular dependencies
        self.pointer_to_ar_node_nested_in = Node.NO_REFERENCE

        # later when we will wrap this node in an ar_node, this value would have to be false
        self.node_can_change_location = True

        # if this value is true then the node can not do any action
        # this value would be deprecated in the cpp implementation, as a call to the destructor would
        # make it unnecessary
        self.finished_lifetime = False

    # remove when transferring to cpp
    def check_if_killed_and_raise_error_if_is(self):
        if self.finished_lifetime:
            raise Exception("this node is dead and can not support any function")

    def destructor(self):
        """
        removes the node from all of its neighbors,
        and sets the node finished_lifetime to True
        """

        # later when moving to cpp you would have to destroy the various data structures you used

        our_location = self.get_location()

        def remove_from_node_by_direction_and_data(direction_of_connection, neighbor_node):
            # I choose to simply remove the connection data from the neighbor but not from us since we are
            # going to destroy the entire NodeEdges structure after we are done, so there is no need to remove each
            # connection from it one by one.

            # if an node is connected to us by an edge that is incoming to us it means that for him we are
            # an outgoing connection
            neighbor_node.remove_neighbor_from_neighbors_list(-direction_of_connection,
                                                              our_location,
                                                              remove_this_node_from_given_node_neighbors_list=False)

        for neighbor in self.incoming_edges_manager.get_a_list_of_all_neighbors_pointers():
            remove_from_node_by_direction_and_data(Node.INCOMING_EDGE_DIRECTION, neighbor)

        for neighbor in self.outgoing_edges_manager.get_a_list_of_all_neighbors_pointers():
            remove_from_node_by_direction_and_data(Node.OUTGOING_EDGE_DIRECTION, neighbor)

        self.finished_lifetime = True

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

    def get_table_number(self):
        return self.table_number

    def get_key_in_table(self):
        return self.key_in_table

    def get_number_of_tables_in_previous_layer(self):
        return self.incoming_edges_manager.get_number_of_tables_in_layer_connected_to()

    def get_number_of_tables_in_next_layer(self):
        return self.outgoing_edges_manager.get_number_of_tables_in_layer_connected_to()

    def set_pointer_to_ar_node_nested_in(self, pointer_to_ar_node_nested_in):
        if self.is_nested_in_ar_node():
            raise Exception("node is already nested in another ar_node. call reset_ar_node_nested_in before "
                            "calling this method")
        self.pointer_to_ar_node_nested_in = pointer_to_ar_node_nested_in

    def get_pointer_to_ar_node_nested_in(self):
        return self.pointer_to_ar_node_nested_in

    def reset_ar_node_nested_in(self):
        self.pointer_to_ar_node_nested_in = Node.NO_REFERENCE

    def is_nested_in_ar_node(self):
        return self.pointer_to_ar_node_nested_in is not Node.NO_REFERENCE

    def get_location(self):
        """
        :return: a tuple of (table_number, key_in_table)
        """
        self.check_if_killed_and_raise_error_if_is()

        # using assumption (2), since the node can not be moved to another layer we do not include the layer number
        # in the id. hence the node id is unique only in the preview of the layer its in
        return self.table_number, self.key_in_table

    def add_or_edit_neighbor(self, direction_of_connection, connection_data):
        """
        :param direction_of_connection: INCOMING_EDGE_DIRECTION or OUTGOING_EDGE_DIRECTION

        :param connection_data: a list as returned by the NodeEdges class

        connects this node and the node given in the connection data to each other
        if the connection already exists it overrides it with the new data
        """
        self._add_or_edit_neighbors_helper(direction_of_connection, [connection_data],
                                           add_this_node_to_given_node_neighbors=True)

    def add_or_edit_neighbors_by_bulk(self, direction_of_connection, list_of_connection_data):
        """
        :param direction_of_connection: INCOMING_EDGE_DIRECTION or OUTGOING_EDGE_DIRECTION

        :param list_of_connection_data: a list of connection_data.
        connection_data is a list as returned by the NodeEdges class

        connects this node and the node given in the connection data to each other
        if the connection already exists it overrides it with the new data
        """
        self._add_or_edit_neighbors_helper(direction_of_connection, list_of_connection_data,
                                           add_this_node_to_given_node_neighbors=True)

    def _add_or_edit_neighbors_helper(self, direction_of_connection, list_of_connection_data,
                                      add_this_node_to_given_node_neighbors=True):
        """
        :param direction_of_connection: INCOMING_EDGE_DIRECTION or OUTGOING_EDGE_DIRECTION

        :param list_of_connection_data: a list of connection_data.
        connection_data is a list as returned by the NodeEdges class

        :param add_this_node_to_given_node_neighbors: if true we would add ourselves to the given node neighbors
        (from the correct direction of course)
        TAKE GREAT CARE WHEN YOU SET IT TO FALSE, IF YOU DO THAT YOU MUST NOT RELOCATE THIS NODE OR THE NODE YOU
        CONNECTED TO.

        connects this node and the node given in the connection data to each other
        if the connection already exists it overrides it with the new data

        finally, it tells all the nodes we are connected to by an outgoing connection that their equation is now wrong
        """
        self.check_if_killed_and_raise_error_if_is()

        if direction_of_connection == Node.INCOMING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.incoming_edges_manager
        elif direction_of_connection == Node.OUTGOING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.outgoing_edges_manager
        else:
            raise Exception("invalid direction_of_connection")

        for connection_data in list_of_connection_data:
            table_number, key_in_table, weight, node_connected_to = connection_data
            edges_manager_to_work_with.add_or_edit_connection(table_number, key_in_table, weight, node_connected_to)

            if add_this_node_to_given_node_neighbors:
                # to avoid infinite loop set add_this_node_to_given_node_neighbors=False
                connection_data_to_feed_to_neighbor = [self.table_number,
                                                       self.key_in_table,
                                                       weight,
                                                       self]
                node_connected_to._add_or_edit_neighbors_helper(-direction_of_connection,
                                                                [connection_data_to_feed_to_neighbor],
                                                                add_this_node_to_given_node_neighbors=False)

    def remove_neighbor_from_neighbors_list(self, direction_of_connection, neighbor_location_data,
                                            remove_this_node_from_given_node_neighbors_list=True):
        """
        :param direction_of_connection:
        :param neighbor_location_data:
        :param remove_this_node_from_given_node_neighbors_list: if true would delete this node from the given
        node neighbors (from the right direction of course)
        TAKE GREAT CARE WHEN YOU SET IT TO FALSE, IF YOU DO THAT YOU MUST NOT RELOCATE THIS NODE OR THE NODE YOU
        CONNECTED TO.

        if the direction_of_connection is incoming then this function also
        tells the global data manager that our equation if now invalid
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

    def get_connection_data_to_neighbor(self, direction_of_connection, neighbor_location_data):
        self.check_if_killed_and_raise_error_if_is()

        if direction_of_connection == Node.INCOMING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.incoming_edges_manager
        elif direction_of_connection == Node.OUTGOING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.outgoing_edges_manager
        else:
            raise Exception("invalid direction_of_connection")

        return edges_manager_to_work_with.get_connection_data_for_neighbor(*neighbor_location_data)

    def get_weight_of_connection_to_neighbor(self, direction_of_connection, neighbor_location_data):
        self.check_if_killed_and_raise_error_if_is()

        if direction_of_connection == Node.INCOMING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.incoming_edges_manager
        elif direction_of_connection == Node.OUTGOING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.outgoing_edges_manager
        else:
            raise Exception("invalid direction_of_connection")

        return edges_manager_to_work_with.find_weight_of_connection(*neighbor_location_data)

    def get_number_of_connections(self, direction):
        if direction == Node.INCOMING_EDGE_DIRECTION:
            return self.incoming_edges_manager.get_number_of_connections()
        elif direction == Node.OUTGOING_EDGE_DIRECTION:
            return self.outgoing_edges_manager.get_number_of_connections()

    def get_iterator_for_connections_data(self, direction):
        self.check_if_killed_and_raise_error_if_is()

        if direction == Node.INCOMING_EDGE_DIRECTION:
            return self.incoming_edges_manager.get_iterator_over_connections()
        elif direction == Node.OUTGOING_EDGE_DIRECTION:
            return self.outgoing_edges_manager.get_iterator_over_connections()

    def get_a_list_of_all_connections_data(self, direction):
        if direction == Node.INCOMING_EDGE_DIRECTION:
            return self.incoming_edges_manager.get_a_list_of_all_connections()
        elif direction == Node.OUTGOING_EDGE_DIRECTION:
            return self.outgoing_edges_manager.get_a_list_of_all_connections()

    def get_combinations_iterator_over_connections(self, direction, r):
        if direction == Node.INCOMING_EDGE_DIRECTION:
            return self.incoming_edges_manager.get_combinations_iterator_over_connections(r)
        elif direction == Node.OUTGOING_EDGE_DIRECTION:
            return self.outgoing_edges_manager.get_combinations_iterator_over_connections(r)

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

    def __str__(self):
        def remove_node_pointer_from_list_of_all_connections(all_connections):
            return list(map(lambda lis: lis[:-1], all_connections))

        to_return = ''
        to_return += f'key number {self.key_in_table}'
        to_return += '\n'
        to_return += 'incoming connections:'
        to_return += '\n'
        incoming_connections = self.incoming_edges_manager.get_a_list_of_all_connections()
        incoming_connections = remove_node_pointer_from_list_of_all_connections(incoming_connections)
        to_return += str(incoming_connections)
        to_return += '\n'
        to_return += 'outgoing connections:'
        to_return += '\n'
        outgoing_connections = self.outgoing_edges_manager.get_a_list_of_all_connections()
        outgoing_connections = remove_node_pointer_from_list_of_all_connections(outgoing_connections)
        to_return += str(outgoing_connections)
        to_return += '\n'

        return to_return
