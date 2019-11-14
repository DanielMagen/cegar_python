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
                 table_manager_reference,
                 number_of_tables_in_previous_layer,
                 number_of_tables_in_next_layer,
                 number_of_tables_in_previous_layer_that_support_deletion,
                 number_of_tables_in_next_layer_that_support_deletion,
                 table_number, key_in_table):
        """

        note that from assumption (3) we do need to care about tables in the current layer
        since we have no connections to nodes in the current layer

        the following arguments given are explained in assumption (4)

        :param table_manager_reference: a reference to the table object that node is saved in
        :param number_of_tables_in_previous_layer:
        :param number_of_tables_in_next_layer:
        :param number_of_tables_in_previous_layer_that_support_deletion:
        :param number_of_tables_in_next_layer_that_support_deletion:


        :param table_number:
        :param key_in_table:
        """

        self.table_manager = table_manager_reference
        self.table_number = table_number
        self.key_in_table = key_in_table
        self.location_can_not_be_changed = False

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

        # when you implement this is cpp have this be a void* pointer to avoid circular dependencies
        self.pointer_to_ar_node_nested_in = Node.NO_AR_NODE_CONTAINER

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

        self.table_manager.notify_node_was_destroyed(self.key_in_table)

        def remove_from_node_by_direction_and_data(direction_of_connection, connection_data):
            table_number, key_in_table, weight, neighbor = connection_data
            neighbor_location_data = [table_number, key_in_table]
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

    def get_table_manager(self):
        return self.table_manager

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
        :return: a tuple of (table_number, key_in_table)
        """
        self._check_if_killed_and_raise_error_if_is()

        # using assumption (2), since the node can not be moved to another layer we do not include the layer number
        # in the id. hence the node id is unique only in the preview of the layer its in
        return (self.table_number, self.key_in_table)

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

    def get_iterator_for_edges_data_using_direction(self, direction):
        if direction == Node.OUTGOING_EDGE_DIRECTION:
            return self.get_iterator_for_outgoing_edges_data()
        elif direction == Node.INCOMING_EDGE_DIRECTION:
            return self.get_iterator_for_incoming_edges_data()

    def add_neighbor(self, direction_of_connection, weight, node, add_this_node_to_given_node_neighbors=False):
        """

        :param direction_of_connection:
        :param weight:
        :param node:
        :param add_this_node_to_given_node_neighbors: if true we would add ourselves to the given node neighbors
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

        table_number, key_in_table = node.get_location()
        edges_manager_to_work_with.add_connection(table_number, key_in_table, weight, node)

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
        self._check_if_killed_and_raise_error_if_is()

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

    def change_location(self, table_number, key_in_table):
        self._check_if_location_can_be_changed_and_raise_error_if_not()
        self._check_if_killed_and_raise_error_if_is()

        previous_location = self.get_location()
        self.table_number = table_number
        self.key_in_table = key_in_table

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
                 table_manager_reference,
                 starting_nodes,
                 table_number,
                 key_in_table):

        if len(starting_nodes) == 0:
            raise Exception("ar node must have at least one starting node")

        first_node_in_starting_nodes = None
        for node in starting_nodes:
            first_node_in_starting_nodes = node
            break

        # from assumption (2) all nodes would be in the same table and would have the same values
        number_of_tables_in_previous_layer = first_node_in_starting_nodes.get_number_of_tables_in_previous_layer()
        number_of_tables_in_next_layer = first_node_in_starting_nodes.get_number_of_tables_in_next_layer()

        super().__init__(
            table_manager_reference,
            number_of_tables_in_previous_layer,
            number_of_tables_in_next_layer,
            number_of_tables_in_previous_layer,
            number_of_tables_in_next_layer,
            table_number, key_in_table)

        self.location_of_ar_node_nested_in = self.get_location()

        for node in starting_nodes:
            if not node.check_if_location_can_be_changed():
                # assumption (2) is violated
                raise Exception("arnodes can only contain nodes which can not change their location")

        # this list should be kept ordered by the nodes indices.
        # from assumption (2) all the nodes in the inner nodes list would be in the same table
        self.inner_nodes = set(starting_nodes)
        for node in starting_nodes:
            node.set_pointer_to_ar_node_nested_in(self.get_location())

        self.activation_status = ARNode.NOT_ACTIVATED_STATUS

    def destructor(self):
        # first go over the list of nodes got and reset their arnode owner
        for node in self.inner_nodes:
            node.reset_ar_node_nested_in()

        super().destructor()

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

    def _insert_edges_for_the_first_time(self, direction_of_connection,
                                         function_to_calculate_merger_of_edges,
                                         function_to_verify_arnode_neighbors_with=lambda x: True,
                                         add_this_node_to_given_node_neighbors=False):
        """
        this function would be used to connect this arnode to other arnodes that may have an incoming or an outgoing
        connection with us.

        :param direction_of_connection:
        either Node.OUTGOING_EDGE_DIRECTION or Node.INCOMING_EDGE_DIRECTION
        the direction from our perspective, i.e. if we want to add outgoing connections
        the direction_to_insert_in would be Node.OUTGOING_EDGE_DIRECTION

        :param function_to_calculate_merger_of_edges:
        a function that receives 2 inputs
        1) a reference to an arnode
        2) a list of weights we are connected to the arnode with
        and returns a new weight for that we will connect to the given arnode with

        :param function_to_verify_arnode_neighbors_with: before accepting an arnode as our neighbor we will screen it
        using this function. if the function returns false we would raise an Exception
        """
        # first go over all arnodes we are connected to via an outgoing connection and create a map of
        # arnode_location -> [reference_to_arnode, [list of weights we are connected to this arnode with]]
        # by assumption (6) all nodes we are connected to via an outgoing connection reside in the same layer and
        # as such the arnode_location is a unique identifier for it
        map_of_weights = {}
        for node in self.inner_nodes:
            for edge_data in node.get_iterator_for_edges_data_using_direction(direction_of_connection):
                _, _, weight, node_connected_to = edge_data
                arnode_connected_to = node_connected_to.get_pointer_to_ar_node_nested_in()
                if arnode_connected_to == Node.NO_AR_NODE_CONTAINER:
                    # assumption (1) is violated, we can't find an arnode to link to
                    raise Exception("can not activate arnode because an outgoing connection can not link into any"
                                    "existent arnode")

                if not function_to_verify_arnode_neighbors_with(arnode_connected_to):
                    raise Exception("failed screening via function")

                location_of_arnode_connected_to = arnode_connected_to.get_location()

                # now check if we have seen the arnode before or not and update the map_of_weights accordingly
                if location_of_arnode_connected_to in map_of_weights:
                    map_of_weights[location_of_arnode_connected_to][1].append(weight)
                else:
                    map_of_weights[location_of_arnode_connected_to] = [arnode_connected_to, [weight]]

        # now the final weight would be the result of the activation of the
        # function_to_calculate_merger_of_outgoing_edges on
        # reference_to_arnode, list_of_weights_we_are_connected_to_this_arnode
        # use the result to connect to the arnodes
        for key in map_of_weights:
            reference_to_arnode, list_of_weights_we_are_connected_to_this_arnode = map_of_weights[key]
            weight_to_connect_to_arnode_with = \
                function_to_calculate_merger_of_edges(reference_to_arnode,
                                                      list_of_weights_we_are_connected_to_this_arnode)

            # if an node is connected to us by an edge that is outgoing from us it means that for him we are
            # an incoming connection,m and vice versa
            reference_to_arnode.add_neighbor(-direction_of_connection,
                                             weight_to_connect_to_arnode_with,
                                             self,
                                             add_this_node_to_given_node_neighbors)

    def forward_activate_arnode(self, function_to_calculate_merger_of_outgoing_edges,
                                add_this_node_to_given_node_neighbors=False):
        """
        this method partially activates the arnode.
        it connects this arnode to all the arnodes containing all the nodes which are connected to the nodes in its
        not list via an outgoing edge.

        :param function_to_calculate_merger_of_outgoing_edges:
        a function that receives 2 inputs
        1) a reference to an arnode
        2) a list of weights we are connected to the arnode with
        and returns a new weight for that we will connect to the given arnode with


        :param add_this_node_to_given_node_neighbors: when we add a new arnode neighbor to this node we might want to
        notify this neighbor to have him add us as his neighbor.
        if true, it will set the add_this_node_to_given_node_neighbors in the add_neighbor function to true.

        """
        self._check_if_killed_and_raise_error_if_is()

        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            raise Exception("can not demote in activation status")

        if self.activation_status == ARNode.ONLY_FORWARD_ACTIVATED_STATUS:
            return

        # else, self.activation_status == ARNode.NOT_ACTIVATED_STATUS from assumption (5)

        # the arnodes we need to connect to might have merged and also our inner_nodes list might be larger than 1.
        # at the start of the program this can't be because for nodes to split or merge requires
        # the arnode to be fully activated, which in turn requires this node to  already be forward activated.
        # however, a merger or a split of nodes might be seen as a demotion in activation status,
        # and as such we need to take into account the fact that when this function is called
        # 1) this arnode might contain multiple nodes in its inner nodes list
        # 2) the arnodes we need to connect to might have merged
        self._insert_edges_for_the_first_time(Node.OUTGOING_EDGE_DIRECTION,
                                              function_to_calculate_merger_of_outgoing_edges,
                                              add_this_node_to_given_node_neighbors=
                                              add_this_node_to_given_node_neighbors)

        # finally, set the right activation status
        self.activation_status = ARNode.ONLY_FORWARD_ACTIVATED_STATUS

    def fully_activate_arnode(self,
                              function_to_calculate_merger_of_incoming_edges,
                              function_to_calculate_merger_of_outgoing_edges,
                              add_this_node_to_given_node_neighbors=False):
        """
        this method fully activates the arnode.
        it connects this arnode to all the arnodes containing all the nodes which are connected to the starting_node
        via an outgoing or an incoming edge.

        :param function_to_calculate_merger_of_incoming_edges:
        a function that receives 2 inputs
        1) a reference to an arnode
        2) a list of weights we are connected to the arnode with
        and returns a new weight for that we will connect to the given arnode with

        :param function_to_calculate_merger_of_outgoing_edges:
        a function that receives 2 inputs
        1) a reference to an arnode
        2) a list of weights we are connected to the arnode with
        and returns a new weight for that we will connect to the given arnode with


        :param add_this_node_to_given_node_neighbors: when we add a new arnode neighbor to this node we might want to
        notify this neighbor to have him add us as his neighbor.
        if true, it will set the add_this_node_to_given_node_neighbors in the add_neighbor function to true.
        """
        self._check_if_killed_and_raise_error_if_is()

        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return

        if self.activation_status == ARNode.NOT_ACTIVATED_STATUS:
            self.forward_activate_arnode(function_to_calculate_merger_of_incoming_edges,
                                         add_this_node_to_given_node_neighbors=add_this_node_to_given_node_neighbors)

        # when connecting incoming edges make sure that the nodes we are connected to are at least forward activated
        # to preserve assumption (5). using assumption (5) its enough to check that their
        # status is not ARNode.NOT_ACTIVATED_STATUS
        self._insert_edges_for_the_first_time(Node.OUTGOING_EDGE_DIRECTION,
                                              function_to_calculate_merger_of_outgoing_edges,
                                              function_to_verify_arnode_neighbors_with=lambda
                                                  node: node.get_activation_status() != ARNode.NOT_ACTIVATED_STATUS,
                                              add_this_node_to_given_node_neighbors=
                                              add_this_node_to_given_node_neighbors
                                              )

        # finally, set the right activation status
        self.activation_status = ARNode.FULLY_ACTIVATED_STATUS

    @staticmethod
    def split(arnodes_to_split, partition_of_arnode_inner_nodes,
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

        table_manager = arnodes_to_split.get_table_manager()

        # before continuing, delete the arnode that needs to be split
        # this would also reset the nodes owner arnode
        arnodes_to_split.destructor()

        for node_list in partition_of_arnode_inner_nodes:
            new_arnode = table_manager.create_new_arnode(node_list)
            for i in range(1, len(node_list)):
                new_arnode.inner_node.append(node_list[i])

            new_arnode.fully_activate_arnode(function_to_calculate_merger_of_incoming_edges,
                                             function_to_calculate_merger_of_outgoing_edges,
                                             add_this_node_to_given_node_neighbors=True)

    @staticmethod
    def merge_two_arnodes(arnode1,
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
        table_manager = arnode1.get_table_manager()
        inner_nodes_for_new_arnode = arnode1.inner_nodes.union(arnode2.inner_nodes)

        # before continuing, delete the arnodes that needs to be merged
        # this would also reset the nodes owner arnode
        arnode1.destructor()
        arnode2.destructor()

        new_arnode = table_manager.create_new_arnode(inner_nodes_for_new_arnode)

        new_arnode.fully_activate_arnode(function_to_calculate_merger_of_incoming_edges,
                                         function_to_calculate_merger_of_outgoing_edges,
                                         add_this_node_to_given_node_neighbors=True)

