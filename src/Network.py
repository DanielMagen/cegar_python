from src.Layer import Layer
from src.MarabouDataManagers.GlobalNetworkManager import GlobalNetworkManager
from src.NodeEdges import NodeEdges
from src.Nodes.GlobalNode import GlobalNode


class Network:
    # note that we use N(x) and y interchangeably
    # we wish to verify either that that the network output is larger than or smaller than
    # a number. ">" would mean that we want to verify y > c and
    # "<" would mean that we want to verify y < c
    # note that we try to find a counter example to the property we want to verify
    # so if we want to verify that y > c we would search for an input which gives us y<=c

    # if we want to verify that N(x) > c,
    # then we would create create a network N' such that N(x) >= N'(x)
    # if we can manage to prove that N'(x) > c we are done since this would mean that c < N'(x) <= N(x)
    # so what we need to do is to verify that N'(x) <= c is unsat
    #
    # so to summarize,
    # if we want to make sure that y < c, i.e. we want to unsat y >= c, we need to increase the output of the network.
    # the same hold for the opposite case,
    # if we want to make sure that y > c, i.e. we want to unsat y <= c, we need to decrease the output of the network.
    # in his paper, yitzhak always assumed that the goal would always be to increase the output.
    # so for now we only support this option.
    # one problem with supporting the other option is that the algorithms to decide which nodes to split or merge
    # might depend on the verification goal of the network (<= >=).
    # in this case I don't know how to change the algorithms to preserve their correctness
    # another thing that needs to be done to support this option is to change
    # get_function_to_calc_weight_for_incoming_edges_for_arnode slightly

    NUMBER_OF_TABLES_IN_LAYER = Layer.NUMBER_OF_OVERALL_TABLES

    # obvious, but I put it here to emphasize that this shouldn't change by any means
    LOCATION_OF_FIRST_LAYER = 0

    CODE_FOR_SAT = 0
    CODE_FOR_UNSAT = 1
    CODE_FOR_SPURIOUS_COUNTEREXAMPLE = 2

    def __init__(self, nnet_reader_object, which_acas_output):
        """
        :param nnet_reader_object:
        an nnet_reader object which has loaded into itself the network and the requested bounds on the network
        input nodes.
        this network class would convert that nnet_reader_object into an inner representation of multiple layers,
        tables and node classes, which are built for the purpose of supporting the abstraction refinement


        :param which_acas_output:
        for now the network class does not support adding arbitrary output bounds (for cegar to work on such bounds
        the network class would need to convert the bounds to a form that cegar know how to deal with, a task which was
        not covered in the paper).
        however, we do support adding the output bounds for the AcasNnet, which are hardcoded into this class.
        """
        self.global_network_manager = GlobalNetworkManager()

        self.layers = []
        # more layers can be added later since we might need to change the output to fit cegar expected network
        self._initialize_layers(nnet_reader_object)

        first_layer_nodes_map, last_layer_nodes_map = self._initialize_nodes_in_all_layers(nnet_reader_object)

        # we need to know what are the global ids of the input and output nodes
        # we can use the maps that were returned by the _initialize_nodes_in_all_layers function to get those ids
        # for the input nodes, those ids can be extracted immediately
        # but the output nodes might still change a bit in the hard_code_acas_output_properties so we wait until the
        # call to the hard_code_acas_output_properties to get the output node global ids
        input_nodes_global_incoming_ids = self._layer_node_map_to_global_ids(Network.LOCATION_OF_FIRST_LAYER,
                                                                             first_layer_nodes_map)

        self.output_bounds_were_set = False
        output_nodes_global_incoming_ids = self.hard_code_acas_output_properties(last_layer_nodes_map,
                                                                                 which_acas_output)

        # all layers in the network are not preprocessed (all nodes are in the unprocessed tables)
        # note in the current implementation we do not use the full potential of the layer class capabilities
        # the layer class can be preprocessed, forward activated and fully activated with much finer control
        # but for now we treat the layers as a single block that need to change the states of its nodes all at once
        self.last_layer_not_preprocessed = len(self.layers) - 1
        self.last_layer_not_forward_activated = len(self.layers) - 1
        self.last_layer_not_fully_activated = len(self.layers) - 1

        # finally, before starting to act upon the Network, save the starting network
        # state as the state that would be used to check possible sat solutions
        if not self.output_bounds_were_set:
            # violation of assumption (5)
            raise AssertionError("the output bounds were not set")

        self._create_valid_equations_for_all_nodes_without_valid_equations()
        self.global_network_manager.save_current_network_as_original_network(input_nodes_global_incoming_ids,
                                                                             output_nodes_global_incoming_ids)

    def _layer_node_map_to_global_ids(self, layer_number, layer_nodes_map):
        """
        :param layer_number:
        :param layer_nodes_map:
        map between index of the node in the conceptual layer (as given by the nnet_reader_object)
        to the key of the node in the unprocessed_table in the layer object

        :return: a list of the incoming global ids of the nodes in the map given
        """
        to_return = []
        current_layer = self.layers[layer_number]
        # we don't need the index of the node in the conceptual layer
        for _, key_in_the_unprocessed_table in layer_nodes_map.items():
            node = current_layer.get_unprocessed_node_by_key(key_in_the_unprocessed_table)
            to_return.append(node.get_global_incoming_id)

        return to_return

    def _initialize_layers(self, nnet_reader_object):
        number_of_layers_in_network = nnet_reader_object.get_number_of_layers_in_network()

        first_layer = Layer(Network.LOCATION_OF_FIRST_LAYER,
                            self.global_network_manager,
                            Layer.NO_POINTER_TO_ADJACENT_LAYER,
                            Layer.NO_POINTER_TO_ADJACENT_LAYER)
        self.layers.append(first_layer)
        # at this point we assert self.layers.index(first_layer) == Network.LOCATION_OF_FIRST_LAYER

        for i in range(1, number_of_layers_in_network + 1):
            self.layers.append(self.layers[i - 1].create_next_layer())

    def _initialize_nodes_in_all_layers(self, nnet_reader_object):
        """
        this function creates all the nodes along with their relations, bounds, equations and constraints
        :param nnet_reader_object:

        :return: 2 maps, 1 for the input nodes and 1 for the output nodes.
        those maps would map between index of the node in the conceptual layer (as given by the nnet_reader_object)
        to the key of the node in the unprocessed_table in the layer object
        """
        # those maps would map between index of the node in the conceptual layer (as given by the nnet_reader_object)
        # to the key of the node in the unprocessed_table in the layer object
        # from assumption (2) every node created would be added to the unprocessed table of its layer so its enough to
        # save those keys, since we wont move any node to other tables before finishing creating the entire network
        current_layer_nodes_map = {}
        previous_layer_nodes_map = {}

        # save the first and last layer maps for later, we'll need them
        first_layer_nodes_map = {}
        last_layer_nodes_map = {}

        # first, initialize all the nodes and their connections
        for current_layer_number in range(len(self.layers)):
            current_layer = self.layers[current_layer_number]
            number_of_nodes_in_current_layer = nnet_reader_object.get_number_of_nodes_in_layer(current_layer_number)

            # first create all the nodes in the layer
            for current_node_number_in_conceptual_layer in range(number_of_nodes_in_current_layer):
                bias_for_new_node = nnet_reader_object.get_bias_for_node(current_layer_number,
                                                                         current_node_number_in_conceptual_layer)
                current_layer_nodes_map[current_node_number_in_conceptual_layer] = current_layer.create_new_node(
                    bias_for_new_node)

            # next connect all the nodes in the current layer to the nodes from the previous layer
            # we do not connect nodes which are connected to each other with weight 0
            for current_node_index_in_conceptual_layer, current_node_key_in_unprocessed_table in current_layer_nodes_map.items():
                # go over each node in the current layer and create a list of all its connections to
                # nodes in the previous layer
                list_of_pairs_of_keys_and_weights = []
                for a_node_index_in_previous_layer, the_key_in_unprocessed_table_of_node_in_previous_layer \
                        in previous_layer_nodes_map.items():
                    weight_of_connection = nnet_reader_object.get_weight_of_connection(current_layer_number,
                                                                                       current_node_index_in_conceptual_layer,
                                                                                       a_node_index_in_previous_layer)
                    if weight_of_connection != 0:
                        list_of_pairs_of_keys_and_weights.append(
                            (the_key_in_unprocessed_table_of_node_in_previous_layer,
                             weight_of_connection))

                # now that we have a list of weights, add all the connections to the current node
                current_layer.add_or_edit_neighbors_to_node_in_unprocessed_table_by_bulk(
                    current_node_key_in_unprocessed_table,
                    Layer.INCOMING_LAYER_DIRECTION,
                    list_of_pairs_of_keys_and_weights)

            # now we finished creating all connections between this layer and the previous one
            if current_layer_number == Network.LOCATION_OF_FIRST_LAYER:
                first_layer_nodes_map = current_layer_nodes_map
            if current_layer_number == len(self.layers) - 1:
                last_layer_nodes_map = current_layer_nodes_map

            # set previous_layer_nodes_map to be current_layer_nodes_map before continuing the loop
            previous_layer_nodes_map = current_layer_nodes_map
            current_layer_nodes_map = {}

        # at this point we created all the nodes and their connections
        # now create the bounds on all input nodes (which reside in layer 0)
        first_layer = self.layers[Network.LOCATION_OF_FIRST_LAYER]
        is_arnode = False
        table_number = Layer.INDEX_OF_UNPROCESSED_TABLE
        lower_bounds = nnet_reader_object.inputMinimums
        upper_bounds = nnet_reader_object.inputMaximums

        for node_index_in_conceptual_layer, node_key_in_unprocessed_table in first_layer_nodes_map.items():
            first_layer.set_lower_and_upper_bound_for_node(is_arnode, table_number,
                                                           node_key_in_unprocessed_table,
                                                           lower_bounds[node_index_in_conceptual_layer],
                                                           upper_bounds[node_index_in_conceptual_layer])

        # now create the equations for all the nodes
        # we don't need to create an equation for the input nodes since they don't have incoming connections
        # since all nodes still reside in the unprocessed table we create the equations and constraints
        # by looking only for nodes in the unprocessed table
        is_arnode = False
        table_number = Layer.INDEX_OF_UNPROCESSED_TABLE
        for i in range(Network.LOCATION_OF_FIRST_LAYER + 1, len(self.layers)):
            self.layers[i].calculate_equation_and_constraint_for_all_nodes_in_table(is_arnode, table_number)

        return first_layer_nodes_map, last_layer_nodes_map

    def hard_code_acas_output_properties(self, last_layer_nodes_map, which_acas_output):
        """
        :param last_layer_nodes_map:
        map between index of the node in the conceptual layer (as given by the nnet_reader_object)
        to the key of the node in the unprocessed_table in the layer object

        :param which_acas_output:
        which of the 4 properties should be added to the network

        this function would also set the output bounds

        :return: a list of te output nodes global incoming ids
        """
        last_layer = self.layers[-1]
        is_arnode = False
        if last_layer.get_number_of_nodes_in_table(is_arnode, Layer.INDEX_OF_UNPROCESSED_TABLE) != 5:
            raise Exception("acas should have exactly 5 outputs")

        if which_acas_output not in range(1, 5):
            raise ValueError("there are only 4 possible acas outputs")

        # y0 node would be y_nodes[0], y1 node would be y_nodes[1] and so on
        y_nodes = [last_layer.get_unprocessed_node_by_key(last_layer_nodes_map[i]) for i in range(5)]

        if which_acas_output == 1:
            # we want to make sure that y0 < 3.9911256459
            # so we want to unsat y0 >= 3.9911256459
            y_nodes[0].set_lower_and_upper_bound(3.9911256459, float('inf'))

            # bounds should be set on all output nodes
            # acas has 5 different output nodes
            # in this case we don't care what happens to all the output nodes other then y0
            for k in range(1, 5):
                y_nodes[k].set_lower_and_upper_bound(float('-inf'), float('inf'))

            self.output_bounds_were_set = True

            return [y_nodes[i].get_global_incoming_id() for i in range(5)]

        """
        if which_acas_output == 2:
            # we want to unsat
            # + y0 - y1 >= 0
            # + y0 - y2 >= 0
            # + y0 - y3 >= 0
            # + y0 - y4 >= 0
            
        elif which_acas_output == 3 or which_acas_output == 4:
            # we want to unsat
            # + y0 - y1 <= 0
            # + y0 - y2 <= 0
            # + y0 - y3 <= 0
            # + y0 - y4 <= 0

            # which is equivalent to unsat
            # - y0 + y1 >= 0
            # - y0 + y2 >= 0
            # - y0 + y3 >= 0
            # - y0 + y4 >= 0
        """

        # we want to create a new layer and input to it the differences between the nodes
        # first create the new output nodes
        new_last_layer = self.layers[-1].create_next_layer()
        self.layers.append(new_last_layer)
        new_output_nodes = []
        bias_for_nodes = 0
        for i in range(4):
            new_node_key = new_last_layer.create_new_node(bias_for_nodes)
            new_node = new_last_layer.get_unprocessed_node_by_key(new_node_key)
            new_output_nodes.append(new_node)

        # now connect the new output nodes to the y_nodes

        # first prepare the various connection data you'll need
        # what we are creating here is a connection data list as the NodeEdges class requires
        # in acas_output 2 the connection to y0 would be of weight 1 and the connection to
        # the rest would be of weight -1
        # in acas_outputs 3,4 it would be the reverse
        if which_acas_output == 2:
            weight_of_connection_to_y0 = 1
        else:
            weight_of_connection_to_y0 = -1
        connections_to_ys = [[*y_nodes[i].get_location(), -weight_of_connection_to_y0, y_nodes[i]]
                             for i in range(len(y_nodes))]
        # change the connection to y0 to be +1 instead of -1
        connections_to_ys[0][NodeEdges.INDEX_OF_WEIGHT_IN_DATA] *= -1

        # now connect each new output node to the previous y's
        for i in range(len(new_output_nodes)):
            new_output_nodes[i].add_or_edit_neighbors_by_bulk(GlobalNode.INCOMING_EDGE_DIRECTION,
                                                              [connections_to_ys[0], connections_to_ys[i + 1]])

        # now set the bounds on the nodes
        for i in range(len(new_output_nodes)):
            new_output_nodes[i].set_lower_and_upper_bound(0, float('inf'))

        self.output_bounds_were_set = True

        def get_node_global_incoming_id(node):
            return node.get_global_incoming_id()

        return list(map(get_node_global_incoming_id, new_output_nodes))

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
        if raise_error_if_overflow and up_to < -1:
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
        if raise_error_if_overflow and up_to < self.last_layer_not_preprocessed:
            raise Exception("requested to forward activate more layers than there were preprocessed")

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
            # to be fully activated a layer needs to have the layer before it forward activated
            # hence the + 1
            if up_to < self.last_layer_not_forward_activated + 1:
                raise Exception("requested to fully activate more layers than there were forward activated")
            elif up_to == -1:
                # i.e. te user wants to fully activate the input which is forbidden according to assumption (3)
                raise Exception("requested to fully activate more layers than there are available")

        # to preserve assumption (3) the input layer could never be fully activated.
        # in a bit of serendipity (and part rigorousness), the fact that we allow layers to be fully activated only if
        # their immediate previous layer has been forward activate, means that the input layer could never be
        # fully activated, because the "previous layer to it" (which does not exist), have not been forward activated,
        # this comes into effect in the '+ 1' in the loop
        # so this +1 takes care of both the demand that the first layer must never be fully activated and that
        # a layer can be fully activated only if their immediate previous layer has been forward activate
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

    def preprocess_the_entire_network(self):
        """
        this function preprocess all of the layers in the network
        """
        self.preprocess_more_layers(len(self.layers), raise_error_if_overflow=False)

    def forward_activate_the_entire_network(self):
        """
        this function preprocess, and forward activates all of the layers in the network
        """
        self.preprocess_the_entire_network()
        self.forward_activate_more_layers(len(self.layers), raise_error_if_overflow=False)

    def fully_activate_the_entire_network(self):
        """
        this function preprocess, and fully activates all of the layers in the network
        """
        self.forward_activate_the_entire_network()
        self.fully_activate_more_layers(len(self.layers), raise_error_if_overflow=False)

    """
    we would merge nodes with the same type of positivity/incrementality in a way that would
    enlarge/dwindle the network output according to the needed goal.
    each such merged group of nodes is called an arnode.
    we need to calculate the incoming and outgoing edges that are directed towards the arnodes which
    might contain a multiplicity of inner nodes.
    this calculation is dependent on the positivity/incrementality of the arnode, which is turn
    is dependent on the table its in in its layer.

    the 2 functions below are used to give us the basic functions to calculate the weight
    of the arnode edges based on their type and the network goal
    """

    #  for now the function is not commutative
    #  the problem how I see it is that there are at least 2^n ways to decide the weight of the merged edge
    #  for example
    #  sum of max of max of sum ...
    #  or
    #  max of max of sum of max...
    #  and so on
    def get_function_to_calc_weight_for_incoming_edges_for_arnode(self,
                                                                  table_number_of_arnode):
        """
        this method returns the function that is given to the arnode to calculate
        its incoming edges from the edges of its inner nodes.
        this function can be fed into all the arnodes methods that require a
        "function_to_calculate_merger_of_incoming_edges"

        :param table_number_of_arnode: one of
        Layer.INDEX_OF_POS_INC_TABLE
        Layer.INDEX_OF_POS_DEC_TABLE
        Layer.INDEX_OF_NEG_INC_TABLE
        Layer.INDEX_OF_NEG_DEC_TABLE

        :return:
        this method returns a function
        that function receives 2 inputs
        1) a reference to an arnode
        2) a list of weights we are connected to the arnode with
        and returns a new weight that we will connect to the given arnode with

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

        if arnode_is_inc_type:
            return lambda node, lis: max(lis)
        return lambda node, lis: min(lis)

    def get_function_to_calc_weight_for_outgoing_edges_for_arnode(self,
                                                                  table_number_of_arnode):
        """
        this method returns a function that is given to the arnode to calculate
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

    def get_function_to_calc_bias_for_arnode(self,
                                             table_number_of_arnode):
        """
        :param table_number_of_arnode: one of
        Layer.INDEX_OF_POS_INC_TABLE
        Layer.INDEX_OF_POS_DEC_TABLE
        Layer.INDEX_OF_NEG_INC_TABLE
        Layer.INDEX_OF_NEG_DEC_TABLE

        :return:
        this method returns the function that is given to the arnode to calculate
        its bias from the bias of its inner nodes

        for now this function is trivial and possibly incorrect,
        Yithzak paper assumes that there are no biases so I don't know what to do with those
        """

        def function_to_calc_bias_for_arnode(list_of_inner_nodes):
            return sum(list_of_inner_nodes)

        return function_to_calc_bias_for_arnode

    def decide_best_arnodes_to_merge(self):
        """
        this is my efficient implementation of algorithm 2 "create initial abstraction"
        the problem with the original pseudo code is that its working backwards.
        for each pair of arnodes it finds an arnode which is connected to both of them and continues from there.
        this approach is fine if the network is fully connected, but my implementation does not assume that.
        so it would be costly to work like "for each pair of arnodes find the intersection of the arnodes
        they are connected to using incoming connections".
        so instead I go the other way around.
        to check what arnodes should be merged in layer k, I look at layer k-1, and for each node in layer k-1,
        I check each pair of arnodes its connected to by an outgoing connection.

        :return:
        the attributes needed to know which arnodes to merge
        a layer number
        a table number
        a list_of_keys_of_arnodes_to_merge inside this table - for now, since we only implement algo 2, this would be
        a pair

        if no arnode set is found that is legible for merging, this function would raise an error
        """
        # first lets check that we fully activated enough layers so that we can start the merging process.
        # the output arnode wont be merged to preserve assumption (4) so we check to see if we at least fully activated
        # a layer before the output layer
        if self.last_layer_not_fully_activated >= len(self.layers) - 2:
            raise Exception("can not decide which arnodes to merge since not enough layers are "
                            "fully activated")

        # to preserve assumption (4) we should't check if (or even try to) merge arnodes in the output or input layers.
        # in this implementation, to check what arnodes should be merged in layer k, I look at the nodes in layer k-1.
        # so I need to loop over the layers which I call "k-1". i.e. I need to loop over the layers that preceed the
        # layers that I want to merge.
        # so when you do the math, I must go through a loop from len(self.layers) - 3 (the second layer from the last)
        # up to (and including) self.last_layer_not_fully_activated.
        # since the loop is exclusive up to, I loop up to self.last_layer_not_fully_activated - 1.

        # from assumption (3) we know that self.last_layer_not_fully_activated must be at least 0, so the loop is
        # sound, i.e. I will never go below 0.
        # this also means that that we wont ever try to merge or split the input layer
        # (since if we wanted to act upon layer 0 we need to use layer "-1" which does not exist)
        # so assumption (4) is again preserved

        best_pair = None
        best_pair_m = float("inf")
        # each pair "m" would indicate maximum difference between weights.
        # the best pair have the lowest m
        layer_of_best_pair = -1

        for i in range(len(self.layers) - 3, self.last_layer_not_fully_activated - 1, -1):
            assert i > -1  # just in case, but it should never happen
            current_layer_number = i + 1
            previous_layer = self.layers[i]
            # I would save a map that would tell me for each pair of nodes in the current_layer the value of m
            # a pair would be accessible using (table_num1, key_in_table1, table_num2, key_in_table2)
            map_of_pairs_to_m = {}

            for table_number in Layer.OVERALL_ARNODE_TABLES:
                # go through all arnodes in this table
                is_arnode = True
                for arnode in previous_layer.get_iterator_for_all_nodes_for_table(is_arnode, table_number):
                    # for each arnode find all the pairs of arnodes its connected to by an outgoing connection
                    for connection_data_pair in arnode.get_combinations_iterator_over_connections(
                            GlobalNode.OUTGOING_EDGE_DIRECTION, 2):

                        connection_data_1, connection_data_2 = connection_data_pair
                        weight_of_connection_1 = connection_data_1[NodeEdges.INDEX_OF_WEIGHT_IN_DATA]
                        weight_of_connection_2 = connection_data_2[NodeEdges.INDEX_OF_WEIGHT_IN_DATA]

                        # note that at this point we assume that arnodes in one type of table (for example pos-inc)
                        # connects only to arnodes that reside in the same type of table (in other layers)
                        # I'm sure it should follow from the layer assumptions.
                        # if you disagree you could assert that the table number as returned
                        # in the connection data, is never changing and always equal to table_number
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

                        if key_of_pair_in_map_of_pairs not in map_of_pairs_to_m \
                                or m > map_of_pairs_to_m[key_of_pair_in_map_of_pairs]:
                            # save for each pair of arnodes in the current layer its biggest m
                            map_of_pairs_to_m[key_of_pair_in_map_of_pairs] = m

            # now we want to find the best pair in the current layer
            # the best pair would have the minimum m
            # search map_of_pairs_to_m for the best pair
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

        if best_pair is None:
            raise Exception("no arnode set found that is legible for merging")

        # now you have the best pair to merge in the network so return the pair attributes
        # best_pair data is of the form (table_num1, key_in_table1, table_num2, key_in_table2)
        # and they should have the same table number
        table_number = best_pair[0]
        pairs_indices_in_table = [best_pair[1], best_pair[3]]

        return layer_of_best_pair, table_number, pairs_indices_in_table

    def decide_best_arnodes_to_split(self):
        """
        this is my implementation of algorithm 3 "weight based refinement"

        :return:
        the attributes needed to know which arnodes to split
        a layer number
        a table number
        the key inside this table
        a list of lists which would be a valid partition of the
        arnode inner nodes - since we only implement algorithm 3, this list would actually tell us to split
        by taking only 1 inner node out of the arnode

        if no arnode is found that is legible for splitting, this function would raise an error
        """
        # the outer layer arnodes wont be split to preserve assumption (4) so for the same reason specified in the
        # decide_best_arnodes_to_merge method,
        # we check to see if we fully activated a layer before the output layer
        if self.last_layer_not_fully_activated >= len(self.layers) - 2:
            raise Exception("can not decide which arnodes to merge since not enough layers are "
                            "fully activated")

        best_arnode_to_split = None
        best_arnode_to_split_m = 0
        index_in_inner_nodes_to_take_out_of_arnode = -1
        layer_number_of_best_arnode = -1

        # to preserve assumption (4) we should't check if (or even try to) split arnodes in the output or input layers.
        # so we start from len(self.layers) - 2
        # from assumption (3) we know that self.last_layer_not_fully_activated must be at least 0, so the loop is
        # sound, I will never go below 1. this also means that that we wont ever try to split the input layer
        # so assumption (4) is again preserved
        for layer_num in range(len(self.layers) - 2, self.last_layer_not_fully_activated, -1):
            for table_number in Layer.OVERALL_ARNODE_TABLES:
                is_arnode = True
                for current_arnode in self.layers[layer_num].get_iterator_for_all_nodes_for_table(is_arnode,
                                                                                                  table_number):
                    inner_nodes = current_arnode.get_inner_nodes()
                    if len(inner_nodes) == 1:
                        # this arnode is not comprised of multiple nodes, hence we cant split it so we skip it
                        continue

                    for j in range(len(inner_nodes)):
                        node = inner_nodes[j]
                        # go through all of the inner node incoming neighbors
                        # for each neighbor measure the difference of weights in connections between
                        # the weight of connection of this node to its neighbor,
                        # and
                        # the weight of connection of the current arnode to the arnode that contains that neighbor.
                        for incoming_connection_data in node.get_iterator_for_connections_data():
                            incoming_node = incoming_connection_data[
                                NodeEdges.INDEX_OF_REFERENCE_TO_NODE_CONNECTED_TO_IN_DATA]
                            weight_of_connection_between_the_nodes = incoming_connection_data[
                                NodeEdges.INDEX_OF_WEIGHT_IN_DATA]

                            arnode_incoming_is_nested_in = incoming_node.get_pointer_to_ar_node_nested_in()
                            weight_of_connection_between_the_arnodes = \
                                arnode_incoming_is_nested_in.get_weight_of_connection_to_neighbor(
                                    GlobalNode.OUTGOING_EDGE_DIRECTION, current_arnode.get_location())

                            diff = abs(
                                weight_of_connection_between_the_arnodes - weight_of_connection_between_the_nodes)

                            if diff > best_arnode_to_split_m:
                                best_arnode_to_split_m = diff
                                best_arnode_to_split = current_arnode
                                index_in_inner_nodes_to_take_out_of_arnode = j
                                layer_number_of_best_arnode = layer_num

        if best_arnode_to_split is None:
            raise Exception("no arnode found that is legible for splitting")
        # now you have the best arnode to split, but you need to create a valid partition for this arnode
        partition = [[]]
        best_arnode_to_split_inner_nodes = best_arnode_to_split.get_inner_nodes()
        for i in range(len(best_arnode_to_split_inner_nodes)):
            if i != index_in_inner_nodes_to_take_out_of_arnode:
                partition[0].append(best_arnode_to_split_inner_nodes[i])

        partition.append([best_arnode_to_split_inner_nodes[index_in_inner_nodes_to_take_out_of_arnode]])

        table, key = best_arnode_to_split.get_location()

        return layer_number_of_best_arnode, table, key, partition

    def merge_list_of_arnodes(self, layer_number, table_number, list_of_keys_of_arnodes_to_merge):
        function_to_calculate_merger_of_incoming_edges = self.get_function_to_calc_weight_for_incoming_edges_for_arnode(
            table_number)
        function_to_calculate_merger_of_outgoing_edges = self.get_function_to_calc_weight_for_outgoing_edges_for_arnode(
            table_number)
        function_to_calculate_arnode_bias = self.get_function_to_calc_bias_for_arnode(table_number)

        self.layers[layer_number].merge_list_of_arnodes(table_number, list_of_keys_of_arnodes_to_merge,
                                                        function_to_calculate_merger_of_incoming_edges,
                                                        function_to_calculate_merger_of_outgoing_edges,
                                                        function_to_calculate_arnode_bias)

    def split_arnode(self, layer_number, table_number, key_in_table, partition_of_arnode_inner_nodes):
        function_to_calculate_merger_of_incoming_edges = self.get_function_to_calc_weight_for_incoming_edges_for_arnode(
            table_number)
        function_to_calculate_merger_of_outgoing_edges = self.get_function_to_calc_weight_for_outgoing_edges_for_arnode(
            table_number)
        function_to_calculate_arnode_bias = self.get_function_to_calc_bias_for_arnode(table_number)

        self.layers[layer_number].split_arnode(table_number, key_in_table, partition_of_arnode_inner_nodes,
                                               function_to_calculate_merger_of_incoming_edges,
                                               function_to_calculate_merger_of_outgoing_edges,
                                               function_to_calculate_arnode_bias)

    def _create_valid_equations_for_all_nodes_without_valid_equations(self):
        """
        creates valid equations for all nodes which do not have valid equations
        """
        if not self.global_network_manager.check_if_can_run_current_network():
            # we need to initialize a valid equation for all the nodes/arnodes without one
            for data in self.global_network_manager.get_list_of_nodes_that_dont_have_valid_equations():
                layer_number, table_number, key_in_table, node_code = data
                layer = self.layers[layer_number]
                is_arnode = (node_code == self.global_network_manager.CODE_FOR_ARNODE)
                layer.calculate_equation_and_constraint_for_a_specific_node(is_arnode, table_number, key_in_table)

    def check_if_network_is_sat_or_unsat(self):
        """
        this function check whether the network is sat, unsat, or has a spurious counter example
        :return: one of
        CODE_FOR_SAT
        CODE_FOR_UNSAT
        CODE_FOR_SPURIOUS_COUNTEREXAMPLE
        """
        self._create_valid_equations_for_all_nodes_without_valid_equations()

        result = self.global_network_manager.verify()
        if result == GlobalNetworkManager.UNSAT:
            return Network.CODE_FOR_UNSAT

        result_is_valid = self.global_network_manager. \
            evaluate_if_result_of_last_verification_attempt_is_a_valid_counterexample()

        if result_is_valid == GlobalNetworkManager.SAT:
            return Network.CODE_FOR_SAT

        return Network.CODE_FOR_SPURIOUS_COUNTEREXAMPLE

    def run_current_network(self, map_of_input_nodes_global_ids_to_values):
        """
        :param map_of_input_nodes_global_ids_to_values:
        a map of the form (input_node_global_id -> value to give it)
        :return:
        runs the current network on the given map_of_input_nodes_global_ids
        and returns if the network was SAT or UNSAT on those inputs
        """
        code_for_network_to_run_eval_on = GlobalNetworkManager.CODE_FOR_CURRENT_NETWORK
        self.global_network_manager.run_network_on_input(code_for_network_to_run_eval_on,
                                                         map_of_input_nodes_global_ids_to_values)
