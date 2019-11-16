from NodeEdges import *
import random


def check_initialization(node_edges_object):
    """
    call after the node_edges_object was initialized
    """
    assert ne.get_number_of_connections() == 0


def check_adding_connection(node_edges_object):
    number_of_tables = node_edges_object.get_number_of_tables_in_layer_connected_to()
    table_number = random.randint(0, number_of_tables - 1)
    key_in_table = random.randint(0, 10)
    weight = random.randint(-20, 20)
    node_connected_to = None

    node_edges_object.add_or_edit_connection(table_number, key_in_table, weight, node_connected_to)

    assert node_edges_object.check_if_connection_exist(table_number, key_in_table) == True
    assert node_edges_object.find_weight_of_connection(table_number, key_in_table) == weight

    return [table_number, key_in_table, weight, node_connected_to]


def check_deleting_connection(node_edges_object):
    table_number, key_in_table, weight, node_connected_to = check_adding_connection(node_edges_object)
    node_edges_object.delete_connection(table_number, key_in_table)
    assert node_edges_object.check_if_connection_exist(table_number, key_in_table) == False


def check_overriding_existing_connection(node_edges_object):
    table_number, key_in_table, weight, node_connected_to = check_adding_connection(node_edges_object)
    new_weight = weight * 2
    if new_weight == 0:
        new_weight = 1

    node_edges_object.add_or_edit_connection(table_number, key_in_table, new_weight, node_connected_to)

    assert node_edges_object.find_weight_of_connection(table_number, key_in_table) == new_weight


def print_all_edges_data(node_edges_object):
    for data in node_edges_object.get_iterator_over_connections():
        print(data)

    print(node_edges_object.get_a_list_of_all_connections())


if __name__ == '__main':
    number_of_tables_in_layer_connected_to = 5
    ne = NodeEdges(number_of_tables_in_layer_connected_to)

    check_initialization(ne)
    for _ in range(20):
        check_adding_connection(ne)
    for _ in range(20):
        check_deleting_connection(ne)
    for _ in range(20):
        check_overriding_existing_connection(ne)

    print_all_edges_data(ne)
