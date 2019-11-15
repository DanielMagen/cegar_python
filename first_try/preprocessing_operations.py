class Node:
    pass

def weight(edge):
    return 0

############### how to keep track on who is positive and who is negative??????????????
def split_single_node_to_pos_neg(network, layer_node_is_in, node_number):
    ##################### not good. if the original node does not have any negative edges it will create a neg_node
    ##################### for nothing
    original_node = network[layer_node_is_in][node_number]

    pos_node = Node()
    neg_node = Node()

    network.add_node(pos_node)
    network.add_node(neg_node)

    for incoming_edge in original_node.get_incoming_edges():
        source_for_incoming_edge = incoming_edge.get_source()
        network.add_edge(source_for_incoming_edge, pos_node, weight(incoming_edge))
        network.add_edge(source_for_incoming_edge, neg_node, weight(incoming_edge))

    for outgoing_edge in original_node.get_outgoing_edges():
        sink_for_outgoing_edge = outgoing_edge.get_sink()

        if weight(outgoing_edge) > 0:
            network.add_edge(pos_node, sink_for_outgoing_edge, weight(outgoing_edge))

        elif weight(outgoing_edge) < 0:
            network.add_edge(neg_node, sink_for_outgoing_edge, weight(outgoing_edge))

    # removes the node, this also removes it from all of its neighbors
    network.remove_node_from_network(original_node)





def preprocess_network_up_to_minimal_layer(network, minimal_layer_to_stop_at):
    """

    :param network:
    :param minimal_layer_to_stop_at:
    :return:
    """
