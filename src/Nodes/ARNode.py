from src.Nodes.Node import Node


# use the decorator pattern
class ARNode(Node):
    """
    this class would represent a ARNode that would work under the assumptions detailed in
    the ASSUMPTIONS file

    important note:
    the arnode wraps regular nodes.
    it has 3 possible activation status and depending on each on them it behaves somewhat differently.
    the arnode has been designed and implemented such that
    1) when the arnode takes over a regular node, all of the actions that are supposed to take place on the regular
    node, now take place using this arnode
    2) if an arnode has a neighbor which is a regular node, then some actions of that node can affect the arnode.
    if so, then the arnode takes care to notice those actions. if the arnode does not do anything about some actions,
    then it means that they do not affect the arnode.
    """
    # I want to first create the different arnodes and only after finishing creating them, activating them.
    # this is required to preserve assumption (1) because arnodes can not be created in another way which still
    # preserves it.
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
                 layer_number,
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
        the programmer must take note and if the arnode is initialized with more than one inner node, immediately
        activate it.

        :param starting_nodes:
        :param table_number:
        :param key_in_table:
        """

        if len(starting_nodes) == 0:
            raise AssertionError("ar node must have at least one inner node")

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
            layer_number,
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
        self.inner_nodes = [starting_nodes[i] for i in range(len(starting_nodes))]  # copy is slow
        for node in starting_nodes:
            node.set_pointer_to_ar_node_nested_in(self)

        self.activation_status = ARNode.NOT_ACTIVATED_STATUS

    def destructor(self):
        # first go over the list of nodes got and reset their arnode owner
        for node in self.inner_nodes:
            node.reset_ar_node_nested_in()

        super().destructor()

    def get_inner_nodes(self):
        return self.inner_nodes

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

    def check_if_node_equation_is_valid(self):
        # preserve assumption (8)
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return not self.global_data_manager.check_if_node_has_invalid_equations(self.layer_number,
                                                                                    self.table_number,
                                                                                    self.key_in_table,
                                                                                    is_arnode=True)
        return self.first_node_in_starting_nodes.check_if_node_equation_is_valid()

    def set_global_equation_to_invalid(self):
        # preserve assumption (8)
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return self.global_data_manager.add_location_of_node_that_dont_have_valid_equation(self.layer_number,
                                                                                               self.table_number,
                                                                                               self.key_in_table,
                                                                                               is_arnode=True)
        self.first_node_in_starting_nodes.set_global_equation_to_invalid()

    def _set_global_equation_to_valid(self):
        # preserve assumption (8)
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return self.global_data_manager.remove_location_of_node_that_dont_have_valid_equation(self.layer_number,
                                                                                                  self.table_number,
                                                                                                  self.key_in_table,
                                                                                                  is_arnode=True)
        self.first_node_in_starting_nodes._set_global_equation_to_valid()

    def get_node_bias(self):
        # preserve assumption (8)
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return super().get_node_bias()
        return self.first_node_in_starting_nodes.get_node_bias()

    def set_node_bias(self, bias):
        # preserve assumption (8)
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return super().set_node_bias(bias)
        return self.first_node_in_starting_nodes.set_node_bias(bias)

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

    def remove_from_global_system(self, give_back_id_to_data_manager=True):
        # preserve assumption (8)
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return super().remove_from_global_system(give_back_id_to_data_manager)
        return self.first_node_in_starting_nodes.remove_from_global_system(give_back_id_to_data_manager)

    def set_pointer_to_ar_node_nested_in(self, ar_node_location):
        raise NotImplementedError("an arnode is considered to be nested inside itself, this can not change")

    def get_pointer_to_ar_node_nested_in(self):
        return self

    def is_nested_in_ar_node(self):
        return True

    def set_in_stone(self):
        # from assumption (3)
        raise NotImplementedError("can not set arnode location in stone")

    def check_if_location_can_be_changed(self):
        return True

    def get_activation_status(self):
        return self.activation_status

    def _take_control_over_inner_nodes_global_values(self, function_to_calculate_arnode_bias,
                                                     should_recalculate_bounds):
        """
        this function should only be called once the arnode is fully activated
        it does the following:
        1) for all the inner nodes that have global variables - it removes those global variables
        2) it set the arnode bias, global_data_manager, id, equation and constraint.
        if it can do so based on the inner nodes it does,
        otherwise it sets them to default values
        3) it uses the given function to calculate the bias for this arnode

        if it can use the inner nodes it also:
        4) if should_recalculate_bounds=true it would calculate new bounds to the arnode based on the bounds of
        its inner nodes. it would do so as described in the doc of the should_recalculate_bounds param


        :param function_to_calculate_arnode_bias: this function would receive the list of inner nodes of the
        ar node, and return a new bias for this arnode.

        :param should_recalculate_bounds: a boolean. if set to true the arnode would have its bounds calculated
        in the following way:
        calculate max (lower bounds for all inner nodes which have bounds)
        and set it as the arnode lower bound. if no nodes exist, it sets self.has_bounds to false
        calculate min (upper bounds for all inner nodes which have bounds)
        and set it as the arnode upper bound. if no nodes exist, it sets self.has_bounds to false
        :return:
        """
        if self.activation_status != ARNode.FULLY_ACTIVATED_STATUS:
            raise AssertionError("can not take over inner nodes with a none fully activated arnode")

        # I want to avoid taking more ids than necessary from the global data manager
        # so I want to delete the inner nodes from the global system before getting a new id.
        # the problem is that various functions require me to have an id before I call them so I need to delete
        # the nodes before I get an id, which would happen before I call those functions. but if those functions
        # rely on the inner_nodes global data its problematic
        # so I'm going to very carefully design this function

        # first set our global_data_manager
        # since the global_data_manager reference is never deleted, we can take it from the first inner node
        self.global_data_manager = self.first_node_in_starting_nodes.global_data_manager

        # now calculate our bias, this should be done before calculating the arnode equation
        # since the bias is never deleted we can give this function all of our inner nodes
        self.set_node_bias(function_to_calculate_arnode_bias(self.inner_nodes))

        # we can call the _take_control_over_inner_nodes_global_values during the run of the program
        # where the inner nodes belonged to a previous arnode which already removed their global variables.
        # as such we check to see if any nodes remain with global variables and act upon them from now on.
        # there could be no such nodes
        inner_nodes_that_still_have_global_variables = []
        for node in self.inner_nodes:
            if node.get_global_incoming_id() == Node.NO_GLOBAL_ID or node.get_global_outgoing_id() == Node.NO_GLOBAL_ID:
                inner_nodes_that_still_have_global_variables.append(node)

        lower_bounds = []
        upper_bounds = []
        if should_recalculate_bounds:
            # now save all the inner nodes bound values to use later
            for node in inner_nodes_that_still_have_global_variables:
                if node.check_if_has_bounds():
                    # we depend on the fact that if a node has only an upper bound or only a lower bound, then
                    # the getLowerBound and getUpperBound would return -infinity or infinity
                    # and not return None
                    lower_bounds.append(self.global_data_manager.getLowerBound(node.get_global_incoming_id))
                    upper_bounds.append(self.global_data_manager.getUpperBound(node.get_global_incoming_id))

        # before continuing remove (almost) all the of the inner nodes global variables
        for i in range(1, len(inner_nodes_that_still_have_global_variables)):
            inner_nodes_that_still_have_global_variables[i].remove_from_global_system()

        if len(inner_nodes_that_still_have_global_variables) >= 1:
            self.global_incoming_id, self.global_outgoing_id = inner_nodes_that_still_have_global_variables[
                0].remove_from_global_system(return_id=False)
        else:
            self.global_incoming_id = self.global_data_manager.get_new_id()
            # now check if the arnode should have only 1 id or 2
            # from assumption (2) all inner nodes are in the same table
            # from assumption (11) it means that all inner nodes are from the same layer
            # from assumption (12) it means that all inner nodes have 1 id or all inner nodes have 2
            # so it suffices to check only the first inner node
            should_create_2_global_ids = self.first_node_in_starting_nodes.check_if_node_is_inner()
            if should_create_2_global_ids:
                self.global_outgoing_id = self.global_data_manager.get_new_id()
            else:
                self.global_outgoing_id = self.global_incoming_id

        # calculate the arnode equation and constraints
        self.calculate_equation_and_constraints()

        # now calculate arnode bounds
        if should_recalculate_bounds:
            # we depend on the fact that if a node has only an upper bound or only a lower bound, then
            # the getLowerBound and getUpperBound would return -infinity or infinity
            # so the lower_bounds and upper_bounds lists do not contain None
            if len(lower_bounds) == 0 or len(upper_bounds) == 0:
                self.has_bounds = False
            else:
                self.set_lower_and_upper_bound(max(lower_bounds), min(upper_bounds))

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
        # first go over all arnodes we are connected to and create a map of
        # arnode_location -> [reference_to_arnode, [list of weights we are connected to this arnode with]]
        # by assumption (6) all nodes we are connected to via an outgoing connection reside in the same layer and
        # as such the arnode_location is a unique identifier for it
        map_of_weights = {}
        for node in self.inner_nodes:
            for edge_data in node.get_iterator_for_connections_data(direction_of_connection):
                _, _, weight, node_connected_to = edge_data
                arnode_connected_to = node_connected_to.get_pointer_to_ar_node_nested_in()
                if arnode_connected_to == Node.NO_REFERENCE:
                    # assumption (1) is violated, we can't find an arnode to link to
                    raise AssertionError("can not calculate edge because a connection can not link into any"
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

            # if a node is connected to us by an edge that is outgoing from us it means that for him we are
            # an incoming connection, and vice versa
            # so connect to the other node using "minus direction_of_connection"
            reference_to_arnode.add_or_edit_neighbor(-direction_of_connection,
                                                     [self.table_number, self.key_in_table,
                                                      weight_to_connect_to_arnode_with, self])

    def check_if_arnode_can_be_forward_activated_and_raise_exception_if_cant(self):
        """
        checks that
        1) all the nodes we are connected to by an outgoing connections have a wrapper arnode
        2) that all the nodes we are connected to by an outgoing connections are connected to us.
        a one directional connection shouldn't happen but we check none the less
        i.e. it checks that assumption (5) holds
        """
        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            raise AssertionError("arnodes can not be demoted in activation state")
        if self.activation_status == ARNode.ONLY_FORWARD_ACTIVATED_STATUS:
            return True

        our_location = self.get_location()
        direction_of_connection = Node.OUTGOING_EDGE_DIRECTION
        for node in self.inner_nodes:
            for edge_data in node.get_iterator_for_connections_data(direction_of_connection):
                _, _, _, node_connected_to = edge_data
                arnode_connected_to = node_connected_to.get_pointer_to_ar_node_nested_in()
                if arnode_connected_to == Node.NO_REFERENCE:
                    # assumption (1) is violated, we can't find an arnode to link to
                    raise AssertionError("can not activate arnode because an outgoing connection can not link into any"
                                         "existent arnode")

                # if an node is connected to us by an edge that is outgoing from us it means that for him we are
                # an incoming connection,m and vice versa
                if not arnode_connected_to.check_if_neighbor_exists(-direction_of_connection, our_location):
                    raise AssertionError("arnode that should be connected to this arnode was not connected. can not "
                                         "forward activate arnode")

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

        if self.activation_status == ARNode.ONLY_FORWARD_ACTIVATED_STATUS:
            return

        # else, self.activation_status == ARNode.NOT_ACTIVATED_STATUS from assumption (5)
        self.check_if_arnode_can_be_forward_activated_and_raise_exception_if_cant()

        # the arnodes we need to connect to might have merged and also our inner_nodes list might be larger than 1.
        # at the start of the program this can't be because for nodes to split or merge requires
        # the arnode to be fully activated, which in turn requires this node to already be forward activated.
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
        2) that all the nodes that have outgoing connections to this arnode, have an arnode which contains them
        and is forward activated at least
        3) that all connections to this arnode are bidirectional. a one directional connection shouldn't happen but
        we check none the less
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

        # now from assumption (5) we are forward activated

        # now check that all needed assumptions hold
        our_location = self.get_location()
        direction_of_connection = Node.INCOMING_EDGE_DIRECTION
        for node in self.inner_nodes:
            for edge_data in node.get_iterator_for_connections_data(direction_of_connection):
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

        # check that all arnodes we are connected to by an outgoing connection are fully activated
        for arnode in self.get_iterator_for_connections_data(Node.OUTGOING_EDGE_DIRECTION):
            for edge_data in arnode.get_iterator_for_connections_data(direction_of_connection):
                _, _, _, arnode_connected_to = edge_data
                if arnode_connected_to.get_activation_status() != ARNode.FULLY_ACTIVATED_STATUS:
                    raise AssertionError("can not fully activate arnode since an outgoing connection is not "
                                         "fully activated")

        return True

    def fully_activate_arnode_without_changing_incoming_edges(self, function_to_calculate_arnode_bias,
                                                              should_recalculate_bounds,
                                                              check_validity_of_activation=True):
        """
        this method fully activates the arnode.
        if the node is already fully activated it does nothing

        the assumption behind this method is that the incoming edges were already set when we forward activated all the
        nodes which have an outgoing connection which is incoming to this arnode.
        (because when we forward activated all those nodes they created an outgoing edge that is incoming to us,
        so all of our incoming connections were already set)

        problem is that the activation process is not commutative. i.e. we get different weights for an edge depending
        on the node we activate (the node at the beginning or the end of the edge). so we might want to recalculate
        the arnode edges before activating it. if so, this is not the function you should call.

        btw, note that we only care about the incoming edges since the node outgoing edges were "put into the game",
        when the arnode was forward activated (think of what happens when the forward activated node is connected to a
        fully activated node which was merged or split).
        when first activating an arnode it shouldn't matter much which full activation function we choose, one that
        recalculates the incoming edges or not, but when we are in the middle of the program and we are activating an
        arnode that was just split or merged, it matters a great deal which full activation function ae choose.

        :param function_to_calculate_arnode_bias: this function would receive the list of inner nodes of the
        ar node, and return a new bias for this arnode.

        :param should_recalculate_bounds: if true it would calculate new bounds to the arnode based on the bounds of
        its inner nodes

        :param check_validity_of_activation: set to true by default since we assume that this function would mostly
        be called only at the very start of the program, and at this stage its better to check the validity.
        this might take a long time to do each time, so if you are sure that
        the activation is valid you can set it to false

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

        # set the right activation status
        self.activation_status = ARNode.FULLY_ACTIVATED_STATUS

        # finally take control over the global variables
        self._take_control_over_inner_nodes_global_values(function_to_calculate_arnode_bias, should_recalculate_bounds)

    def fully_activate_arnode_and_recalculate_incoming_edges(self, function_to_calculate_merger_of_incoming_edges,
                                                             should_recalculate_bounds,
                                                             function_to_calculate_arnode_bias):
        """
        this method fully activates the arnode.
        if the node is already fully activated it does nothing

        otherwise it recalculates the incoming connections weights to this arnode

        :param function_to_calculate_merger_of_incoming_edges:
        a function that receives 2 inputs
        1) a reference to an arnode
        2) a list of weights we are connected to the arnode with
        and returns a new weight for that we will connect to the given arnode with

        :param should_recalculate_bounds: if true it would calculate new bounds to the arnode based on the bounds of
        its inner nodes

        :param function_to_calculate_arnode_bias: this function would receive the list of inner nodes of the
        ar node, and return a new bias for this arnode.
        """
        self.check_if_killed_and_raise_error_if_is()

        if self.activation_status == ARNode.FULLY_ACTIVATED_STATUS:
            return

        if self.activation_status == ARNode.NOT_ACTIVATED_STATUS:
            # from assumption (5) for us to be fully activated requires the arnodes we are connected to by an
            # outgoing connection to be fully activated. for this to be the case, we have to be forward activated
            # before, again from assumption (5).
            # hence it can not be that we are not forward activated once we are called to fully activate ourselves.
            raise AssertionError("must fully activate arnodes we are connected to by an outgoing connection before"
                                 "fully activating this arnode")

        # when connecting incoming edges make sure that the nodes we are connected to are at least forward activated
        # to preserve assumption (5). using assumption (5) its enough to check that their
        # status is not ARNode.NOT_ACTIVATED_STATUS
        self._recalculate_edges_in_direction(Node.INCOMING_EDGE_DIRECTION,
                                             function_to_calculate_merger_of_incoming_edges,
                                             function_to_verify_arnode_neighbors_with=lambda node:
                                             node.get_activation_status() != ARNode.NOT_ACTIVATED_STATUS)

        # set the right activation status
        self.activation_status = ARNode.FULLY_ACTIVATED_STATUS

        # finally take control over the global variables
        self._take_control_over_inner_nodes_global_values(function_to_calculate_arnode_bias, should_recalculate_bounds)
