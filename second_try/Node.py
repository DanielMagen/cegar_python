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

        # when you implement this is cpp have this be a void* pointer to avoid circular dependencies
        self.pointer_to_ar_node_nested_in = Node.NO_AR_NODE_CONTAINER

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

        # if this value is true then the node can not do any action
        # this value would be deprecated in the cpp implementation, as a call to the destructor would
        # make it unnecessary
        self.finished_lifetime = False

    def destructor(self):
        """
        removes the node from all of its neighbors,
        and sets the node finished_lifetime to True

        it does not remove the node from its residing table, its up to the table to do so.
        """

        def remove_from_node_by_direction_and_data(direction_of_connection, connection_data):
            table_number, index_in_table, weight, neighbor = connection_data
            neighbor_location_data = [table_number, index_in_table]
            neighbor.remove_neighbor_from_neighbors_list(direction_of_connection,
                                                         neighbor_location_data,
                                                         remove_this_node_from_given_node_neighbors_list=False)

        # if an node is connected to us by an edge that is incoming to us it means that for him we are
        # an outgoing connection
        for data in self.get_iterator_for_incoming_edges_data():
            remove_from_node_by_direction_and_data(Node.OUTGOING_EDGE_DIRECTION, data)

        for data in self.get_iterator_for_outgoing_edges_data():
            remove_from_node_by_direction_and_data(Node.INCOMING_EDGE_DIRECTION, data)

        self.finished_lifetime = True

    def check_if_killed(self):
        return self.finished_lifetime

    def _check_if_killed_and_raise_error_if_is(self):
        if self.check_if_killed():
            raise Exception("this arnode is dead and can not support any function")

    def get_number_of_tables_in_previous_layer(self):
        return self.incoming_edges_manager.get_number_of_tables_in_layer_connected_to()

    def get_number_of_tables_in_next_layer(self):
        return self.outgoing_edges_manager.get_number_of_tables_in_layer_connected_to()

    def get_pointer_to_ar_node_nested_in(self):
        return self.pointer_to_ar_node_nested_in

    # when you implement this in cpp have another way to check if the pointer is valid. I remember we saw some way to
    # have the pointer be null or 0 in cpp
    def reset_ar_node_nested_in(self):
        self.pointer_to_ar_node_nested_in = Node.NO_AR_NODE_CONTAINER

    def set_pointer_to_ar_node_nested_in(self, ar_node_location):
        if self.is_nested_in_ar_node():
            raise Exception("node is already nested in another ar_node. call reset_ar_node_nested_in before"
                            " calling this method")
        self.pointer_to_ar_node_nested_in = ar_node_location

    def is_nested_in_ar_node(self):
        return self.pointer_to_ar_node_nested_in is not Node.NO_AR_NODE_CONTAINER

    def set_in_stone(self):
        """
        removes the ability to change the node location
        """
        self.location_can_not_be_changed = True

    def check_if_location_can_be_changed(self):
        return self.location_can_not_be_changed

    def get_location(self):
        """
        :return: [table_number, index_in_table]
        """
        self._check_if_killed_and_raise_error_if_is()

        # using assumption (2), since the node can not be moved to another layer we do not include the layer number
        # in the id. hence the node id is unique only in the preview of the layer its in
        return [self.table_number, self.index_in_table]

    def _check_if_location_can_be_changed_and_raise_error_if_not(self):
        """
        if the node location can not be changed it raises an error
        otherwise it does nothing
        """
        if self.location_can_not_be_changed:
            raise Exception("the node location cannot be changed")

    def get_iterator_for_incoming_edges_data(self):
        self._check_if_killed_and_raise_error_if_is()

        return self.incoming_edges_manager.get_iterator_over_connections()

    def get_iterator_for_outgoing_edges_data(self):
        self._check_if_killed_and_raise_error_if_is()

        return self.outgoing_edges_manager.get_iterator_over_connections()

    def add_neighbor(self, direction_of_connection, weight, node, add_this_node_to_given_node_neighbors=False):
        """

        :param direction_of_connection:
        :param weight:
        :param node:
        :param add_this_node_to_given_node_neighbors: if true would add this node to the given node neighbors
        (from the right direction of course)
        :return:
        """
        self._check_if_killed_and_raise_error_if_is()

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

    def remove_neighbor_from_neighbors_list(self, direction_of_connection, neighbor_location_data,
                                            remove_this_node_from_given_node_neighbors_list=False):
        """
        :param direction_of_connection:
        :param neighbor_location_data:
        :param remove_this_node_from_given_node_neighbors_list: if true would delete this node from the given
        node neighbors (from the right direction of course)
        :return:
        """
        self._check_if_killed_and_raise_error_if_is()

        if direction_of_connection == Node.INCOMING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.incoming_edges_manager
        elif direction_of_connection == Node.OUTGOING_EDGE_DIRECTION:
            edges_manager_to_work_with = self.outgoing_edges_manager
        else:
            raise Exception("invalid direction_of_connection")

        table_number, index_in_table = neighbor_location_data
        _, node_connected_to = edges_manager_to_work_with.delete_connection(table_number, index_in_table)

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
        self._check_if_killed_and_raise_error_if_is()

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
        self._check_if_killed_and_raise_error_if_is()

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

    def change_location(self, table_number, index_in_table):
        self._check_if_location_can_be_changed_and_raise_error_if_not()
        self._check_if_killed_and_raise_error_if_is()

        previous_location = self.get_location()
        self.table_number = table_number
        self.index_in_table = index_in_table

        self._notify_all_neighbors_that_my_location_changed(previous_location)


# use the decorator pattern
class ARNode(Node):
    """
    this class would represent a ARNode that would work under the assumptions detailed in
    the ASSUMPTIONS file.
    """
    # I want to first create the different arnodes and only after finishing creating them, activating them.
    # this is required to preserve assumption (1) because arnodes can not be created another way which still preserves
    # it.
    # in addition to that I want to be able to only partially convert the network into an arnode form. this partial
    # transformation only makes sense if we transform the network into an arnode form from the end backwards.
    # an arnode of which its incoming edges are not from arnodes can not logically support abstraction or refinement.
    # as such we use the ONLY_FORWARD_ACTIVATED_STATUS to indicate that from this arnode backwards we can not guarantee
    # that the network has been converted into an arnode form.
    # further assumptions about he different activation status can be found in the ASSUMPTIONS file
    NOT_ACTIVATED_STATUS = 0
    ONLY_FORWARD_ACTIVATED_STATUS = 1
    FULLY_ACTIVATED_STATUS = 1

    def __init__(self,
                 starting_node,
                 table_number,
                 index_in_table):
        """
        :param starting_node:
        :param table_number:
        :param index_in_table:
        """
        number_of_tables_in_previous_layer = starting_node.get_number_of_tables_in_previous_layer()
        number_of_tables_in_next_layer = starting_node.get_number_of_tables_in_next_layer()
        layer_number = starting_node.get_layer_number()

        super().__init__(
            number_of_tables_in_previous_layer,
            number_of_tables_in_next_layer,
            number_of_tables_in_previous_layer,
            number_of_tables_in_next_layer,
            layer_number, table_number, index_in_table)

        self.location_of_ar_node_nested_in = self.get_location()

        if not starting_node.check_if_location_can_be_changed():
            # assumption (2) is violated
            raise Exception("arnodes can only contain nodes which can not change their location")

        self.inner_nodes = [starting_node]
        starting_node.set_pointer_to_ar_node_nested_in(self.get_location())

        self.activation_status = ARNode.NOT_ACTIVATED_STATUS

    def set_pointer_to_ar_node_nested_in(self, ar_node_location):
        raise NotImplementedError("can not change")

    def get_pointer_to_ar_node_nested_in(self):
        return self.get_location()

    def is_nested_in_ar_node(self):
        return True

    def set_in_stone(self):
        # from assumption (3)
        raise NotImplementedError("can not set arnode location in stone")

    def check_if_location_can_be_changed(self):
        return False

    def get_activation_status(self):
        return self.activation_status

    def forward_activate_arnode(self, add_this_node_to_given_node_neighbors=False):
        """
        this method partially activates the arnode.
        it connects this arnode to all the arnodes containing all the nodes which are connected to the starting_node
        via an outgoing edge.

        :param add_this_node_to_given_node_neighbors: when we add a new arnode neighbor to this node we might want to
        notify this neighbor to have him add us as his neighbor.
        if true, it will set the add_this_node_to_given_node_neighbors in the add_neighbor function to true.

        """
        self._check_if_killed_and_raise_error_if_is()

        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            # from assumptions (6)
            raise Exception("can not demote in activation status")

        if self.activation_status == ARNode.ONLY_FORWARD_ACTIVATED_STATUS:
            return

        # else, self.activation_status == ARNode.NOT_ACTIVATED_STATUS from assumption (5)

        # since before calling this function self.activation_status == ARNode.NOT_ACTIVATED_STATUS
        # from assumptions (4) we conclude that the arnode only contains 1 node - the starting_node it received
        # simply replace the starting_node outgoing edges to nodes they are connected to with outgoing edges to
        # the arnodes which contain them

        direction_of_connection = ARNode.OUTGOING_EDGE_DIRECTION

        starting_node = self.inner_nodes[0]

        # from assumption (5) we conclude that all the nodes that we are connected to by an outgoing edge can not
        # be fully activated yet as full activation requires this node to be forward activated
        # and from assumption (6) this must be the first time (and from assumption (5) the only time) we are entering
        # this status. as such from assumption (4) the arnodes we are connected to could not have merge or split and as
        # such these arnodes only contain a single node.
        # i.e. we do not need to care about nodes that were merged before calling this function, simply go over the
        # starting node connection and translate them to connections to arnodes
        iterator_for_outgoing_edges = starting_node.get_iterator_for_outgoing_edges_data()
        for data in iterator_for_outgoing_edges:
            _, _, weight, node_connected_to = data
            if not node_connected_to.is_nested_in_ar_node():
                # assumption (1) is violated
                raise Exception("the arnode needs all of its outgoing edges to be connected to only arnodes")
            arnode_containing_node = node_connected_to.get_pointer_to_ar_node_nested_in()
            self.add_neighbor(direction_of_connection,
                              weight,
                              arnode_containing_node,
                              add_this_node_to_given_node_neighbors)

        # finally, set the right activation status
        self.activation_status = ARNode.ONLY_FORWARD_ACTIVATED_STATUS

    def fully_activate_arnode(self, add_this_node_to_given_node_neighbors=False):
        """
        this method fully activates the arnode.
        it connects this arnode to all the arnodes containing all the nodes which are connected to the starting_node
        via an outgoing or an incoming edge.

        :param add_this_node_to_given_node_neighbors: when we add a new arnode neighbor to this node we might want to
        notify this neighbor to have him add us as his neighbor.
        if true, it will set the add_this_node_to_given_node_neighbors in the add_neighbor function to true.
        """
        self._check_if_killed_and_raise_error_if_is()

        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return

        # from assumption (5) for our node to be fully activated entails all the nodes we are connected to by
        # an outgoing edge to be fully activated beforehand. if this node was not forward activated then by
        # assumption (6) it means this node is not activated at all. as such by assumption (5) the nodes we are
        # connected to could not be fully activated.
        # i.e. assumptions (5) and (6) imply that the activation process must be gradual.
        if self.activation_status != ARNode.ONLY_FORWARD_ACTIVATED_STATUS:
            raise Exception("the nodes we are connected to by an outgoing edge must be fully activated")

        # now from assumption (5) we get self.activation_status = ARNode.ONLY_FORWARD_ACTIVATED_STATUS

        # all the outgoing edges were already added using the forward_activate_arnode function
        # simply add all the incoming edges

        # since before calling this function self.activation_status == ARNode.ONLY_FORWARD_ACTIVATED_STATUS maximally
        # from assumptions (4) we conclude that the arnode only contains 1 node - the starting_node it received
        # simply replace the starting_node outgoing edges to nodes they are connected to with outgoing edges to
        # the arnodes which contain them

        direction_of_connection = ARNode.INCOMING_EDGE_DIRECTION

        starting_node = self.inner_nodes[0]

        # from assumptions (5) we conclude that the incoming edges arnodes could not have been fully activated since it
        # would entail us to have been fully activated first, but we are only now entering the fully activated status.
        # and from assumption (6) this must be the first time (and from assumption (5) the only time) we are entering
        # this status. as such from assumption (4) the arnodes we are connected to could not have merge or split and as
        # such these arnodes only contain a single node.
        # however these nodes can by in a non-activated status and they could not connect to us as it would contradict
        # assumptions (5), so we will check for such nodes.
        iterator_for_incoming_edges = starting_node.get_iterator_for_incoming_edges_data()
        for data in iterator_for_incoming_edges:
            _, _, weight, node_connected_to = data
            if not node_connected_to.is_nested_in_ar_node():
                # assumption (1) is violated
                raise Exception("the arnode needs all of its outgoing edges to be connected to only arnodes")

            arnode_containing_node = node_connected_to.get_pointer_to_ar_node_nested_in()

            if arnode_containing_node.get_activation_status() != ARNode.ONLY_FORWARD_ACTIVATED_STATUS:
                raise Exception("the arnode could not be fully activated before fully activating all the arnodes its"
                                "connected to by a outgoing edge")

            self.add_neighbor(direction_of_connection,
                              weight,
                              arnode_containing_node,
                              add_this_node_to_given_node_neighbors)

            # finally, set the right activation status
            self.activation_status = ARNode.FULLY_ACTIVATED_STATUS

    def split(self, partition_of_arnode_inner_nodes):
        pass

    @staticmethod
    def merge_two_arnodes(arnode1,
                          arnode2,
                          layer_number, table_number, index_in_table,
                          function_to_calculate_merger_of_incoming_edges,
                          function_to_calculate_merger_of_outgoing_edges):
        """
        this method merges the two arnodes given into a single arnode.
        the merged arnode would contain all the inner nodes that both arnodes contained.

        the 2 arnodes given are killed - i.e. they are removed from their neighbors and no action can be preformed on
        them from here on out.


        :param arnode1: a fully activated arnode
        :param arnode2: a fully activated arnode

        data required for the creation of the new arnode:
        :param layer_number:
        :param table_number:
        :param index_in_table:
        :param function_to_calculate_merger_of_incoming_edges:
        :param function_to_calculate_merger_of_outgoing_edges:
        :return: the new merged arnode
        """
        pass
