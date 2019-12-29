from src.Nodes.Node import Node


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
    FULLY_ACTIVATED_STATUS = 2

    def __init__(self,
                 starting_nodes,
                 table_number,
                 key_in_table):
        """
        assumption (7)
        when arnode is first created, if its given a single node to start with it can remain in any activation
        status as needed.
        but if its created with more than a single node, it must be immediately fully activated. this is because only
        fully activated arnodes can merge and as such contain more than a single inner node. but to allow the
        program to create a new arnode when splitting or merging arnodes,
        I allow the arnodes constructor to receive more than one initial inner node.

        :param starting_nodes:
        :param table_number:
        :param key_in_table:
        """

        if len(starting_nodes) == 0:
            raise AssertionError("ar node must have at least one starting node")

        self.first_node_in_starting_nodes = None
        for node in starting_nodes:
            self.first_node_in_starting_nodes = node
            break

        # from assumption (2) all nodes would be in the same table and would have the same values
        number_of_tables_in_previous_layer = self.first_node_in_starting_nodes.get_number_of_tables_in_previous_layer()
        number_of_tables_in_next_layer = self.first_node_in_starting_nodes.get_number_of_tables_in_next_layer()

        # from assumption (8) we will make sure that until fully activated, the arnode won't have any global variables
        # of its own
        super().__init__(
            number_of_tables_in_previous_layer,
            number_of_tables_in_next_layer,
            table_number, key_in_table,
            Node.NO_BIAS,
            Node.NO_GLOBAL_ID, Node.NO_GLOBAL_ID, Node.NO_REFERENCE)

        self.location_of_ar_node_nested_in = self.get_location()

        for node in starting_nodes:
            if node.check_if_location_can_be_changed():
                # assumption (2) is violated
                raise AssertionError("arnodes can only contain nodes which can not change their location")

        # this list should be kept ordered by the nodes indices.
        # from assumption (2) all the nodes in the inner nodes list would be in the same table
        self.inner_nodes = [starting_nodes[i] for i in range(len(starting_nodes))]  # copy is really slow
        for node in starting_nodes:
            node.set_pointer_to_ar_node_nested_in(self)

        self.activation_status = ARNode.NOT_ACTIVATED_STATUS

    def destructor(self):
        # first go over the list of nodes got and reset their arnode owner
        for node in self.inner_nodes:
            node.reset_ar_node_nested_in()

        super().destructor()

    def _take_control_over_inner_nodes_global_values(self, function_to_calculate_arnode_bias):
        """
        this function should only be called once the arnode is fully activated
        it does the following:
        1) it removes all of the inner nodes global variables
        2) it uses the given function to calculate the bias for this arnode
        3) it calculates the arnode equation and constraint.
        4) it calculates max (lower bounds for all inner nodes which have bounds)
        and sets it as the arnode lower bound. if no nodes exist, it sets self.has_bounds to false
        5) it calculates min (upper bounds for all inner nodes which have bounds)
        and sets it as the arnode upper bound. if no nodes exist, it sets self.has_bounds to false

        :param function_to_calculate_arnode_bias: this function would receive the list of inner nodes of the
        ar node, and return a new bias for this arnode.
        :param global_incoming_id:
        :param global_outgoing_id:
        :return:
        """
        # I'm going to very carefully design this function because I want to avoid taking more ids than necessary
        # so I need to delete the inner nodes from the global system before getting a new id.
        # the problem is that various functions require me to have an id before I call them so I need to delete
        # the nodes before I get an id, which would happen before I call those functions. but if those functions
        # rely on the inner_nodes global data its problematic

        # first set our global_data_manager
        self.global_data_manager = self.first_node_in_starting_nodes.global_data_manager

        # now calculate our bias, this should be done before calculating the arnode equation
        self.bias = function_to_calculate_arnode_bias(self.inner_nodes)

        # now save all the inner nodes bound values to use later
        lower_bounds = []
        upper_bounds = []
        input_query_reference = self.global_data_manager.get_input_query_reference()
        for node in self.inner_nodes:
            if node.has_bounds:
                lower_bounds.append(input_query_reference.getLowerBound(node.get_global_incoming_id))
                upper_bounds.append(input_query_reference.getUpperBound(node.get_global_incoming_id))

        # now check if the arnode should have only 1 id or 2
        # from assumption (2) all inner nodes are in the same table
        # from assumption (11) it means that all inner nodes are from the same table
        # from assumption (12) it means that all inner nodes have 1 id or all inner nodes have 2
        # so it suffices to check only the first inner node
        should_create_2_global_ids = (
                    self.first_node_in_starting_nodes.global_incoming_id !=
                    self.first_node_in_starting_nodes.global_outgoing_id)

        # now before continuing remove all the of the inner nodes global variables
        for node in self.inner_nodes:
            node.remove_from_global_system()

        # now get a new id for us
        self.global_incoming_id = self.global_data_manager.get_new_id()
        self.global_outgoing_id = self.global_incoming_id
        if should_create_2_global_ids:
            self.global_outgoing_id = self.global_data_manager.get_new_id()

        # calculate the arnode equation and constraints
        self.calculate_equation_and_constraints()

        # now calculate arnode bounds
        inner_nodes_which_have_bounds = []
        for node in self.inner_nodes:
            if node.has_bounds:
                inner_nodes_which_have_bounds.append(node)

        if len(inner_nodes_which_have_bounds) == 0:
            self.has_bounds = False
        else:
            self.set_lower_and_upper_bound(max(lower_bounds), min(upper_bounds))

    def get_global_incoming_id(self):
        # preserve assumption (8)
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return super().get_global_incoming_id()
        return self.first_node_in_starting_nodes.get_global_incoming_id()

    def get_global_outgoing_id(self):
        # preserve assumption (8)
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return super().get_global_outgoing_id()
        return self.first_node_in_starting_nodes.get_global_outgoing_id()

    def get_node_bias(self):
        # preserve assumption (8)
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return super().get_node_bias()
        return self.first_node_in_starting_nodes.get_node_bias()

    def check_if_have_global_id(self):
        # preserve assumption (8)
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return super().check_if_have_global_id()
        return self.first_node_in_starting_nodes.check_if_have_global_id()

    def calculate_equation_and_constraints(self):
        # preserve assumption (8)
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return super().calculate_equation_and_constraints()
        return self.first_node_in_starting_nodes.calculate_equation_and_constraints()

    def remove_equation_and_constraints(self):
        # preserve assumption (8)
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return super().remove_equation_and_constraints()
        return self.first_node_in_starting_nodes.remove_equation_and_constraints()

    def remove_from_global_system(self):
        # preserve assumption (8)
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return super().remove_from_global_system()
        return self.first_node_in_starting_nodes.remove_from_global_system()

    def refresh_global_variables(self, call_calculate_equation_and_constraints=True):
        """
        :return:
        in contrast to the method from the node class, if we do not succeed refreshing the arnode for some reason,
        we always raise an exception, and when we succeed we always return Node.NO_REFERENCE
        """

        # preserve assumption (8)
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            to_return = super().refresh_global_variables(call_calculate_equation_and_constraints)
        else:
            to_return = self.first_node_in_starting_nodes.refresh_global_variables(
                call_calculate_equation_and_constraints)

        if to_return == Node.NO_REFERENCE:
            return to_return

        raise Exception("arnode was not able to be refreshed")

    def set_pointer_to_ar_node_nested_in(self, ar_node_location):
        raise NotImplementedError("can not change")

    def get_pointer_to_ar_node_nested_in(self):
        return self

    def is_nested_in_ar_node(self):
        # not sure if to set it to true or false, I need to see what effects this have on the program
        return True

    def set_in_stone(self):
        # from assumption (3)
        raise NotImplementedError("can not set arnode location in stone")

    def check_if_location_can_be_changed(self):
        return False

    def get_activation_status(self):
        return self.activation_status

    def _recalculate_edges_in_direction(self,
                                        direction_of_connection,
                                        function_to_calculate_merger_of_edges,
                                        function_to_verify_arnode_neighbors_with=lambda x: True):
        """
        this function would be used to connect this arnode to other arnodes that may have an incoming or an outgoing
        connection with us.
        this function would create a double connection, i.e. we would be connected to other nodes and they would
        be connected to us

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
            for edge_data in node.get_iterator_for_edges_data(direction_of_connection):
                _, _, weight, node_connected_to = edge_data
                arnode_connected_to = node_connected_to.get_pointer_to_ar_node_nested_in()
                if arnode_connected_to == Node.NO_REFERENCE:
                    # assumption (1) is violated, we can't find an arnode to link to
                    raise AssertionError("can not activate arnode because a connection can not link into any"
                                         "existent arnode")

                if not function_to_verify_arnode_neighbors_with(arnode_connected_to):
                    raise AssertionError("failed screening via function")

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
            reference_to_arnode.add_or_edit_neighbor(-direction_of_connection,
                                                     [self.table_number, self.key_in_table,
                                                      weight_to_connect_to_arnode_with, self])

    def forward_activate_arnode(self, function_to_calculate_merger_of_outgoing_edges):
        """
        this method partially activates the arnode.
        it connects this arnode to the arnodes it should be connected to via an outgoing connection.
        this function would create a double connection, i.e. we would be connected to other nodes and they would
        be connected to us

        :param function_to_calculate_merger_of_outgoing_edges:
        a function that receives 2 inputs
        1) a reference to an arnode
        2) a list of weights we are connected to the arnode with
        and returns a new weight for that we will connect to the given arnode with
        """
        self.check_if_killed_and_raise_error_if_is()

        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            raise AssertionError("can not demote in activation status")

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
        self._recalculate_edges_in_direction(Node.OUTGOING_EDGE_DIRECTION,
                                             function_to_calculate_merger_of_outgoing_edges)

        # finally, set the right activation status
        self.activation_status = ARNode.ONLY_FORWARD_ACTIVATED_STATUS

    def check_if_arnode_can_be_fully_activated_and_raise_exception_if_cant(self):
        """
        it checks that
        1) that the arnode is at least forward activated
        2) that the arnode is connected to all the arnodes it should be connected to by an incoming connection.
        3) that all the arnodes that have outgoing connections to this arnode are forward activated at least
        """
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return True

        if self.activation_status == ARNode.NOT_ACTIVATED_STATUS:
            # from assumption (5) for us to be fully activated requires the arnodes we are connected to by an outgoing
            # connection to be fully activated. for this to be the case, we have to be forward activated before, again
            # from assumption (5). hence it can not be that we are not forward activated once we are called to
            # fully activate ourselves.
            raise AssertionError("must fully activate arnodes we are connected to by an outgoing connection before"
                                 "fully activating this arnode")

        # now check that all needed assumptions hold
        our_location = self.get_location()
        direction_of_connection = Node.INCOMING_EDGE_DIRECTION
        for node in self.inner_nodes:
            for edge_data in node.get_iterator_for_edges_data(direction_of_connection):
                _, _, _, node_connected_to = edge_data
                arnode_connected_to = node_connected_to.get_pointer_to_ar_node_nested_in()
                if arnode_connected_to == Node.NO_REFERENCE:
                    # assumption (1) is violated, we can't find an arnode to link to
                    raise AssertionError("can not activate arnode because an incoming connection can not link into any"
                                         "existent arnode")

                # if an node is connected to us by an edge that is outgoing from us it means that for him we are
                # an incoming connection,m and vice versa
                if not arnode_connected_to.check_if_neighbor_exists(-direction_of_connection, our_location):
                    raise AssertionError("arnode that should be connected to this arnode was not connected. can not "
                                         "fully activate arnode")

                if arnode_connected_to.get_activation_status() == ARNode.NOT_ACTIVATED_STATUS:
                    raise AssertionError("can not fully activate arnode since an incoming connection is not "
                                         "forward activated")

        direction_of_connection = Node.OUTGOING_EDGE_DIRECTION
        for node in self.inner_nodes:
            for edge_data in node.get_iterator_for_edges_data(direction_of_connection):
                _, _, _, node_connected_to = edge_data
                arnode_connected_to = node_connected_to.get_pointer_to_ar_node_nested_in()
                if arnode_connected_to == Node.NO_REFERENCE:
                    # assumption (1) is violated, we can't find an arnode to link to
                    raise AssertionError("can not activate arnode because an incoming connection can not link into any"
                                         "existent arnode")

                # if an node is connected to us by an edge that is outgoing from us it means that for him we are
                # an incoming connection,m and vice versa
                if not arnode_connected_to.check_if_neighbor_exists(-direction_of_connection, our_location):
                    raise AssertionError("arnode that should be connected to this arnode was not connected. can not "
                                         "fully activate arnode")

                if arnode_connected_to.get_activation_status() != ARNode.FULLY_ACTIVATED_STATUS:
                    raise AssertionError("can not fully activate arnode since an outgoing connection is not "
                                         "fully activated")

        return True

    def fully_activate_arnode_without_changing_incoming_edges(self, function_to_calculate_arnode_bias,
                                                              check_validity_of_activation=True):
        """
        this method fully activates the arnode.
        if the node is already fully activated it does nothing

        the assumption behind this method is that the incoming edges were already set when we forward activated all the
        nodes which have an outgoing connection to this arnode

        :param check_validity_of_activation: this might take a long time to do each time, so if you are sure that
        the activation is valid you can set it to false

        :param function_to_calculate_arnode_bias: this function would receive the list of inner nodes of the
        ar node, and return a new bias for this arnode.
        """
        self.check_if_killed_and_raise_error_if_is()

        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return

        if self.activation_status == ARNode.NOT_ACTIVATED_STATUS:
            # from assumption (5) for us to be fully activated requires the arnodes we are connected to by an outgoing
            # connection to be fully activated. for this to be the case, we have to be forward activated before, again
            # from assumption (5). hence it can not be that we are not forward activated once we are called to
            # fully activate ourselves.
            raise AssertionError("must fully activate arnodes we are connected to by an outgoing connection before"
                                 "fully activating this arnode")

        if check_validity_of_activation:
            self.check_if_arnode_can_be_fully_activated_and_raise_exception_if_cant()

        # finally, set the right activation status
        self.activation_status = ARNode.FULLY_ACTIVATED_STATUS

        # finally take control over the global variables
        self._take_control_over_inner_nodes_global_values(function_to_calculate_arnode_bias)

    def fully_activate_arnode_and_recalculate_incoming_edges(self, function_to_calculate_merger_of_incoming_edges,
                                                             function_to_calculate_arnode_bias):
        """
        this method fully activates the arnode.
        if the node is already fully activated it does nothing

        otherwise, it connects/reconnects this arnode to all the arnodes containing all the nodes
        which are connected to the starting_node via an outgoing or an incoming edge.


        :param function_to_calculate_merger_of_incoming_edges:
        a function that receives 2 inputs
        1) a reference to an arnode
        2) a list of weights we are connected to the arnode with
        and returns a new weight for that we will connect to the given arnode with

        :param function_to_calculate_arnode_bias: this function would receive the list of inner nodes of the
        ar node, and return a new bias for this arnode.

        :param global_incoming_id:
        :param global_outgoing_id:
        """
        self.check_if_killed_and_raise_error_if_is()

        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return

        if self.activation_status == ARNode.NOT_ACTIVATED_STATUS:
            # from assumption (5) for us to be fully activated requires the arnodes we are connected to by an outgoing
            # connection to be fully activated. for this to be the case, we have to be forward activated before, again
            # from assumption (5). hence it can not be that we are not forward activated once we are called to
            # fully activate ourselves.
            raise AssertionError("must fully activate arnodes we are connected to by an outgoing connection before"
                                 "fully activating this arnode")

        # when connecting incoming edges make sure that the nodes we are connected to are at least forward activated
        # to preserve assumption (5). using assumption (5) its enough to check that their
        # status is not ARNode.NOT_ACTIVATED_STATUS
        self._recalculate_edges_in_direction(Node.INCOMING_EDGE_DIRECTION,
                                             function_to_calculate_merger_of_incoming_edges,
                                             function_to_verify_arnode_neighbors_with=lambda
                                                 node: node.get_activation_status() != ARNode.NOT_ACTIVATED_STATUS)

        # finally, set the right activation status
        self.activation_status = ARNode.FULLY_ACTIVATED_STATUS

        # finally take control over the global variables
        self._take_control_over_inner_nodes_global_values(function_to_calculate_arnode_bias)
