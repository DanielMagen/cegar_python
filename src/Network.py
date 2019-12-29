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
    MULTIPLICITY_OF_IDS = 20  # arbitrarly set it to 20

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

    def __init__(self, AcasNnet_object, goal_index):
        """
        :param AcasNnet_object:
        an AcasNnet object which has loaded into itself the network and the requested bounds on the network input nodes.
        this network class would convert that network into an inner representation of multiple layers, tables and
        node classes, which are built for the purpose of supporting the abstraction refinement

        :param goal_index: either INDEX_OF_NEED_TO_INCREASE_OUTPUT or INDEX_OF_NEED_TO_DECREASE_OUTPUT
        if INDEX_OF_NEED_TO_INCREASE_OUTPUT is given we assume that we want to increase the network output
        """
        if goal_index not in Network.POSSIBLE_GOALS:
            raise Exception("can not initialize network with illegal goal index")

        self.goal_index = goal_index

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
        pass

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
