from maraboupy import MarabouCore
from src.MarabouDataManagers.IDManager import IDManager

"""
manage all global data which is required for the marabou system
- global ids : can automatically reduce the number of used variables or set bounds on 
"artificial variables" which are not being used.

- input query

- equation

- solving and evaluating the network - would be used to save the original network input query
and use it to evaluate a proposed solution

"""


class GlobalDataManager(IDManager):
    UNSAT = False
    SAT = True

    """
    currently this class does not support reaching the end of its available id range.
    if we exhaust the ids, then the class behavior is no defined. it would make errors. 
    so do not exhaust the id ranges in it!
    """

    def __init__(self, max_id_non_exclusive):
        """
        this class would give available ids in increasing order
        :param max_id_non_exclusive: the maximum id that can be given
        """
        super().__init__(max_id_non_exclusive)

        self.input_query_reference = MarabouCore.InputQuery()

        self.input_query_of_original_network = None
        self.input_nodes_global_incoming_ids = []
        self.output_nodes_global_incoming_ids = []

        # those sets would hold triplets of the form (layer_number, table_number, key_in_table)
        # for nodes that dont have valid equations
        # if those sets are not empty, then the solving process can not take place
        self.set_of_nodes_locations_that_dont_have_valid_equations = set([])

        self.counter_example_of_last_solution_attempt = None
        self.result_of_last_evaluation = {}  # this would save the result of the evaluation of the network on the
        # counter example, as given by the marabou_core solve function.

    def addEquation(self, equation):
        self.input_query_reference.addEquation(equation)

    def removeEquation(self, equation):
        self.input_query_reference.removeEquation(equation)

    def add_location_of_node_that_dont_have_valid_equation(self, layer_number, table_number, key_in_table):
        self.set_of_nodes_locations_that_dont_have_valid_equations.add((layer_number, table_number, key_in_table))

    def check_if_node_has_invalid_equations(self, layer_number, table_number, key_in_table):
        return (layer_number, table_number, key_in_table) in self.set_of_nodes_locations_that_dont_have_valid_equations

    def remove_location_of_node_that_dont_have_valid_equation(self, layer_number, table_number, key_in_table):
        # discard ignores removal of items that are not in the set
        self.set_of_nodes_locations_that_dont_have_valid_equations.discard((layer_number, table_number, key_in_table))

    def setLowerBound(self, node_global_incoming_id, lower_bound):
        """
        given a node global incoming id, it places the given lower bound on it
        :param node_global_incoming_id:
        :param lower_bound: if its -infinity it does not set any bound
        :return:
        """
        if lower_bound != float('-inf'):
            self.input_query_reference.setLowerBound(node_global_incoming_id, lower_bound)

    def setUpperBound(self, node_global_incoming_id, upper_bound):
        """
        given a node global incoming id, it places the given upper bound on it
        :param node_global_incoming_id:
        :param upper_bound: if its infinity it does not set any bound
        :return:
        """
        if upper_bound != float('inf'):
            self.input_query_reference.setUpperBound(node_global_incoming_id, upper_bound)

    def getLowerBound(self, node_global_incoming_id):
        """
        given a node global incoming id, it returns the lower bound placed on it
        :param node_global_incoming_id:
        :return:
        """
        return self.input_query_reference.getLowerBound(node_global_incoming_id)

    def getUpperBound(self, node_global_incoming_id):
        """
        given a node global incoming id, it returns the upper bound placed on it
        :param node_global_incoming_id:
        :return:
        """
        return self.input_query_reference.getUpperBound(node_global_incoming_id)

    def removeBounds(self, node_global_incoming_id):
        """
        given a node global incoming id, it removes the upper and lower bounds set on it
        :param node_global_incoming_id:
        :return:
        """
        return self.input_query_reference.removeBounds(node_global_incoming_id)

    def addReluConstraint(self, id1, id2):
        MarabouCore.addReluConstraint(self.input_query_reference, id1, id2)

    def removeReluConstraint(self, id1, id2):
        MarabouCore.removeReluConstraint(self.input_query_reference, id1, id2)

    def get_new_equation(self):
        return MarabouCore.Equation()

    def save_current_input_query_as_original_network(self, input_nodes_global_incoming_ids,
                                                     output_nodes_global_incoming_ids):
        """
        this function copies the current self.input_query_reference and saves it to
        self.input_query_of_original_network
        IMPORTANT:
        assumption (7)
        it assumes that the output bounds were already set on all of the output nodes

        input_query_of_original_network would be used to evaluate possible sat
        results later on.
        from assumption (5) we know that the input nodes wont change their global id throughout the program life,
        so we can use this old input query knowing that when a possible solution would tell us to. for example, set
        input node with global id 5 to be 1.2, then it would be the input node with global id 5 from the start

        also from assumption (6) we now that the output nodes global id would remain the same (this assumption also
        gives us the same guarantee for the input nodes so with assumption 5 we are double sure that input nodes
        ids wont change)

        :param input_nodes_global_incoming_ids:
        :param output_nodes_global_incoming_ids:

        """
        self.input_query_of_original_network = self.input_query_reference.copy()
        self.input_nodes_global_incoming_ids = input_nodes_global_incoming_ids
        self.output_nodes_global_incoming_ids = output_nodes_global_incoming_ids

    def get_counter_example_of_last_solution_attempt(self):
        return self.counter_example_of_last_solution_attempt

    def evaluate_if_result_of_last_verification_attempt_is_a_valid_counterexample(self):
        """
        :return:
        if the evaluation is SAT it returns SAT and saves the result in result_of_last_evaluation
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
            value_given = self.counter_example_of_last_solution_attempt[node_global_id]
            input_query_to_eval.setLowerBound(node_global_id, value_given)
            input_query_to_eval.setUpperBound(node_global_id, value_given)

        options = None  ########################### check what are those options
        filename_to_save_log_in = ""
        map_of_node_to_value, stats = MarabouCore.solve(input_query_to_eval, options, filename_to_save_log_in)

        if len(self.counter_example_of_last_solution_attempt) > 0:
            # there is a SAT solution
            self.result_of_last_evaluation = map_of_node_to_value
            return GlobalDataManager.SAT
        else:
            return GlobalDataManager.UNSAT

    def verify(self):
        """
        gives a clone of the input query to the solving engine and returns the result
        :return: SAT or UN-SAT indicating whether or not the input query has a counter example
        if it does, the counter example would be saved.

        the counter example could be retrieved by calling get_counter_example_input_query_of_last_solution_attempt
        the counter example could also be checked if its a correct counter example or not.
        """
        input_query_copy = self.input_query_reference.copy()
        options = None  ########################### check what are those options
        filename_to_save_log_in = ""

        # if I understand correctly this is a map of "node_global_id -> value it got"
        self.counter_example_of_last_solution_attempt, stats = \
            MarabouCore.solve(input_query_copy, options, filename_to_save_log_in)

        if len(self.counter_example_of_last_solution_attempt) > 0:
            # there is a SAT solution
            return GlobalDataManager.SAT

        return GlobalDataManager.UNSAT

    def _set_artificial_bounds_on_a_hole_id(self, hole_id):
        """
        :param hole_id: an id that is currently in the range of possible ids to give, such that its presence makes
        a hole in self.ranges
        it artificially sets a bound of 0,0 on it
        """
        self.input_query_reference.setLowerBound(hole_id, 0)
        self.input_query_reference.setUpperBound(hole_id, 0)

    def _remove_artificial_bounds_on_a_hole_id(self, hole_id):
        """
        :param hole_id: an id that is currently in the range of possible ids to give, such that its presence makes
        a hole in self.ranges
        removes the artificial bounds that were set on the hole id
        """
        self.input_query_reference.removeBounds(hole_id)

    def set_number_of_variables(self, number_of_variables):
        self.input_query_reference.setNumberOfVariables(number_of_variables)

    def reset_number_of_variables_in_input_query(self):
        """
        check what is the maximum id that was given away and sets the number of variables in the system to be
        it + 1
        :return: how many variables there are in the system right now
        """
        num_of_variables_in_system = self.get_maximum_id_used() + 1
        self.input_query_reference.setNumberOfVariables(num_of_variables_in_system)

        return num_of_variables_in_system

    def get_new_id(self):
        to_return = super().get_new_id()

        if self._check_if_ranges_has_holes():
            # then the id we are going to return is a hole id.
            # we need to remove the artificial bounds that were set on it
            self._remove_artificial_bounds_on_a_hole_id(to_return)

        return to_return

    def give_id_back(self, id_returned):
        """
        :param id_returned: an id that should be marked as available
        for now this function almost completely trusts the user that a correct id is given back
        (i.e. we only get an id that was given before)

        also, this function assumes that the user "cleaned" the id before returning it.
        i.e. no bounds, relu constraints, or any other kind of things are related to the id.
        so the user should not expect that this function will "clean" the id for him. this fact is used in outside
        classes, so be very careful if you want to change it.
        """

        length_of_ranges_before_insertion = len(self.ranges)
        largest_available_id_before_insertion = self.ranges[IDManager.LOCATION_OF_LARGEST_AVAILABLE_ID]

        super().give_id_back(id_returned)

        # before finishing there are a couple of checks to make.
        # first check if the id_returned merged the 2 final ranges
        # (for example ranges was [0,1,5,9,10,max] and we inserted 9 then now ranges is [0,1,5,max])
        # if that happened then we can reduce the number of variables in the input query
        # (for example, in the state [0,1,5,9,10,max] we held ids 5,6,7,8 as hole ids, and after inserting 9
        # we can reduce the number of used variables in the input query to 5 (0,1,2,3,4) (with 0 being a hole id))
        if length_of_ranges_before_insertion > IDManager.LENGTH_OF_SIMPLE_RANGE:
            # if the length_of_ranges_before_insertion was 2 then we couldn't have "merge the 2 final ranges"
            # since there were no 2 final ranges.
            # so this subsequence would only run when there is a possibility of merger.
            current_largest_available_id = self.ranges[IDManager.LOCATION_OF_LARGEST_AVAILABLE_ID]
            if largest_available_id_before_insertion != current_largest_available_id:
                # then the final range [a, max] was changed, and the only way it could have changed is by merging
                # the 2 final ranges. so we get rid of all unnecessary variables
                # since all the ids we are about to return were hole ids,
                for i in range(current_largest_available_id, largest_available_id_before_insertion):
                    self._remove_artificial_bounds_on_a_hole_id(i)
                # now reset the number of used variables
                self.reset_number_of_variables_in_input_query()
        else:
            # check for holes
            if len(self.ranges) == IDManager.LENGTH_OF_SIMPLE_RANGE:
                # then the id we inserted did not create a new hole,
                # the only way it could happen is if the id returned was the largest id given
                # so we can simply reduce the number of used variables by 1 (since we gave up our largest used id)
                self.reset_number_of_variables_in_input_query()
            else:
                # the inserted id should be treated as a hole id
                self._set_artificial_bounds_on_a_hole_id(id_returned)
