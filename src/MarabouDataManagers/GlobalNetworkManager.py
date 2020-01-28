from src.MarabouDataManagers.GlobalDataManager import GlobalDataManager
from maraboupy import MarabouCore

"""
manage some of the global data which is required for the marabou system

- solving and evaluating the network - would be used to save the original network input query
and use it to evaluate a proposed solution
"""


class GlobalNetworkManager(GlobalDataManager):
    CODE_FOR_ORIGINAL_NETWORK = 0
    CODE_FOR_CURRENT_NETWORK = 1

    def __init__(self, max_id_non_exclusive):
        super().__init__(max_id_non_exclusive)

        self.counter_example_of_last_verification_attempt = None

        self.input_query_of_original_network = None
        self.input_nodes_global_incoming_ids = []
        self.output_nodes_global_incoming_ids = []

        # this would save the result of the evaluation of the network on the
        # counter example, as given by the marabou_core solve function.
        self.result_of_counter_example_of_last_verification_attempt_applied_to_original_network = {}

    def get_input_nodes_global_incoming_ids(self):
        # copy is slow
        return [self.input_nodes_global_incoming_ids[i] for i in range(len(self.input_nodes_global_incoming_ids))]

    def get_output_nodes_global_incoming_ids(self):
        # copy is slow
        return [self.output_nodes_global_incoming_ids[i] for i in range(len(self.output_nodes_global_incoming_ids))]

    def get_counter_example_of_last_verification_attempt(self):
        return self.counter_example_of_last_verification_attempt

    def check_if_can_run_current_network(self):
        """
        :return: true if you can start verifying the network
        and false otherwise.
        for now, its false iff there are nodes in the network that don't have a valid equation
        (for example one for their neighbors was deleted)

        you can get an iterator over all the nodes which dont have a valid equation using the function
        get_list_of_nodes_that_dont_have_valid_equations
        """
        return len(self.set_of_nodes_locations_that_dont_have_valid_equations) == 0

    def save_current_network_as_original_network(self, input_nodes_global_incoming_ids,
                                                 output_nodes_global_incoming_ids):
        """
        this function copies the current self.input_query and saves it to
        self.input_query_of_original_network
        IMPORTANT:
        assumption (7)
        it assumes that the output bounds were already set on all of the output nodes

        input_query_of_original_network would be used to evaluate possible sat results later on.
        from assumption (5) we know that the input nodes wont change their global id throughout the program life,
        so we can use this old input query knowing that when a possible solution would tell us to, for example, set
        input node with global id 5 to be 1.2, then it would be the input node with global id 5 from the start

        also from assumption (6) we now that the output nodes global id would remain the same (this assumption also
        gives us the same guarantee for the input nodes so with assumption 5 we are double sure that input nodes
        ids wont change)

        :param input_nodes_global_incoming_ids:
        :param output_nodes_global_incoming_ids:

        """
        if not self.check_if_can_run_current_network():
            raise Exception("can not save a network which can not be run later")

        self.input_query_of_original_network = self.input_query.copy()
        self.input_nodes_global_incoming_ids = input_nodes_global_incoming_ids
        self.output_nodes_global_incoming_ids = output_nodes_global_incoming_ids

    def run_network_on_input(self, code_for_network_to_run_eval_on,
                             map_of_input_nodes_global_ids_to_values):
        """
        :param code_for_network_to_run_eval_on:
        if CODE_FOR_CURRENT_NETWORK it would run the evaluation on the current network
        else if its CODE_FOR_ORIGINAL_NETWORK it would run the evaluation on the network saved in the last call to
        save_network_query_as_original_network

        :param map_of_input_nodes_global_ids_to_values:
        a map of the form (input_node_global_id -> value to give it)

        :return:
        the map_of_node_to_value which we get from the MarabouCore.solve function
        note that if the given input is unsat then the map would be empty

        IMPORTANT: This function does not save any data to the global network manager
        it simply evaluates the network you want on the input you want and returns the output
        """
        if code_for_network_to_run_eval_on == GlobalNetworkManager.CODE_FOR_CURRENT_NETWORK:
            if not self.check_if_can_run_current_network():
                raise Exception("can not run the network there are nodes with invalid equations")
            input_query_to_eval = self.input_query.copy()
        elif code_for_network_to_run_eval_on == GlobalNetworkManager.CODE_FOR_ORIGINAL_NETWORK:
            input_query_to_eval = self.input_query_of_original_network.copy()
        else:
            raise ValueError("illegal code for network")

        for node_global_id in self.input_nodes_global_incoming_ids:
            value_given = map_of_input_nodes_global_ids_to_values[node_global_id]
            input_query_to_eval.setLowerBound(node_global_id, value_given)
            input_query_to_eval.setUpperBound(node_global_id, value_given)

        options = None  ########################### check what are those options
        filename_to_save_log_in = ""
        map_of_node_to_value, stats = MarabouCore.solve(
            input_query_to_eval.get_new_marabou_input_query_object(self.get_maximum_id_used(),
                                                                   self.input_nodes_global_incoming_ids,
                                                                   self.output_nodes_global_incoming_ids),
            options,
            filename_to_save_log_in)

        return map_of_node_to_value

    def verify(self):
        """
        gives a clone of the current input query to the solving engine
        :return:
        SAT or UN-SAT indicating whether or not the input query has a counter example
        if its SAT, the counter example would be saved in counter_example_of_last_verification_attempt

        the counter example could be retrieved by calling get_counter_example_input_query_of_last_solution_attempt
        the counter example could also be checked if its a correct counter example or not by calling
        evaluate_if_result_of_last_verification_attempt_is_a_valid_counterexample
        """
        if not self.check_if_can_run_current_network():
            raise Exception("can not verify since there are nodes with invalid equations")

        options = None  ########################### check what are those options
        filename_to_save_log_in = ""

        # if I understand correctly this is a map of "node_global_id -> value it got"
        self.counter_example_of_last_verification_attempt, stats = \
            MarabouCore.solve(self.input_query.get_new_marabou_input_query_object(self.get_maximum_id_used(),
                                                                                  self.input_nodes_global_incoming_ids,
                                                                                  self.output_nodes_global_incoming_ids),
                              options,
                              filename_to_save_log_in)

        if len(self.counter_example_of_last_verification_attempt) > 0:
            # there is a SAT solution
            return GlobalDataManager.SAT

        return GlobalDataManager.UNSAT

    def evaluate_if_result_of_last_verification_attempt_is_a_valid_counterexample(self):
        """
        :return:
        if the evaluation is SAT it returns SAT and saves the result in
        result_of_counter_example_of_last_verification_attempt_applied_to_original_network
        otherwise it returns UNSAT
        """

        # from assumption (6) we now that the inputs and output global ids would never change once given
        # so we now that the input and output that are saved inside self.counter_example_of_last_solution_attempt
        # are correct (each input is mapped to itself amd only itself, and each input is mapped to. the same for output)

        # the trick to implement this function
        # is to run the marabou solving function on the input nodes
        # where for each input node we have upper_bound_i=lower_bound_i=k
        # since the output bounds were set already, all we'll need to do is to see if its SAT.

        input_query_to_eval = self.input_query_of_original_network.copy()
        for node_global_id in self.input_nodes_global_incoming_ids:
            value_given = self.counter_example_of_last_verification_attempt[node_global_id]
            input_query_to_eval.setLowerBound(node_global_id, value_given)
            input_query_to_eval.setUpperBound(node_global_id, value_given)

        options = None  ########################### check what are those options
        filename_to_save_log_in = ""
        map_of_node_to_value, stats = MarabouCore.solve(
            input_query_to_eval.get_new_marabou_input_query_object(self.get_maximum_id_used(),
                                                                   self.input_nodes_global_incoming_ids,
                                                                   self.output_nodes_global_incoming_ids),
            options,
            filename_to_save_log_in)

        if len(self.counter_example_of_last_verification_attempt) > 0:
            # there is a SAT solution
            self.result_of_counter_example_of_last_verification_attempt_applied_to_original_network = map_of_node_to_value
            return GlobalDataManager.SAT
        else:
            return GlobalDataManager.UNSAT
