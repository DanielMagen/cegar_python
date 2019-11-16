from src.Nodes.Node import Node
from src.NodeEdges import NodeEdges
import random

"""
checks only the complex parts of the node
"""

number_of_tables_in_previous_layer = random.randint(1, 10)
number_of_tables_in_current_layer = random.randint(1, 10)
number_of_tables_in_next_layer = random.randint(1, 10)
table_number = random.randint(0, number_of_tables_in_current_layer - 1)
key_in_table = random.randint(0, 10)

node = Node(number_of_tables_in_previous_layer,
            number_of_tables_in_next_layer,
            table_number, key_in_table)


def t_get_number_of_tables_in_layers(node_object):
    assert node_object.get_number_of_tables_in_previous_layer() == number_of_tables_in_previous_layer
    assert node_object.get_number_of_tables_in_next_layer() == number_of_tables_in_next_layer


def create_new_node_in_direction(direction):
    if direction == Node.INCOMING_EDGE_DIRECTION:
        new_node_number_of_tables_in_previous_layer = random.randint(1, 10)
        new_node_number_of_tables_in_current_layer = number_of_tables_in_previous_layer
        new_node_number_of_tables_in_next_layer = number_of_tables_in_current_layer

    elif direction == Node.OUTGOING_EDGE_DIRECTION:
        new_node_number_of_tables_in_previous_layer = number_of_tables_in_current_layer
        new_node_number_of_tables_in_current_layer = number_of_tables_in_next_layer
        new_node_number_of_tables_in_next_layer = random.randint(1, 10)
    else:
        raise Exception("illegal direction")

    new_node_table_number = random.randint(0, new_node_number_of_tables_in_current_layer - 1)
    new_node_key_in_table = random.randint(0, 10)

    new_node = Node(new_node_number_of_tables_in_previous_layer,
                    new_node_number_of_tables_in_next_layer,
                    new_node_table_number, new_node_key_in_table)

    return new_node


def t_adding_connection(node_object):
    possible_direction_of_connection = [Node.INCOMING_EDGE_DIRECTION, Node.OUTGOING_EDGE_DIRECTION]

    for direction_of_connection in possible_direction_of_connection:
        for should_add_given_node_to_new_node_neighbors in [True, False]:
            new_node = create_new_node_in_direction(direction_of_connection)
            new_node_table_number, new_node_key_in_table = new_node.get_location()

            weight = random.randint(-20, 20)
            connection_data = [new_node_table_number, new_node_key_in_table, weight, new_node]
            node_object.add_or_edit_neighbor(direction_of_connection, connection_data,
                                             add_this_node_to_given_node_neighbors=should_add_given_node_to_new_node_neighbors)

            assert node_object.check_if_neighbor_exists(direction_of_connection, new_node.get_location()) == True
            assert new_node.check_if_neighbor_exists(-direction_of_connection,
                                                     node_object.get_location()) == should_add_given_node_to_new_node_neighbors


def t_remove_connection(node_object):
    possible_direction_of_connection = [Node.INCOMING_EDGE_DIRECTION, Node.OUTGOING_EDGE_DIRECTION]
    for direction_of_connection in possible_direction_of_connection:
        for should_add_given_node_to_new_node_neighbors in [True, False]:
            new_node = create_new_node_in_direction(direction_of_connection)
            new_node_table_number, new_node_key_in_table = new_node.get_location()

            weight = random.randint(-20, 20)
            connection_data = [new_node_table_number, new_node_key_in_table, weight, new_node]
            node_object.add_or_edit_neighbor(direction_of_connection, connection_data,
                                             add_this_node_to_given_node_neighbors=should_add_given_node_to_new_node_neighbors)

            node_object.remove_neighbor_from_neighbors_list(direction_of_connection, new_node.get_location(),
                                                            remove_this_node_from_given_node_neighbors_list=False)

            assert node_object.check_if_neighbor_exists(direction_of_connection, new_node.get_location()) == False

            if should_add_given_node_to_new_node_neighbors:
                # preform another test where you verify that one sided deletion and double sided deletion work
                assert new_node.check_if_neighbor_exists(-direction_of_connection,
                                                         node_object.get_location()) == True

                # now add another new node but this time preform double sided deletion

                new_node = create_new_node_in_direction(direction_of_connection)
                new_node_table_number, new_node_key_in_table = new_node.get_location()

                weight = random.randint(-20, 20)
                connection_data = [new_node_table_number, new_node_key_in_table, weight, new_node]
                node_object.add_or_edit_neighbor(direction_of_connection, connection_data,
                                                 add_this_node_to_given_node_neighbors=should_add_given_node_to_new_node_neighbors)

                node_object.remove_neighbor_from_neighbors_list(direction_of_connection, new_node.get_location(),
                                                                remove_this_node_from_given_node_neighbors_list=True)

                assert node_object.check_if_neighbor_exists(direction_of_connection, new_node.get_location()) == False
                assert new_node.check_if_neighbor_exists(-direction_of_connection,
                                                         node_object.get_location()) == False


def t_get_iterator_for_edges_data(node_object):
    possible_direction_of_connection = [Node.INCOMING_EDGE_DIRECTION, Node.OUTGOING_EDGE_DIRECTION]
    for direction_of_connection in possible_direction_of_connection:
        iterator_for_edges_data = node_object.get_iterator_for_edges_data(direction_of_connection)
        for data in iterator_for_edges_data:
            # print(data)
            pass


def t_get_notified_when_neighbor_changes(node_object):
    possible_direction_of_connection = [Node.INCOMING_EDGE_DIRECTION, Node.OUTGOING_EDGE_DIRECTION]
    for direction_of_connection in possible_direction_of_connection:
        new_node = create_new_node_in_direction(direction_of_connection)
        new_node_table_number, new_node_key_in_table = new_node.get_location()

        weight = random.randint(-20, 20)
        connection_data = [new_node_table_number, new_node_key_in_table, weight, new_node]
        node_object.add_or_edit_neighbor(direction_of_connection, connection_data,
                                         add_this_node_to_given_node_neighbors=True)

        new_table_number = random.randint(0, number_of_tables_in_current_layer - 1)
        new_key_in_table = random.randint(0, 10)
        new_node.set_new_location(new_table_number, new_key_in_table)

        # first check that the 2 nodes know about each other
        assert node_object.check_if_neighbor_exists(direction_of_connection, new_node.get_location()) == True
        assert new_node.check_if_neighbor_exists(-direction_of_connection, node_object.get_location()) == True

        # now try and see if the node knows that the new node changed location
        data = node_object.get_connection_data_for_neighbor(direction_of_connection, new_node.get_location())
        assert data[NodeEdges.INDEX_OF_REFERENCE_TO_NODE_CONNECTED_TO_IN_DATA] == new_node


if __name__ == '__main':
    t_get_number_of_tables_in_layers(node)
    for _ in range(20):
        t_adding_connection(node)
    for _ in range(20):
        t_remove_connection(node)
    for _ in range(20):
        t_get_iterator_for_edges_data(node)
    for _ in range(20):
        t_get_notified_when_neighbor_changes(node)
