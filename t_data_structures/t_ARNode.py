from src.Nodes.Node import Node
from src.NodeEdges import NodeEdges
from src.Nodes.ARNode import ARNode
import random
from itertools import permutations

"""
checks only the complex parts of the ARNode
"""

# work with big numbers to avoid duplicates
number_of_tables_in_previous_layer = random.randint(10, 20)
number_of_tables_in_current_layer = random.randint(10, 20)
number_of_tables_in_next_layer = random.randint(10, 20)


def get_random_weight():
    return random.randint(-20, 20)


def get_random_permutations_of_range(up_to_exclusive):
    all_permutations = permutations([i for i in range(up_to_exclusive)])
    all_permutations = list(all_permutations)
    return all_permutations[random.randint(0, len(all_permutations) - 1)]


def get_new_node_in_current_layer():
    table_number = random.randint(0, number_of_tables_in_current_layer - 1)
    key_in_table = random.randint(0, 50)

    return Node(number_of_tables_in_previous_layer,
                number_of_tables_in_next_layer,
                table_number, key_in_table)


def get_new_node_in_previous_layer():
    table_number = random.randint(0, number_of_tables_in_previous_layer - 1)
    key_in_table = random.randint(0, 50)

    return Node(random.randint(10, 20),
                number_of_tables_in_current_layer,
                table_number, key_in_table)


def get_new_node_in_next_layer():
    table_number = random.randint(0, number_of_tables_in_next_layer - 1)
    key_in_table = random.randint(0, 50)

    return Node(number_of_tables_in_current_layer,
                random.randint(10, 20),
                table_number, key_in_table)


def t_check_arnode_wont_start_if_node_isnt_set_in_stone():
    table_number = random.randint(0, number_of_tables_in_current_layer - 1)
    key_in_table = random.randint(0, 50)

    try:
        new_arnode = ARNode([get_new_node_in_current_layer()],
                            table_number,
                            key_in_table)
    except:
        return

    raise AssertionError("node was started with node that is not set in stone")


def t_arnode_forward_activation():
    node_in_previous_layer = get_new_node_in_previous_layer()

    # create another node to check that forward activation is affected only by outgoing connections
    # we will link this node to the node in the current layer but will not insert it into an arnode wrapper
    # this should not interfere with the forward activation of the arnode wrapper of the node in the current
    node_in_previous_layer2 = get_new_node_in_previous_layer()

    node_in_current_layer = get_new_node_in_current_layer()
    node_in_next_layer = get_new_node_in_next_layer()

    node_in_previous_layer.set_in_stone()
    node_in_current_layer.set_in_stone()
    node_in_next_layer.set_in_stone()

    # connect between the nodes
    node_in_previous_layer.add_or_edit_neighbor(Node.OUTGOING_EDGE_DIRECTION,
                                                [*node_in_current_layer.get_location(),
                                                 get_random_weight(),
                                                 node_in_current_layer])

    node_in_previous_layer2.add_or_edit_neighbor(Node.OUTGOING_EDGE_DIRECTION,
                                                 [*node_in_current_layer.get_location(),
                                                  get_random_weight(),
                                                  node_in_current_layer])

    node_in_current_layer.add_or_edit_neighbor(Node.OUTGOING_EDGE_DIRECTION,
                                               [*node_in_next_layer.get_location(),
                                                get_random_weight(),
                                                node_in_next_layer])

    # now create corresponding arnodes for the nodes
    arnode_in_previous_layer = ARNode([node_in_previous_layer],
                                      *node_in_previous_layer.get_location())

    arnode_in_current_layer = ARNode([node_in_current_layer],
                                     *node_in_current_layer.get_location())

    # before creating the arnode for the node_in_next_layer, check that you really can't forward activate
    # arnode_in_current_layer, because he has a outgoing connection to node_in_next_layer and node_in_next_layer hasn't
    # been given an arnode wrapper yet
    try:
        arnode_in_current_layer.forward_activate_arnode(lambda x, lis: sum(lis))
        raise Exception("did not raise error when trying to incorrectly forward activate an arnode")
    except AssertionError:
        pass

    arnode_in_next_layer = ARNode([node_in_next_layer],
                                  *node_in_next_layer.get_location())

    # test that forward activation can be done at any order as long as the right conditions are met
    all_arnodes_needed_to_activate = [arnode_in_previous_layer, arnode_in_current_layer, arnode_in_next_layer]
    for i in get_random_permutations_of_range(len(all_arnodes_needed_to_activate)):
        all_arnodes_needed_to_activate[i].forward_activate_arnode(lambda x, lis: sum(lis))

    assert arnode_in_previous_layer.get_activation_status() == ARNode.ONLY_FORWARD_ACTIVATED_STATUS
    assert arnode_in_current_layer.get_activation_status() == ARNode.ONLY_FORWARD_ACTIVATED_STATUS
    assert arnode_in_next_layer.get_activation_status() == ARNode.ONLY_FORWARD_ACTIVATED_STATUS


def t_arnode_full_activation():
    node_in_previous_layer = get_new_node_in_previous_layer()

    # create another node to check that forward activation is affected only by outgoing connections, but that
    # full activation is also affected by incoming connections
    node_in_previous_layer2 = get_new_node_in_previous_layer()

    node_in_current_layer = get_new_node_in_current_layer()
    node_in_next_layer = get_new_node_in_next_layer()

    node_in_previous_layer.set_in_stone()
    node_in_current_layer.set_in_stone()
    node_in_next_layer.set_in_stone()

    # connect between the nodes
    node_in_previous_layer.add_or_edit_neighbor(Node.OUTGOING_EDGE_DIRECTION,
                                                [*node_in_current_layer.get_location(),
                                                 get_random_weight(),
                                                 node_in_current_layer])

    node_in_previous_layer2.add_or_edit_neighbor(Node.OUTGOING_EDGE_DIRECTION,
                                                 [*node_in_current_layer.get_location(),
                                                  get_random_weight(),
                                                  node_in_current_layer])

    node_in_current_layer.add_or_edit_neighbor(Node.OUTGOING_EDGE_DIRECTION,
                                               [*node_in_next_layer.get_location(),
                                                get_random_weight(),
                                                node_in_next_layer])

    # now create corresponding arnodes for the nodes
    arnode_in_previous_layer = ARNode([node_in_previous_layer],
                                      *node_in_previous_layer.get_location())

    arnode_in_current_layer = ARNode([node_in_current_layer],
                                     *node_in_current_layer.get_location())

    arnode_in_next_layer = ARNode([node_in_next_layer],
                                  *node_in_next_layer.get_location())

    # test that forward activation can be done at any order as long as the right conditions are met
    all_arnodes_needed_to_activate = [arnode_in_previous_layer, arnode_in_current_layer, arnode_in_next_layer]
    for i in get_random_permutations_of_range(len(all_arnodes_needed_to_activate)):
        all_arnodes_needed_to_activate[i].forward_activate_arnode(lambda x, lis: sum(lis))

    assert arnode_in_previous_layer.get_activation_status() == ARNode.ONLY_FORWARD_ACTIVATED_STATUS
    assert arnode_in_current_layer.get_activation_status() == ARNode.ONLY_FORWARD_ACTIVATED_STATUS
    assert arnode_in_next_layer.get_activation_status() == ARNode.ONLY_FORWARD_ACTIVATED_STATUS

    # now begin fully activating
    arnode_in_next_layer.fully_activate_arnode_without_changing_incoming_edges()

    # since we still haven't even wrapped node_in_previous_layer2 in an arnode we shouldn't be able to fully activate
    # the node in the current layer. if it were not for this node, we should have been able to fully activate it since
    # we fully activated the arnode_in_next_layer
    try:
        arnode_in_current_layer.check_if_arnode_can_be_fully_activated_and_raise_exception_if_cant()
        raise Exception("did not raise error when trying to incorrectly fully activate an arnode")
    except AssertionError:
        pass

    # now we wrap the node_in_previous_layer2 in an arnode, but still we shouldn't be able to fully activate
    # the node in the current since the arnode won't be forward activated
    node_in_previous_layer2.set_in_stone()
    arnode_in_previous_layer2 = ARNode([node_in_previous_layer2],
                                       *node_in_previous_layer2.get_location())
    try:
        arnode_in_current_layer.check_if_arnode_can_be_fully_activated_and_raise_exception_if_cant()
        raise Exception("did not raise error when trying to incorrectly fully activate an arnode")
    except AssertionError:
        pass

    # passed all tests so far, activate arnode_in_previous_layer2
    arnode_in_previous_layer2.forward_activate_arnode(lambda x, lis: sum(lis))

    # now we shouldn't be able to fully activate arnode_in_previous_layer since arnode_in_current_layer was not
    # fully activated before
    try:
        arnode_in_previous_layer.check_if_arnode_can_be_fully_activated_and_raise_exception_if_cant()
        raise Exception("did not raise error when trying to incorrectly fully activate an arnode")
    except AssertionError:
        pass

    arnode_in_current_layer.fully_activate_arnode_without_changing_incoming_edges()
    arnode_in_previous_layer.fully_activate_arnode_without_changing_incoming_edges()
    arnode_in_previous_layer2.fully_activate_arnode_without_changing_incoming_edges()



t_arnode_full_activation()
