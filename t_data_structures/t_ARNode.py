from src.Nodes.Node import Node
from src.NodeEdges import NodeEdges
from src.Nodes.ARNode import ARNode
import random

"""
checks only the complex parts of the ARNode
"""

# work with big numbers to avoid duplicates
number_of_tables_in_previous_layer = random.randint(10, 20)
number_of_tables_in_current_layer = random.randint(10, 20)
number_of_tables_in_next_layer = random.randint(10, 20)


def get_new_node():
    table_number = random.randint(0, number_of_tables_in_current_layer - 1)
    key_in_table = random.randint(0, 50)

    return Node(number_of_tables_in_previous_layer,
                number_of_tables_in_next_layer,
                table_number, key_in_table)


def t_check_arnode_wont_start_if_node_isnt_set_in_stone():
    table_number = random.randint(0, number_of_tables_in_current_layer - 1)
    key_in_table = random.randint(0, 50)

    try:
        new_arnode = ARNode(get_new_node(),
                            table_number,
                            key_in_table)
        raise Exception("node was started with node that is not set in stone")
    except:
        pass


t_check_arnode_wont_start_if_node_isnt_set_in_stone()
