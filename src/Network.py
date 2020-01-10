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
        # for now the goal of the network would always be to increase its output
        # TODO check if its ok, maybe it needs to be the opposite
        self.goal_index = Network.INDEX_OF_NEED_TO_INCREASE_OUTPUT

        self.number_of_layers_in_network = len(AcasNnet_object.layerSizes)

        self.global_data_manager = GlobalDataManager(Network.MULTIPLICITY_OF_IDS * self.number_of_nodes_in_network)

        self.layers = [None for _ in range(self.number_of_layers_in_network)]
        self._initialize_layers()

        # all layers in the network are not preprocessed
        self.last_layer_not_preprocessed = len(self.layers) - 1

        # now create all the nodes in the network
        self.number_of_nodes_in_network = 0
        self._initialize_nodes_in_all_layers(AcasNnet_object)

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

    def preprocess_more_layers(self, number_of_layers_to_preprocess):
        """
        :param number_of_layers_to_preprocess:
        preprocess 'number_of_layers_to_preprocess' network layers which were not already preprocessed
        the preprocess procedure is carried from end to start
        """
        for i in range(self.last_layer_not_preprocessed,
                       max(-1, self.last_layer_not_preprocessed - number_of_layers_to_preprocess), -1):
            self.layers[i].preprocess_entire_layer()
            self.last_layer_not_preprocessed -= 1

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
