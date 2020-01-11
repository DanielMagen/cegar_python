from src.Layer import *
from src.GlobalDataManager import *


class Network:
    # note that we use N(x) and y interchangeably
    # we wish to verify either that that the network output is larger than or smaller than
    # a number. ">" would mean that we want to verify y > c and
    # "<" would mean that we want to verify y < c
    # note that we try to find a counter example to the property we want to verify
    # so if we want to verify that y > c we would search for an input which gives us y<=c
    POSSIBLE_VERIFICATION_GOALS = ['>', '<']

    # ratio between number of initial nodes to available ids
    MULTIPLICITY_OF_IDS = 20  # arbitrarily set it to 20

    LOCATION_OF_FIRST_LAYER = 0

    """
    the idea is such:
    if we want to verify that y > c we would search for an input which gives us y <= c
    i.e. that N(x)=y <= c
    so we will create N' such that N(x) <= N'(x)
    and as such N'(x) <= c --> N(x) <= c

    so if we want to verify that y > c we will enlarge the output of the network
    and if we want to verify that y < c we will dwindle the output of the network
    """
    UNINITIALIZED_GOAL_INDEX = -1
    INDEX_OF_NEED_TO_INCREASE_OUTPUT = POSSIBLE_VERIFICATION_GOALS.index('>')
    INDEX_OF_NEED_TO_DECREASE_OUTPUT = POSSIBLE_VERIFICATION_GOALS.index('<')

    POSSIBLE_GOALS = [INDEX_OF_NEED_TO_INCREASE_OUTPUT, INDEX_OF_NEED_TO_DECREASE_OUTPUT]

    NUMBER_OF_TABLES_IN_LAYER = Layer.NUMBER_OF_OVERALL_TABLES

    def __init__(self, AcasNnet_object, which_acas_output):
        """
        :param AcasNnet_object:
        an AcasNnet object which has loaded into itself the network and the requested bounds on the network input nodes.
        this network class would convert that network into an inner representation of multiple layers, tables and
        node classes, which are built for the purpose of supporting the abstraction refinement


        :param which_acas_output:
        for now the network class does not support adding arbitrary output bounds (for cegar to work on such bounds
        the network class would need to convert the bounds to a single bound of the form >).
        we do support adding the output bounds for the AcasNnet, which are hardcoded into this class.
        """
        self.number_of_layers_in_network = len(AcasNnet_object.layerSizes)

        self.global_data_manager = GlobalDataManager(Network.MULTIPLICITY_OF_IDS * self.number_of_nodes_in_network)

        self.layers = [None for _ in range(self.number_of_layers_in_network)]
        self._initialize_layers()

        # all layers in the network are not preprocessed
        # note that currently we do not use the full potential of the layer class capabilities
        # the layer class can be preprocessed, forward activated and fully activated with much more finer control
        # but for now we treat the layers as a single block that need to change states all at once
        self.last_layer_not_preprocessed = len(self.layers) - 1
        self.last_layer_not_forward_activated = len(self.layers) - 1
        self.last_layer_not_fully_activated = len(self.layers) - 1

        # now create all the nodes in the network
        self.number_of_nodes_in_network = 0
        self._initialize_nodes_in_all_layers(AcasNnet_object)

        # for now the goal of the network would always be to increase its output
        self.goal_index = Network.UNINITIALIZED_GOAL_INDEX
        # this function would set self.goal_index to either
        # INDEX_OF_NEED_TO_INCREASE_OUTPUT or INDEX_OF_NEED_TO_DECREASE_OUTPUT
        self.hard_code_acas_output_properties(which_acas_output)

        # finally, before starting to act upon the Network, save the starting network
        # state as the state that would be used to check possible sat solutions
        self.global_data_manager.save_current_input_query_as_original_network()

    def _initialize_layers(self):
        self.layers[0] = Layer(self.global_data_manager, Layer.NO_POINTER_TO_ADJACENT_LAYER,
                               Layer.NO_POINTER_TO_ADJACENT_LAYER)

        for i in range(1, len(self.layers)):
            self.layers[i] = self.layers[i - 1].create_next_layer()

    def _initialize_nodes_in_all_layers(self, AcasNnet_object):
        """
        :param AcasNnet_object:
        creates all the nodes, their relations, their bounds, equations and constraints
        """
        LOCATION_OF_WEIGHTS = 0
        LOCATION_OF_BIASES = 0

        matrix = AcasNnet_object.getMatrix()

        def get_bias_for_node(layer_number, index_in_layer_of_node):
            """
            :param layer_number:
            :param index_in_layer_of_node:
            :return: the bias for the (index_in_layer_of_node)th node in the given layer
            """
            if layer_number == Network.LOCATION_OF_FIRST_LAYER:
                return Node.NO_BIAS
            return matrix[layer_number - 1][LOCATION_OF_BIASES][index_in_layer_of_node][0]

        def get_weight_of_connection(layer_number, index_in_layer_of_node, index_in_previous_layer_of_node):
            """
            :param layer_number:
            :param index_in_layer_of_node:
            :param index_in_previous_layer_of_node:
            :return: the weight of connection between (index_in_layer_of_node)th node in the given layer
            and (index_in_next_layer_of_node)th node in the previous layer
            """
            return matrix[layer_number][LOCATION_OF_WEIGHTS][index_in_layer_of_node][index_in_previous_layer_of_node]

        # first, initialize all the nodes and their connections

        # those maps would map between index of the node in the conceptual layer (as given by the matrix)
        # to the key of the node in the unprocessed_table in the layer object
        # from assumption (2) all nodes created would be added to the unprocessed table of the layer so its enough to
        # save those keys, since we wont move any nodes before finishing creating the entire network
        current_layer_nodes_map = {}
        previous_layer_nodes_map = {}

        # save the first layer map for later,we'll need it
        first_layer_nodes_map = {}

        for current_layer_number in range(len(self.layers)):
            current_layer = self.layers[current_layer_number]
            number_of_nodes_in_current_layer = AcasNnet_object.layerSizes[current_layer_number]

            # first create all the nodes in the layer
            for current_node_number in range(number_of_nodes_in_current_layer):
                current_layer_nodes_map[current_node_number] = current_layer.create_new_node(
                    get_bias_for_node(current_layer_number, current_node_number))

            # next connect all those nodes, to the nodes from the previous layer
            # we do not connect nodes which are connected to each other with 0 weight
            for current_node_index_in_layer, current_node_key_in_unprocessed_table in current_layer_nodes_map.items():
                list_of_pairs_of_keys_and_weights = []
                for a_node_index_in_previous_layer, the_key_in_unprocessed_table_of_node_in_previous_layer \
                        in previous_layer_nodes_map.items():
                    weight_of_connection = get_weight_of_connection(current_layer_number,
                                                                    current_node_index_in_layer,
                                                                    a_node_index_in_previous_layer)
                    if weight_of_connection != 0:
                        list_of_pairs_of_keys_and_weights.append(
                            (the_key_in_unprocessed_table_of_node_in_previous_layer,
                             weight_of_connection))

                # finally add all the connections to the current node
                current_layer.add_or_edit_neighbors_to_node_in_unprocessed_table_by_bulk(
                    current_node_key_in_unprocessed_table,
                    Layer.INCOMING_LAYER_DIRECTION,
                    list_of_pairs_of_keys_and_weights)

            # after finishing creating all connections between this layer and the previous one,
            # set previous_layer_nodes_map to be current_layer_nodes_map before continuing the loop
            previous_layer_nodes_map = current_layer_nodes_map
            current_layer_nodes_map = {}

            if current_layer_number == Network.LOCATION_OF_FIRST_LAYER:
                first_layer_nodes_map = previous_layer_nodes_map

        # first create the bounds on all input nodes which reside in layer 0
        first_layer = self.layers[Network.LOCATION_OF_FIRST_LAYER]
        is_arnode = False
        table_number = Layer.INDEX_OF_UNPROCESSED_TABLE
        lower_bounds = AcasNnet_object.mins
        upper_bounds = AcasNnet_object.maxes

        for node_index_in_layer, node_key_in_unprocessed_table in first_layer_nodes_map.items():
            first_layer.set_lower_and_upper_bound_for_node(is_arnode, table_number,
                                                           node_key_in_unprocessed_table,
                                                           lower_bounds[node_index_in_layer],
                                                           upper_bounds[node_index_in_layer])

        # now create the equations for all the nodes
        # we dont create an equation for the input nodes
        # since all nodes still reside in the unprocessed table we create the equations and constraints only for them
        is_arnode = False
        table_number = Layer.INDEX_OF_UNPROCESSED_TABLE
        for i in range(Network.LOCATION_OF_FIRST_LAYER + 1, len(self.layers)):
            self.layers[i].calculate_equation_and_constraints_for_all_nodes_in_table(is_arnode, table_number)

    #################################################################################################################################################################
    def hard_code_acas_output_properties(self, which_acas_output):
        """
        sent a mail to guy in 10.1 asking him which set of properties to hardcode

        :param which_acas_output:
        which of the 4/11 properties should be added to the network

        this function would set self.goal_index to either
        INDEX_OF_NEED_TO_INCREASE_OUTPUT or INDEX_OF_NEED_TO_DECREASE_OUTPUT
        """
        # TODO implement
        pass

    def preprocess_more_layers(self, number_of_layers_to_preprocess, raise_error_if_overflow=False):
        """
        :param number_of_layers_to_preprocess:
        preprocess 'number_of_layers_to_preprocess' network layers which were not already preprocessed
        the preprocess procedure is carried from end to start

        :param raise_error_if_overflow: is set to false by default.
        if true, the function would raise an exception if
        last_layer_not_preprocessed - number_of_layers_to_preprocess < -1
        i.e. it would raise an exception if the number of requested layers to activate is more than those which are
        left.
        if its false, it simply preprocess as many layers as it can. note that this number could be 0.
        """
        up_to = self.last_layer_not_preprocessed - number_of_layers_to_preprocess
        if raise_error_if_overflow:
            if up_to < -1:
                raise Exception("requested to preprocess more layers than there are available")

        for i in range(self.last_layer_not_preprocessed,
                       max(-1, up_to), -1):
            self.layers[i].preprocess_entire_layer()
            self.last_layer_not_preprocessed -= 1

    def forward_activate_more_layers(self, number_of_layers_to_forward_activate, raise_error_if_overflow=False):
        """
        :param number_of_layers_to_forward_activate:
        forward activates 'number_of_layers_to_forward_activate' network layers which were not already forward activated
        the forward activation procedure is carried from end to start

        :param raise_error_if_overflow: is set to false by default.
        if true, the function would raise an exception if
        we request to forward activate more layers than there are available.
        layers are available for forward activation only if they have been preprocessed before.

        if its false, it simply forward activates as many layers as it can. note that this number could be 0.

        """
        up_to = self.last_layer_not_forward_activated - number_of_layers_to_forward_activate
        if raise_error_if_overflow:
            if up_to < self.last_layer_not_preprocessed:
                raise Exception("requested to forward activate more layers than there are available")

        for i in range(self.last_layer_not_forward_activated,
                       max(self.last_layer_not_preprocessed, up_to), -1):
            current_layer = self.layers[i]
            for table_number in Layer.OVERALL_ARNODE_TABLES:
                function_to_calculate_merger_of_outgoing_edges = self. \
                    get_function_to_calc_weight_for_outgoing_edges_for_arnode(table_number)
                current_layer.forward_activate_arnode_table(
                    table_number,
                    function_to_calculate_merger_of_outgoing_edges)

            self.last_layer_not_forward_activated -= 1

    def fully_activate_more_layers(self, number_of_layers_to_fully_activate,
                                   raise_error_if_overflow=False):
        """
        :param number_of_layers_to_fully_activate:
        fully activates 'number_of_layers_to_fully_activate' network layers which were not already fully activated
        the full activation procedure is carried from end to start

        :param raise_error_if_overflow: is set to false by default.
        if true, the function would raise an exception if
        we request to fully activate more layers than there are available.
        layers are available for full activation only if they and the layer immediately prior to them have been
        forward activated before.
        also note that the input layer should never be fully activated (to preserve assumption (3)), so
        trying to fully activate it would count as something that we would raise an error about.

        if its false, it simply fully activates as many layers as it can. note that this number could be 0.
        """
        up_to = self.last_layer_not_fully_activated - number_of_layers_to_fully_activate
        if raise_error_if_overflow:
            # to be fully activated a layer needs to have the layer before it forward activated, hence the +1
            if up_to < self.last_layer_not_forward_activated + 1:
                raise Exception("requested to fully activate more layers than there are available")
            elif up_to == -1:
                # i.e. te user wants to fully activate the input which is forbidden according to assumption (3)
                raise Exception("requested to fully activate more layers than there are available")

        # in a bit of serendipity, the fact that we allow only layers to be fully activated if
        # their immediate previous layer has been forward activate, means that the input layer could never be
        # fully activated, because the "previous layer to it" (which does not exist), have not been forward activated,
        # this comes into effect in the '+ 1' in the loop.
        # to preserve assumption (3) the input layer could never be fully activated.
        for i in range(self.last_layer_not_fully_activated,
                       max(self.last_layer_not_forward_activated + 1, up_to), -1):
            current_layer = self.layers[i]
            for table_number in Layer.OVERALL_ARNODE_TABLES:
                # since this is the first time the arnode is being activated (we are not activating a node which was
                # just split or merged), we don't need to recalculate the incoming edges to the arnode, those were
                # calculated by the arnodes which were forward activated
                current_layer.fully_activate_table_without_changing_incoming_edges(
                    table_number,
                    self.get_function_to_calc_bias_for_arnode(table_number),
                    check_validity_of_activation=True)

            self.last_layer_not_fully_activated -= 1

    """
    we would merge nodes with the same type of positivity/incrementality in a way that would
    enlarge/dwindle the network output according to the needed goal.
    each such merged group of nodes is called an arnode.
    we need to calculate the incoming and outgoing edges that are directed towards the arnodes which
    might contain a multiplicity of inner nodes.
    this calculation is dependent on the positivity/incrementality of the arnode, which is turn
    is dependent on the table its in in its layer.
    
    the 2 functions below are used to give us the basic functions to calculate the weight
    of the arnode edges based on their type and the network goal_index
    """

    def get_function_to_calc_weight_for_incoming_edges_for_arnode(self,
                                                                  table_number_of_arnode):
        """
        this function returns the function that is given to the arnode to calculate
        its incoming edges from the edges of its inner nodes.
        this function can be fed into all the arnodes functions that require a
        "function_to_calculate_merger_of_incoming_edges"

        :param table_number_of_arnode: one of
        Layer.INDEX_OF_POS_INC_TABLE
        Layer.INDEX_OF_POS_DEC_TABLE
        Layer.INDEX_OF_NEG_INC_TABLE
        Layer.INDEX_OF_NEG_DEC_TABLE

        :return:
        a function that receives 2 inputs
        1) a reference to an arnode
        2) a list of weights we are connected to the arnode with
        and returns a new weight for that we will connect to the given arnode with

        for example if we want to increase the network output and we have a group of incremental nodes then we will
        return a function of the form
        lambda node, list: max(lis)
        """
        if table_number_of_arnode in [Layer.INDEX_OF_POS_INC_TABLE, Layer.INDEX_OF_NEG_INC_TABLE]:
            arnode_is_inc_type = True
        elif table_number_of_arnode in [Layer.INDEX_OF_POS_DEC_TABLE, Layer.INDEX_OF_NEG_DEC_TABLE]:
            arnode_is_inc_type = False
        else:
            raise ValueError('given table number is invalid')

        if self.goal_index == Network.INDEX_OF_NEED_TO_INCREASE_OUTPUT:
            if arnode_is_inc_type:
                return lambda node, lis: max(lis)
            return lambda node, lis: min(lis)

        else:
            # self.goal_index == Network.INDEX_OF_NEED_TO_DECREASE_OUTPUT
            if arnode_is_inc_type:
                return lambda node, lis: min(lis)
            return lambda node, lis: max(lis)

    def get_function_to_calc_weight_for_outgoing_edges_for_arnode(self,
                                                                  table_number_of_arnode):
        """
        this function returns the function that is given to the arnode to calculate
        its outgoing edges from the edges of its inner nodes.
        this function can be fed into all the arnodes functions that require a
        "function_to_calculate_merger_of_outgoing_edges"

        :param table_number_of_arnode: one of
        Layer.INDEX_OF_POS_INC_TABLE
        Layer.INDEX_OF_POS_DEC_TABLE
        Layer.INDEX_OF_NEG_INC_TABLE
        Layer.INDEX_OF_NEG_DEC_TABLE

        :return:
        a function that receives 2 inputs
        1) a reference to an arnode
        2) a list of weights we are connected to the arnode with
        and returns a new weight for that we will connect to the given arnode with
        """
        # for now it seems that the function is sum all the times
        return lambda node, lis: sum(lis)

    ######################## ask Yithzak about this
    def get_function_to_calc_bias_for_arnode(self,
                                             table_number_of_arnode):
        def function_to_calc_bias_for_arnode(list_of_inner_nodes):
            if len(list_of_inner_nodes) == 1:
                return list_of_inner_nodes[0].get_node_bias()
            return 0

        return function_to_calc_bias_for_arnode

    def decide_best_arnodes_to_merge(self):
        """
        this is my efficient implementation of algorithm 2 "create initial abstraction"
        the problem with the original psudo code is that its working backwards, for each pair
        of arnodes it finds an arnode which is connected to both of them and continues from there.
        its fine if the network is fully connected. but my implementation does not assume that,
        so it would be costly to go "for each pair of arnodes find the intersection of the arnodes
        they are connected to using incoming connections". so instead I go the other way around. to check what arnodes
        should be merged in layer k I look at layer k-1, and for each node a in layer k-1, for each pair of arnodes
        its connected to by an outgoing connection.

        :return:
        the attributes needed to know which arnodes to merge
        a layer number
        a table number
        a list_of_keys_of_arnodes_to_merge inside this table
        """
        # the output arnode wont be merged to preserve assumption (4) so we check to see if we fully activated
        # a layer before the output layer
        if self.last_layer_not_fully_activated >= len(self.layers) - 2:
            raise Exception("can not decide which arnodes to merge since not enough layers are "
                            "fully activated")

        # to preserve assumption (4) we should't check if (or even try to) merge arnodes in the output or input layers.
        # in this implementation, to check what arnodes should be merged in layer k I look at layer k-1.
        # so when you do the math, I must go through a loop from len(self.layers) - 3 (the second layer from the last)
        # up to (and including) self.last_layer_not_fully_activated. since the loop is exclusive up to
        # self.last_layer_not_fully_activated - 1.
        # from assumption (3) we know that self.last_layer_not_fully_activated must be at least 0, so the loop is
        # sound, I will never go below 0. this also means that that we wont ever try to merge or split the input layer
        # (since if we wanted to act upon layer 0 we need to use layer -1 which does not exist)
        # so assumption (4) is again preserved

        best_pair = None
        best_pair_m = float("inf")  # m would indicate maximum difference between weights.
        layer_of_best_pair = -1
        # i.e. weight of a->ar1 and weight of a->ar2 would differ most.
        for i in range(len(self.layers) - 3, self.last_layer_not_fully_activated - 1, -1):
            assert i > -1  # just in case, but it should never happen
            current_layer_number = i + 1
            previous_layer = self.layers[i]
            # I would save a map that would tell me for each pair of nodes in the current_layer the value of m
            # a pair would be accessible using (table_num1, index_in_table1, table_num2, index_in_table2)
            map_of_pairs_to_m = {}

            for table_number in Layer.OVERALL_ARNODE_TABLES:
                for arnode in previous_layer.get_iterator_for_all_nodes_for_table(True, table_number):
                    for connection_data_pair in arnode.get_combinations_iterator_over_connections(
                            Node.OUTGOING_EDGE_DIRECTION, 2):

                        connection_data_1, connection_data_2 = connection_data_pair
                        weight_of_connection_1 = connection_data_1[NodeEdges.INDEX_OF_WEIGHT_IN_DATA]
                        weight_of_connection_2 = connection_data_2[NodeEdges.INDEX_OF_WEIGHT_IN_DATA]

                        # note that at this point we assume that arnodes in one type of table (for example pos-inc)
                        # connects only to arnodes that reside in the same type of table
                        # I'm sure it should follow from the layer assumptions.
                        # if you disagree you could assert that the table number as returned
                        # in the connection data, is never changing and always equal to Layer.INDEX_OF_POS_INC_TABLE

                        """
                        if you wish to test
                        assert connection_data_1[NodeEdges.INDEX_OF_TABLE_NUMBER_IN_DATA] == \
                               weight_of_connection_2[NodeEdges.INDEX_OF_TABLE_NUMBER_IN_DATA] == table_number
                        """

                        m = abs(weight_of_connection_1 - weight_of_connection_2)

                        key_of_pair_in_map_of_pairs = (connection_data_1[NodeEdges.INDEX_OF_TABLE_NUMBER_IN_DATA],
                                                       connection_data_1[NodeEdges.INDEX_OF_KEY_IN_TABLE_IN_DATA],
                                                       connection_data_2[NodeEdges.INDEX_OF_TABLE_NUMBER_IN_DATA],
                                                       connection_data_2[NodeEdges.INDEX_OF_KEY_IN_TABLE_IN_DATA])

                        if key_of_pair_in_map_of_pairs not in map_of_pairs_to_m:
                            map_of_pairs_to_m[key_of_pair_in_map_of_pairs] = m
                        elif m > map_of_pairs_to_m[key_of_pair_in_map_of_pairs]:
                            map_of_pairs_to_m[key_of_pair_in_map_of_pairs] = m

            # now search map_of_pairs_to_m for the best pair
            best_pair_in_layer = None
            m_of_best_pair_in_layer = float("inf")  # infinity
            for current_pair, m_of_current_pair in map_of_pairs_to_m.items():
                if m_of_current_pair < m_of_best_pair_in_layer:
                    m_of_best_pair_in_layer = m_of_current_pair
                    best_pair_in_layer = current_pair

            # now compare the best pair from this layer to the best pair overall
            if m_of_best_pair_in_layer < best_pair_m:
                best_pair_m = m_of_best_pair_in_layer
                best_pair = best_pair_in_layer
                layer_of_best_pair = current_layer_number

        # now you have the best pair to merge in the network so return the pair attributes
        # best_pair data is of the form (table_num1, index_in_table1, table_num2, index_in_table2)
        # and they should have the same table number
        table_number = best_pair[1]
        pairs_indices_in_table = [best_pair[0], best_pair[2]]

        return layer_of_best_pair, table_number, pairs_indices_in_table

    def run_cegar(self):
        result = self.global_data_manager.verify()
        if result == GlobalDataManager.UNSAT:
            return result

        result_is_valid = self.global_data_manager. \
            evaluate_if_result_of_last_solution_attempt_is_a_valid_counterexample()

        if result_is_valid:
            return GlobalDataManager.SAT
