########################################## currently this file contains the function that were written in the first try. update them later

"""
stuff that needs to be modular
the nodes cataloging

the abstraction process:
    up to which layer are we preforming the abstraction
the abstraction process order nodes order


the refinement process:
    which neurons to split
    how many to split
    how to choose which to split

what kind of net we would hold - should we compile the net from zero
to full each time or should we create a simulated net

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

    return sum


def get_net_from_path():
    pass


def convert_network_to_only_have_1_output(network):
    pass


def run_abstraction_refinement(full_path_to_net,
                               function_to_do_the_abstraction,
                               function_to_do_the_refinement,
                               function_to_decide_what_to_do_if_process_fails):
    """


    :param full_path_to_net:

    :param function_to_do_the_abstraction: this function abstracts the network up to a certain layer and returns the
    abstracted_network and the minimum layer index it has abstracted (abstraction is done from end to start)

    :param function_to_do_the_refinement:
    this function receives the network and the minimum layer index it was abstracted to
    it then does the refinement on the network
    it can either return sat or unsat or it can decide to stop at which point we use the
    function_to_decide_what_to_do_if_process_fails function

    :param function_to_decide_what_to_do_if_process_fails: will only be called if the function_to_do_the_refinement
    fails. it would decide if we want to stop or maybe simply use normal verification

    :return:
    """
    # a globally available variable
    network = get_net_from_path(full_path_to_net)

    network = convert_network_to_only_have_1_output(network)

    abstracted_network, minimum_layer_we_abstracted_to = function_to_do_the_abstraction(network)

    results = function_to_do_the_refinement(network, abstracted_network, minimum_layer_we_abstracted_to)

    if results == 'sat':
        return 'sat'
    elif results == 'unsat':
        return 'unsat'
    else:
        # it failed
        return function_to_decide_what_to_do_if_process_fails(network, abstracted_network)

