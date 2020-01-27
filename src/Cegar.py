"""
this class would be use to implement the various cegar algorithms
and to interface with general marabou
"""
from src.Network import Network


def run_cegar_naive(nnet_reader_object, which_acas_output):
    """
    naive algorithm
    abstracts all the way and only then starts to refine back
    """
    network = Network(nnet_reader_object, which_acas_output)
    network.fully_activate_the_entire_network()

    # merge all arnodes
    while True:
        try:
            layer_number, table_number, list_of_keys_of_arnodes_to_merge = network.decide_best_arnodes_to_merge()
            network.merge_list_of_arnodes(layer_number, table_number, list_of_keys_of_arnodes_to_merge)
        except:
            break

    while True:
        result = network.check_if_network_is_sat_or_unsat()
        if result == network.CODE_FOR_SAT:
            print('SAT')
            break
        elif result == network.CODE_FOR_UNSAT:
            print('UNSAT')
            break

        # we have a spurious counter example
        layer_number, table_number, key_in_table, partition_of_arnode_inner_nodes = network.decide_best_arnodes_to_merge()
        network.split_arnode(layer_number, table_number, key_in_table, partition_of_arnode_inner_nodes)