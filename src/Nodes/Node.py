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

    NO_GLOBAL_ID = -1
    NO_EQUATION = None
    NO_REFERENCE = None
    NO_BIAS = 0

    def __init__(self,
                 number_of_tables_in_previous_layer,
                 number_of_tables_in_next_layer,
                 layer_number,
                 table_number, key_in_table,
                 bias,
                 global_incoming_id, global_outgoing_id,
                 global_data_manager):
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
        :param global_incoming_id:
        :param global_outgoing_id:
        :param global_data_manager:
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

        # each node which is not an input or and output node would be represented by 2 system nodes, which would be
        # connected by a relu activation function. those nodes ids are given to the node as incoming_id and outgoing_id.
        #  if a node is an input or output node, the incoming_id should be equal to the outgoing_id
        self.global_incoming_id = global_incoming_id
        self.global_outgoing_id = global_outgoing_id
        # each node would a reference to the global_data_manager object which is responsible for the system.
        # the node destructor would call it if need be
        self.global_data_manager = global_data_manager

        # each node would manage the equation that links it to its incoming nodes
        self.equation = Node.NO_EQUATION
        self.bias = bias  # this variable is NOT considered a global variable. it should not be deleted as long as
        # the node lives, because the arnodes which take over this node would use this node bias to calculate their own

        # each node would manage the constraint between its 2 global IDs. if the ids are the same, no constraint would
        # be added
        self.has_constraint = False
        # if we set bounds on this node, this would be set to true
        self.has_bounds = False

        # this variable would be set to false if we know that the equation that the node set is no longer correct
        # for example, if an incoming neighbor changed its global id for some reason, then the equation we calculated
        # is no longer correct
        # if the variable has no equation then it is set to True
        self.global_equation_is_valid = True

        # if this value is true then the node can not do any action
        # this value would be deprecated in the cpp implementation, as a call to the destructor would
        # make it unnecessary
        self.finished_lifetime = False

    ################ remove when transferring to cpp
    def check_if_killed_and_raise_error_if_is(self):
        if self.finished_lifetime:
            raise Exception("this node is dead and can not support any function")

    def destructor(self):
        """
        removes the node from all of its neighbors,
        and sets the node finished_lifetime to True
        """

        # for now simply remove yourself from as a neighbor from all other nodes
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

        # finally, remove from the global system
        if self.global_incoming_id != Node.NO_GLOBAL_ID or self.global_outgoing_id != Node.NO_GLOBAL_ID:
            self.remove_from_global_system()

        self.finished_lifetime = True

    def get_global_incoming_id(self):
        return self.global_incoming_id

    def get_global_outgoing_id(self):
        return self.global_outgoing_id

    def get_node_bias(self):
        return self.bias

    def set_node_bias(self, bias):
        self.bias = bias
        if self.equation != Node.NO_EQUATION:
            # since we changed the bias the node equation is no longer correct
            self.global_equation_is_valid = False

    def check_if_have_global_id(self):
        return self.global_incoming_id != Node.NO_GLOBAL_ID and self.global_outgoing_id != Node.NO_GLOBAL_ID

    def set_global_equation_to_invalid(self):
        self.global_equation_is_valid = False

    def check_if_have_global_equation_is_valid(self):
        return self.global_equation_is_valid

    def set_lower_and_upper_bound(self, lower_bound, upper_bound):
        """
        sets lower and upper bound on the node global_incoming_id
        :param lower_bound:
        :param upper_bound:
        :return:
        """
        if self.global_incoming_id == Node.NO_GLOBAL_ID:
            raise Exception("can not set lower and upper bound without a valid global id")

        self.global_data_manager.setLowerBound(self.global_incoming_id, lower_bound)
        self.global_data_manager.setUpperBound(self.global_incoming_id, upper_bound)

        self.has_bounds = True

    def remove_node_bounds(self):
        if self.global_incoming_id == Node.NO_GLOBAL_ID:
            raise Exception("can not remove lower and upper bound without a valid global id")
        # for now this function does not exist, but I think that creating one should be ok, its just a map object
        # and we can delete form it at ease
        self.global_data_manager.removeBounds(self.global_incoming_id)

        self.has_bounds = False

    def calculate_equation_and_constraints(self):
        """
        this function calculates the equation between this node and its incoming nodes
        and the constraint between its 2 global ids

        if the equation and constraint already exist, it first deletes them from and then recalculates them

        from assumption (9) the equation and constraint should be set or removed together
        """
        if self.global_incoming_id == Node.NO_GLOBAL_ID or self.global_outgoing_id == Node.NO_GLOBAL_ID:
            raise Exception("the node global id has been removed form it and as such could not be given an equation")

        # first check if they already exist and if so delete them
        if self.equation != Node.NO_EQUATION:
            # from assumption (9) the equation and constraint should be set or removed together,
            # so its enough to check if the equation was set or not
            self.remove_equation_and_constraints()

        # before starting, check if the node you are about to add an equation and constraint to is an inner
        # or an outer node. according to assumption (11) an outer node can only have 1 global id
        if self.global_incoming_id == self.global_outgoing_id:
            # check if we are in the input or output node
            if self.incoming_edges_manager.has_no_connections():
                # we are in the input layer, no need to assign any equations
                # setting self.global_equation_is_valid = True was done by remove_equation_and_constraints
                # so simply return
                return
        else:
            # initialize the relu constraint between them
            self.global_data_manager.addReluConstraint(self.global_incoming_id,
                                                       self.global_outgoing_id)
            self.has_constraint = True

            # initialize the equation
        self.equation = self.global_data_manager.get_new_equation()
        # add -1 * yourself
        self.equation.addAddend(-1, self.global_incoming_id)

        # now go through all incoming nodes and add weight * node_id to the equation
        iterator_over_incoming_connections = self.incoming_edges_manager.get_iterator_over_connections()

        for connection_data in iterator_over_incoming_connections:
            weight = connection_data[NodeEdges.INDEX_OF_WEIGHT_IN_DATA]
            id_of_incoming_node = connection_data[
                NodeEdges.INDEX_OF_REFERENCE_TO_NODE_CONNECTED_TO_IN_DATA].get_global_outgoing_id()

            self.equation.addAddend(weight, id_of_incoming_node)

        # finally set the equation to equation to 0 and add the equation to the input query
        self.equation.setScalar(-self.bias)
        self.global_data_manager.addEquation(self.equation)

        # finally set global_equation_is_valid to true since an equation and constraint were updated
        self.global_equation_is_valid = True

    def remove_equation_and_constraints(self):
        """
        simply remove the equation and constraint from the input query and marabou_core
        and sets them to none in this node
        """
        # from assumption (9) the equation and constraint should be set or removed together,
        # so its enough to check if the equation was set or not
        if self.equation == Node.NO_EQUATION:
            # not much to do, since no equation was set
            return

        self.global_data_manager.removeEquation(self.equation)
        if self.has_constraint:
            self.global_data_manager.removeReluConstraint(self.global_incoming_id, self.global_outgoing_id)

        self.equation = Node.NO_EQUATION
        self.has_constraint = False

        # finally set global_equation_is_valid to True since the equation and constraint were removed
        self.global_equation_is_valid = True

    def remove_from_global_system(self, return_id=True):
        """
        1) removes this node global ids
        2) if the node was given an equation and a constraint it removes them too.
        3) resets the reference to the marabou_core, input_query and id_manager to be null

        :param return_id: true by default, should not be changed unless you know what you're doing
        if its set to true, the function always returns -1,-1.
        otherwise, this function does not give back the ids of the node to the global system,
        but simply returns the pair of ids.
        notice that no matter what, the id should be clean when this function is finished,
        i.e. no bounds, relu constraints, or any other kind of things should be related to the id of this node.
        """
        if self.global_incoming_id == Node.NO_GLOBAL_ID or self.global_outgoing_id == Node.NO_GLOBAL_ID:
            if self.global_incoming_id == Node.NO_GLOBAL_ID and self.global_outgoing_id == Node.NO_GLOBAL_ID:
                # not much to do, since no global variables were set
                self.global_data_manager = Node.NO_REFERENCE
                return
            else:
                raise Exception("the node was given a only a 1 of the global_incoming_id, global_outgoing_id "
                                "when it should have received both")

        # to preserve assumption (10)
        # before giving back the ids remove all bounds, constraints and equations involving it
        if self.equation != Node.NO_EQUATION:
            # from assumption (9) the equation and constraint should be set or removed together,
            # so its enough to check if the equation was set or not
            self.remove_equation_and_constraints()

        if self.has_bounds:
            self.remove_node_bounds()
            self.has_bounds = False

        # since the give_id_back function does not clean the id, the id should be clean by this stage
        global_incoming_id_to_return = -1
        global_outgoing_id_to_return = -1
        if return_id:
            self.global_data_manager.give_id_back(self.global_incoming_id)
            if self.global_incoming_id != self.global_outgoing_id:
                self.global_data_manager.give_id_back(self.global_outgoing_id)
        else:
            global_incoming_id_to_return = self.global_incoming_id
            global_outgoing_id_to_return = self.global_outgoing_id

        self.global_incoming_id = Node.NO_GLOBAL_ID
        self.global_outgoing_id = Node.NO_GLOBAL_ID

        self.global_data_manager = Node.NO_REFERENCE

        return global_incoming_id_to_return, global_outgoing_id_to_return

    def refresh_global_variables(self, call_calculate_equation_and_constraints=True):
        """
        :param call_calculate_equation_and_constraints: true by default, if true this method calls the
        calculate_equation_and_constraints method after refreshing the global ids.
        if false, the node would remain without an equation or constraint after the refreshing has finished.

        :return:
        this function tries to removes this node from the global system and then reinsert it and recalculate an
        equation and constraint for the node.

        if the node has no global data and is not nested inside an arnode it raises an exception.

        otherwise, if the node has no global data and is nested inside an arnode this method does nothing
        and returns a reference to the arnode the node is nested in. this is because this method assumes that
        if such a case is met then we are fulfilling arnode assumption (8), i.e. this node has given up any
        authority to decide what the global variables are and the decision is entirely up to the arnode its nested in.

        otherwise, after the method is over it returns Node.NO_REFERENCE

        it assumes that this node currently has a valid global data manager
        it removes this node from the global system and then reinsert it
        if self.global_incoming_id != self.global_outgoing_id it will try to take 2 ids for itself
        otherwise it would try to take only 1

        note that after this function is finished, it calls each and every node which we are connected to via an
        outgoing connection, and tells it that its global data is not valid
        (we changed our id so the node which is outgoing from us has an invalid equation).
        as such when calling this function, to avoid inefficiency, if you need to also refresh nodes which we are
        connected to by an outgoing connection, its better to refresh us first, because else you will need to
        recalculate the equations for those nodes more than once.
        """
        if self.global_data_manager == Node.NO_REFERENCE or \
                self.global_incoming_id == Node.NO_GLOBAL_ID or self.global_outgoing_id == Node.NO_GLOBAL_ID:
            if self.is_nested_in_ar_node():
                # assumption (7)
                return self.get_pointer_to_ar_node_nested_in()
            else:
                raise Exception("this node has no global data and is not nested inside any arnode and as "
                                "such could not be refreshed")

        global_data_reference_backup = self.global_data_manager
        should_create_2_global_ids = (self.global_incoming_id != self.global_outgoing_id)
        self.remove_from_global_system()

        self.global_data_manager = global_data_reference_backup
        self.global_incoming_id = self.global_data_manager.get_new_id()
        self.global_outgoing_id = self.global_incoming_id
        if should_create_2_global_ids:
            self.global_outgoing_id = self.global_data_manager.get_new_id()

        if call_calculate_equation_and_constraints:
            self.calculate_equation_and_constraints()

        # now tell all our outgoing connections that their global data is invalid
        outgoing_connections_iter = self.get_iterator_for_connections_data(Node.OUTGOING_EDGE_DIRECTION)
        for connection_data in outgoing_connections_iter:
            node = connection_data[NodeEdges.INDEX_OF_REFERENCE_TO_NODE_CONNECTED_TO_IN_DATA]
            node.set_global_equation_to_invalid()

        return Node.NO_REFERENCE

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
            raise Exception("node is already nested in another ar_node. call reset_ar_node_nested_in before"
                            " calling this method")
        self.pointer_to_ar_node_nested_in = pointer_to_ar_node_nested_in

    def get_pointer_to_ar_node_nested_in(self):
        return self.pointer_to_ar_node_nested_in

    # when you implement this in cpp have another way to check if the pointer is valid. I remember we saw some way to
    # have the pointer be null or 0 in cpp
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

        finally, it sets global_equation_is_valid of all the nodes we are connected to by an outgoing connection
        to False
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

        if direction_of_connection == Node.INCOMING_EDGE_DIRECTION:
            # set global_equation_is_valid to False since an incoming connection data was edited and as
            # such if an equation was calculated before, it is now invalid
            # from assumption (8) the equation is affected only by incoming connections
            self.set_global_equation_to_invalid()

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

    def remove_neighbor_from_neighbors_list(self, direction_of_connection, neighbor_location_data,
                                            remove_this_node_from_given_node_neighbors_list=True):
        """
        :param direction_of_connection:
        :param neighbor_location_data:
        :param remove_this_node_from_given_node_neighbors_list: if true would delete this node from the given
        node neighbors (from the right direction of course)
        TAKE GREAT CARE WHEN YOU SET IT TO FALSE, IF YOU DO THAT YOU MUST NOT RELOCATE THIS NODE OR THE NODE YOU
        CONNECTED TO.

        this function also sets global_equation_is_valid to False
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

        # finally set global_equation_is_valid to False since a connection data was edited and as such if an equation
        # was calculated before, it is now invalid
        self.set_global_equation_to_invalid()

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
