from src.Layer import *
import random


number_of_tables_in_previous_layer = random.randint(1, 10)
number_of_tables_in_current_layer = random.randint(1, 10)
number_of_tables_in_next_layer = random.randint(1, 10)

previous_layer = Layer(random.randint(1, 10), number_of_tables_in_current_layer)
current_layer = Layer(number_of_tables_in_previous_layer, number_of_tables_in_next_layer)
next_layer = Layer(number_of_tables_in_current_layer, random.randint(1, 10))

layers = [previous_layer, current_layer, next_layer]

# now add nodes to each layer
unprocessed_nodes_keys_for_each_layer = []
for layer in layers:
    amount_of_nodes_to_create = random.randint(1, 10)
    unprocessed_nodes_for_current_layer = []