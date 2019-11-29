from src.Layer import *
import random
from itertools import permutations


def get_random_weight():
    return random.randint(-100, 100)

def get_random_permutations_of_range(up_to_exclusive):
    all_permutations = permutations([i for i in range(up_to_exclusive)])
    all_permutations = list(all_permutations)
    return all_permutations[random.randint(0, len(all_permutations) - 1)]


def get_randomly_connected_layers():
    layers = [Layer(), Layer(), Layer()]

    for i in range(len(layers) - 1):
        layers[i].set_next_layer(layers[i + 1])
        layers[i + 1].set_previous_layer(layers[i])

    # now add nodes to each layer
    unprocessed_nodes_keys_for_each_layer = []
    for layer in layers:
        amount_of_nodes_to_create = random.randint(1, 10)
        unprocessed_nodes_keys_for_current_layer = []

        for i in range(amount_of_nodes_to_create):
            new_node_key = layer.create_new_node()
            unprocessed_nodes_keys_for_current_layer.append(new_node_key)

        unprocessed_nodes_keys_for_each_layer.append(unprocessed_nodes_keys_for_current_layer)

    # now connect the nodes using random weights
    for i in range(len(layers) - 1):
        current_layer = layers[i]
        next_layer = layers[i + 1]
        for node_key_in_current_layer in unprocessed_nodes_keys_for_each_layer[i]:
            for node_key_in_next_layer in unprocessed_nodes_keys_for_each_layer[i + 1]:
                random_weight = get_random_weight()

                current_layer.add_or_edit_neighbor_to_node_in_unprocessed_table(node_key_in_current_layer,
                                                                                Layer.OUTGOING_LAYER_DIRECTION,
                                                                                node_key_in_next_layer,
                                                                                random_weight)

    return layers


def print_layers(layers):
    for layer in layers:
        print(layer)


layers = get_randomly_connected_layers()

# if you want to print the layers and see them use this
# print_layers(layers)

# now create all the arnodes
for i in range((len(layers) - 1), -1, -1):
    layers[i].preprocess_entire_layer()

# now all the arnodes are existent but are not even forward activate and as such have no edges
# forward activate them before continuing

for i in range((len(layers) - 1), -1, -1):
    # randomly activate the tables to check that their activation order doesnt matter
    for table_number in get_random_permutations_of_range(4):
        # for now use sum as the edges merger function
        layers[i].forward_activate_arnode_table(table_number, lambda node, lis: sum(lis))


print_layers(layers)
