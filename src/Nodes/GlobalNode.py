from src.Nodes.Node import Node
from src.NodeEdges import NodeEdges

"""
this class is the a wrapper around the node class which enables
the node class to also have global variables which relate to the marabou system
"""


class GlobalNode(Node):
    NO_GLOBAL_ID = -1
    # when you implement this in cpp have another way to check if the pointer is valid. I remember we saw some way to
    # have the pointer be null or 0 in cpp
    NO_EQUATION = Node.NO_REFERENCE
    NO_BIAS = 0

    def __init__(self,
                 number_of_tables_in_previous_layer,
                 number_of_tables_in_next_layer,
                 layer_number,
                 table_number, key_in_table,
                 bias,
                 global_incoming_id, global_outgoing_id,
                 global_data_manager):

        super().__init__(number_of_tables_in_previous_layer,
                         number_of_tables_in_next_layer,
                         layer_number,
                         table_number, key_in_table)
        # each node which is not an input or and output node would be represented by 2 system nodes, which would be
        # connected by a relu activation function. those nodes ids are given to the node as incoming_id and outgoing_id.
        # if a node is an input or output node, the incoming_id should be equal to the outgoing_id
        self.global_incoming_id = global_incoming_id
        self.global_outgoing_id = global_outgoing_id

        # this variable is important and should not be deleted until the end of the program
        self.node_is_inner = (global_incoming_id != global_outgoing_id)

        # each node would a reference to the global_data_manager object which is responsible for the system.
        # the node destructor would call it if need be
        self.global_data_manager = global_data_manager
        # note that in the process of creating and deleting arnodes, we would need the inner nodes
        # global_data_manager data, so we do not delete the reference to it when deleting all other global data

        # each node would manage the equation that links it to its incoming nodes
        # important note: this equation is solely the connection between this node and its incoming nodes
        self.equation = GlobalNode.NO_EQUATION
        # note that since the node is initialized without any neighbors, then from assumption (14) its equation is
        # considered valid. when we will add neighbors to it then its equation would no longer be valid
        # until recalculated

        self.bias = bias  # this variable it should not be deleted as long as
        # the node lives, because the arnodes which take over this node would use this node bias to calculate their own
        # bias

        # each node would manage the constraint between its 2 global IDs. if the ids are the same, no constraint would
        # be added
        self.has_constraint = False
        # if we set bounds on this node, this would be set to true
        self.has_bounds = False

    def destructor(self):
        super().destructor()

        # its actually better computationally to first remove all the neighbors and only then remove
        # yourself from the global system - that way you wont need to notice all the neighbors that youre
        # destroying yourself twice

        # finally, remove from the global system
        if self.global_incoming_id != GlobalNode.NO_GLOBAL_ID or self.global_outgoing_id != GlobalNode.NO_GLOBAL_ID:
            self.remove_id_equation_and_constraint()

    def get_global_incoming_id(self):
        return self.global_incoming_id

    def get_global_outgoing_id(self):
        return self.global_outgoing_id

    def check_if_node_is_inner(self):
        return self.node_is_inner

    def check_if_has_bounds(self):
        return self.has_bounds

    def check_if_node_equation_is_valid(self):
        return not self.global_data_manager.check_if_node_has_invalid_equations(self.layer_number,
                                                                                self.table_number,
                                                                                self.key_in_table,
                                                                                is_arnode=False)

    def set_global_equation_to_invalid(self):
        """
        for example, if an incoming neighbor changed its global id for some reason, then the equation we calculated
        is no longer correct
        """
        self.global_data_manager.add_location_of_node_that_dont_have_valid_equation(self.layer_number,
                                                                                    self.table_number,
                                                                                    self.key_in_table,
                                                                                    is_arnode=False)

    def _set_global_equation_to_valid(self):
        """
        for example, if an incoming neighbor changed its global id for some reason, then the equation we calculated
        is no longer correct
        """
        self.global_data_manager.remove_location_of_node_that_dont_have_valid_equation(self.layer_number,
                                                                                       self.table_number,
                                                                                       self.key_in_table,
                                                                                       is_arnode=False)

    def get_node_bias(self):
        return self.bias

    def set_node_bias(self, bias):
        self.bias = bias
        # no need to check if if self.equation == Node.NO_EQUATION, because if so then from assumption (14)
        # the node equation is valid only if the node has no neighbors
        if self.equation != GlobalNode.NO_EQUATION:
            # since we changed the bias the node equation is no longer correct
            self.set_global_equation_to_invalid()

    def check_if_have_global_id(self):
        return self.global_incoming_id != GlobalNode.NO_GLOBAL_ID and self.global_outgoing_id != GlobalNode.NO_GLOBAL_ID

    def set_lower_and_upper_bound(self, lower_bound, upper_bound):
        """
        sets lower and upper bound on the node global_incoming_id
        :param lower_bound:
        :param upper_bound:
        :return:
        """
        if self.global_incoming_id == GlobalNode.NO_GLOBAL_ID:
            raise Exception("can not set lower and upper bound without a valid global id")

        self.global_data_manager.setLowerBound(self.global_incoming_id, lower_bound)
        self.global_data_manager.setUpperBound(self.global_incoming_id, upper_bound)

        self.has_bounds = True

    def remove_node_bounds(self):
        if self.global_incoming_id == GlobalNode.NO_GLOBAL_ID:
            raise Exception("can not remove lower and upper bound without a valid global id")
        # for now this function does not exist, but I think that creating one should be ok, its just a map object
        # and we can delete form it at ease
        self.global_data_manager.removeBounds(self.global_incoming_id)

        self.has_bounds = False

    def remove_equation_and_constraint(self):
        """
        simply remove the equation and constraint from the global data manager
        and sets them to none in this node
        """
        # from assumption (9) the equation and constraint should be set or removed together,
        # so its enough to check if the equation was set or not
        if self.equation == GlobalNode.NO_EQUATION:
            # not much to do, since no equation was set
            return

        self.global_data_manager.removeEquation(self.equation)
        if self.has_constraint:
            self.global_data_manager.removeReluConstraint(self.global_incoming_id, self.global_outgoing_id)

        self.equation = GlobalNode.NO_EQUATION
        self.has_constraint = False

        if self.incoming_edges_manager.has_no_connections():
            # since we have no neighbors then our equation (which is non existent) is valid from assumption (14)
            self._set_global_equation_to_valid()
        else:
            self.set_global_equation_to_invalid()

    def calculate_equation_and_constraint(self):
        """
        this function calculates the equation between this node and its incoming nodes
        and the constraint between its 2 global ids

        if the equation and constraint already exist, it first deletes them and then recalculates them

        from assumption (9) the equation and constraint should be set or removed together
        """
        if self.global_incoming_id == GlobalNode.NO_GLOBAL_ID or self.global_outgoing_id == GlobalNode.NO_GLOBAL_ID:
            raise Exception("the node global id has been removed form it and as such could not be given an equation")

        # first check if they already exist and if so delete them
        if self.equation != GlobalNode.NO_EQUATION:
            # from assumption (9) the equation and constraint should be set or removed together,
            # so its enough to check if the equation was set or not
            self.remove_equation_and_constraint()

        # before starting, check if the node you are about to add an equation and constraint to is an inner
        # or an outer node. according to assumption (11) an outer node can only have 1 global id
        if not self.check_if_node_is_inner:
            self.has_constraint = False
            if self.incoming_edges_manager.has_no_connections():
                # we are in the input layer, no need to assign any equations since we dont have any incoming connections
                # also we dont need to have any constraints
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

        # finally tell the data manager that a valid equation were set for you
        self._set_global_equation_to_valid()

    def remove_id_equation_and_constraint(self, give_back_id_to_data_manager=True):
        """
        deletes some of the global variables

        1) removes this node global ids
        2) if the node was given an equation and a constraint it removes them too.

        :param give_back_id_to_data_manager: true by default, should not be changed unless you know what you're doing
        if its set to true, the function always returns -1,-1.
        otherwise, this function does not give back the ids of the node to the global manager,
        but simply returns the pair of ids.
        notice that no matter what, the id should be clean when this function is finished,
        i.e. no bounds, relu constraints, or any other things should be related to the id of this node.
        """
        if self.global_incoming_id == GlobalNode.NO_GLOBAL_ID or self.global_outgoing_id == GlobalNode.NO_GLOBAL_ID:
            if self.global_incoming_id == GlobalNode.NO_GLOBAL_ID and self.global_outgoing_id == GlobalNode.NO_GLOBAL_ID:
                # not much to do, since no global variables were set
                return
            else:
                raise Exception("the node was given a only a 1 of the global_incoming_id, global_outgoing_id "
                                "when it should have received both")

        # to preserve assumption (10)
        # before giving back the ids remove all bounds, constraints and equations involving it
        if self.equation != GlobalNode.NO_EQUATION:
            # from assumption (9) the equation and constraint should be set or removed together,
            # so its enough to check if the equation was set or not
            self.remove_equation_and_constraint()

        if not self.check_if_node_equation_is_valid():
            # since our global data is removed, our equation is considered valid from assumption (15)
            self._set_global_equation_to_valid()

        if self.has_bounds:
            self.remove_node_bounds()
            self.has_bounds = False

        # since the give_id_back function does not "clean" the id, the id should be clean by this stage
        # unless the programmer has made a mistake

        global_incoming_id_to_return = -1
        global_outgoing_id_to_return = -1
        if give_back_id_to_data_manager:
            self.global_data_manager.give_id_back(self.global_incoming_id)
            if self.global_incoming_id != self.global_outgoing_id:
                self.global_data_manager.give_id_back(self.global_outgoing_id)
        else:
            global_incoming_id_to_return = self.global_incoming_id
            global_outgoing_id_to_return = self.global_outgoing_id

        self.global_incoming_id = GlobalNode.NO_GLOBAL_ID
        self.global_outgoing_id = GlobalNode.NO_GLOBAL_ID

        return global_incoming_id_to_return, global_outgoing_id_to_return

    def _add_or_edit_neighbors_helper(self, direction_of_connection, list_of_connection_data,
                                      add_this_node_to_given_node_neighbors=True):

        super()._add_or_edit_neighbors_helper(direction_of_connection, list_of_connection_data,
                                              add_this_node_to_given_node_neighbors)

        if direction_of_connection == Node.INCOMING_EDGE_DIRECTION:
            # an incoming connection data was edited and as such if an equation was calculated before, it is now invalid
            # from assumption (8) the equation is affected only by incoming connections
            self.set_global_equation_to_invalid()

    def remove_neighbor_from_neighbors_list(self, direction_of_connection, neighbor_location_data,
                                            remove_this_node_from_given_node_neighbors_list=True):

        super().remove_neighbor_from_neighbors_list(direction_of_connection, neighbor_location_data,
                                                    remove_this_node_from_given_node_neighbors_list)

        if direction_of_connection == Node.INCOMING_EDGE_DIRECTION:
            if self.incoming_edges_manager.has_no_connections():
                # assumption (14)
                self._set_global_equation_to_valid()
            else:
                # an incoming connection data was edited and as such if an equation was calculated before,
                # it is now invalid from assumption (8) the equation is affected only by incoming connections
                self.set_global_equation_to_invalid()
