from maraboupy import MarabouNetworkNNet
from trying_to_rewrite.Edge import Edge
from trying_to_rewrite.ARNode import ARNode

"""
this file is a python implementation of the abstraction refinement algorithms


"""
# note that we use N(x) and y interchangeably
# we wish to verify either that that the network output is larger than or smaller than
# a number. ">" would mean that we want to verify y > c and
# "<" would mean that we want to verify y < c
# note that we try to find a counter example to the property we want to verify
# so if we want to verify that y > c we would search for an input which gives us y<=c
POSSIBLE_VERIFICATION_GOALS = ['>', '<']

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


def relu(x):
    return max(x, 0)


def get_abstraction_operation_for_incoming_edges_for_neuron_incrementality_type(current_goal_index,
                                                                                neuron_group_is_increment):
    """
    we would merge neurons with the same type of positivity/incrementality in a way that would
    enlarge/dwindle the network output according to the needed goal
    when merging said neurons we change their outgoing and incoming edges accordingly.

    this function returns what needs to be done the incoming edges that are directed towards the group we wish to merge.
    this can be determined only by the incrementality_type.

    :param current_goal_index: either INDEX_OF_NEED_TO_INCREASE_OUTPUT or INDEX_OF_NEED_TO_DECREASE_OUTPUT

    :param neuron_group_is_increment: if true, will indicate that the group of neurons are all of 'inc' type

    :return:
    this function returns the operation that needs to be done to the incoming edges of a group of neurons of
    the given incrementality type.
    for example if we want to increase the network output and we have a group of incremental neurons then we return
    'max'
    """

    if current_goal_index == INDEX_OF_NEED_TO_INCREASE_OUTPUT:
        if neuron_group_is_increment:
            return max
        return min

    elif current_goal_index == INDEX_OF_NEED_TO_DECREASE_OUTPUT:
        if neuron_group_is_increment:
            return min
        return max

    raise ValueError("invalid goal index")


def get_abstraction_operation_for_outgoing_edges_for_neuron_type(current_goal_index,
                                                                 neuron_group_is_increment,
                                                                 neuron_group_is_positive):
    """
    we would merge neurons with the same type of positivity/incrementality in a way that would
    enlarge/dwindle the network output according to the needed goal
    when merging said neurons we change their outgoing and incoming edges accordingly.

    this function returns what needs to be done the outgoing edges that are directed towards the group we wish to merge.

    :param current_goal_index: either INDEX_OF_NEED_TO_INCREASE_OUTPUT or INDEX_OF_NEED_TO_DECREASE_OUTPUT

    :param neuron_group_is_increment: if true, will indicate that the group of neurons are all of 'inc' type

    :param neuron_group_is_positive: if true, will indicate that the group of neurons are all of 'pos' type

    :return:
    this function returns the operation that needs to be done to the outgoing edges of a group of neurons of
    the given type.
    """

    # TODO check with yitzhak about it
    return sum


def get_node_id(index_of_layer_node_is_in, index_of_node_in_layer):
    return [index_of_layer_node_is_in, index_of_node_in_layer]


def get_net_object_from_neural_net_file(neural_net_full_path):
    """
    :param neural_net_full_path: the full path to the neural_net
    :return: a net object which is equivalent to given neural net formatted network
    """
    # read the given neural_net into Marabou Network
    generated_net = MarabouNetworkNNet.MarabouNetworkNNet(filename=neural_net_full_path)
    number_of_layers_in_network = len(generated_net.layerSizes)

    def get_net_edges():
        """
        :return: a 3d matrix called edges such that
        edges[i] is list of list of edges between layer i to layer i+1
        edges[i][j] is list of out edges from node j in layer i
        edges[i][j][k] is the k'th out edge of "node" j in "layer" i
        TODO : note that this list
         currently holds edge object and not just the weight between the edges. this is an testing oriented
         feature that maybe should be removed later on
        """
        edges = []

        # initialize the edges matrix
        # there are number_of_layers_in_network layers so there are number_of_layers_in_network - 1
        # lists of edges between layers
        for current_layer in range(number_of_layers_in_network - 1):
            # we will add all the edges from this layer to the next
            edges.append([])

            for current_node_in_layer in range(len(generated_net.weights[current_layer])):
                edges[current_layer].append([])

                for k in range(len(generated_net.weights[current_layer][current_node_in_layer])):
                    weight = generated_net.weights[current_layer][current_node_in_layer][k]
                    # TODO : I switched between src and dest, check with yitzhak that its correct
                    new_edge = Edge(get_node_id(current_layer, current_node_in_layer),
                                    get_node_id(current_layer + 1, k),
                                    weight)
                    edges[current_layer][current_node_in_layer].append(new_edge)

        # validate sizes
        assert (len(generated_net.weights) == len(edges))
        for i in range(len(generated_net.layerSizes) - 1):
            assert (len(generated_net.weights[i]) == len(edges[i]))
            for j in range(len(generated_net.weights[i])):
                assert (len(generated_net.weights[i][j]) == len(edges[i][j]))
                for k in range(len(generated_net.weights[i][j])):
                    if generated_net.weights[i][j][k] != edges[i][j][k].weight:
                        print(f"wrong edges: {i},{j},{k}")
                        assert False

        return edges

    def get_net_nodes(net_edges):
        """
        :param net_edges: a list of edges as given by the get_net_edges function

        :return: a list of list of ARNode instances such that
        nodes[i] is list of nodes in layer i
        nodes[i][j] is ARNode instance of node j in layer i
        """
        nodes = []

        # a table that would allow to get to the arnode by its index in the network
        table_of_arnodes = []
        for current_layer in range(number_of_layers_in_network):
            table_of_arnodes.append([None for _ in range(len(generated_net.weights[current_layer]))])


        for current_layer in range(number_of_layers_in_network):
            nodes.append([])
            for current_node_in_layer in range(len(generated_net.weights[current_layer])):
                node_name = get_node_id(current_layer, current_node_in_layer)
                # avoid using python copy function since its slow as hell
                node_out_edges = []
                node_out_edges.extend(net_edges[current_layer][current_node_in_layer])
                current_ar_node = ARNode(name=node_name,
                                      ar_type=None,
                                      in_edges=[],
                                      out_edges=node_out_edges,
                                      activation_func=relu,
                                      bias=0.0  # assigned later
                                      )
                nodes[current_layer].append(current_ar_node)
                table_of_arnodes[current_layer][current_node_in_layer] = current_ar_node


        # now update all ARNode incoming edges for each ARNode
        for current_layer in range(number_of_layers_in_network):
            for arnode in table_of_arnodes[current_layer]:






    # after all nodes instances exist, add input and output edges
    for i, layer in enumerate(edges):  # layer is list of list of edges
        for j, node in enumerate(layer):  # node is list of edges
            for k, edge in enumerate(node):  # edge is Edge instance
                # print (i,j,k)
                src_node = name2node_map[edge.src]
                dest_node = name2node_map[edge.dest]
                src_node.out_edges.append(edge)
                dest_node.in_edges.append(edge)

    # TODO create nodes using the edges
    layers = []
    for i, layer in enumerate(nodes):
        if i == 0:
            type_name = "input"
        elif i == len(generated_net.layerSizes) - 1:
            type_name = "output"
        else:
            type_name = "hidden"
        layers.append(Layer(type_name=type_name, nodes=nodes[i]))

    # TODO create layers using the nodes
    net = Net(layers=layers)

    for i, biases in enumerate(generated_net.biases):
        layer = net.layers[i + 1]
        for j, node in enumerate(layer.nodes):
            node.bias = biases[j]
    return net
