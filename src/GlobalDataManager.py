from maraboupy import MarabouCore
from maraboupy.Marabou import createOptions

"""
manage all global data which is required for the marabou system
- global ids : can automatically reduce the number of used variables or set bounds on 
"artificial variables" which are not being used.

- input query

- equation

- solving and evaluating the network - would be used to save the original network input query
and use it to evaluate a proposed solution

"""


class GlobalDataManager:
    LOCATION_OF_LARGEST_AVAILABLE_ID = -2
    LENGTH_OF_SIMPLE_RANGE = 2  # if self.ranges is of that length then its of the form [a, max]

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
        self.max_id = max_id_non_exclusive
        """
        the list will hold an ordered list of ranges of the form [a,b],[c,d],[e,f],...
        (such that for the range [a,b] valid ids to give would be a,a+1,..., b-1)
        in order to save space declaring useless lists the ranges will be held
        consecutively as such: a,b,c,d,e,f,...
        """
        self.ranges = [0, max_id_non_exclusive]

        self.input_query_reference = MarabouCore.InputQuery()
        self.input_query_of_original_network = None

        self.counter_example_of_last_solution_attempt = None

    def save_current_input_query_as_original_network(self):
        """
        this function copies the current self.input_query_reference and saves it to
        self.input_query_of_original_network

        input_query_of_original_network would be used to evaluate possible sat
        results later on.
        from assumption (5) we know that the input nodes wont change their id throughout the program life,
        so we can use this old input query knowing that when a possible solution would tell us to. for example, set
        input node with global id 5 to be 1.2, then it would be the input node with global id 5 from the start
        """
        self.input_query_of_original_network = self.input_query_reference.copy()

    def addEquation(self, equation):
        self.input_query_reference.addEquation(equation)

    def removeEquation(self, equation):
        self.input_query_reference.removeEquation(equation)

    def setLowerBound(self, node_global_incoming_id, lower_bound):
        """
        given a node global incoming id, it places the given lower bound on it
        :param node_global_incoming_id:
        :param lower_bound:
        :return:
        """
        return self.input_query_reference.setLowerBound(node_global_incoming_id, lower_bound)

    def setUpperBound(self, node_global_incoming_id, upper_bound):
        """
        given a node global incoming id, it places the given upper bound on it
        :param node_global_incoming_id:
        :param upper_bound:
        :return:
        """
        return self.input_query_reference.setUpperBound(node_global_incoming_id, upper_bound)

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

    def get_counter_example_of_last_solution_attempt(self):
        return self.counter_example_of_last_solution_attempt

    def evaluate_if_result_of_last_solution_attempt_is_a_valid_counterexample(self):
        #######################################################################################################################
        """
        the trick to implement this function
        is to run the marabou solving function on the input nodes
        where for each input node we have upper_bound_i=lower_bound_i=k
        
        :return:
        """

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

        self.counter_example_of_last_solution_attempt, stats = \
            MarabouCore.solve(input_query_copy, options, filename_to_save_log_in)

        if len(self.counter_example_of_last_solution_attempt) > 0:
            # there is a SAT solution
            return GlobalDataManager.SAT

        return GlobalDataManager.UNSAT

    def _check_if_ranges_has_holes(self):
        """
        :return: true if the range of free ids has holes in it, i.e. if self.ranges is not
        of the form [a, max_id_non_exclusive]
        """
        # since the only time the ranges wont have holes is when it is in the form [a, max_id_non_exclusive]
        # we simply need to check if its length is different than 2
        return len(self.ranges) != 2

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

    def _insert_id_into_ranges(self, id_to_insert):
        """
        uses a binary insertion algorithm
        :param id_to_insert:
        :return the index in self.ranges that the id was inserted in
        """
        start = 0
        end = len(self.ranges)

        while start + 1 < end:
            to_check = (start + end) // 2

            if self.ranges[to_check] > id_to_insert:
                end = to_check
            else:
                start = to_check

        #  the end variable will hold the location to push the new range
        #  make sure it is a valid starting location (a valid one is divisible by 2)
        if end % 2 != 0:
            end -= 1

        # now push the "range" [id, id+1] to the vector
        self.ranges = self.ranges[:end] + [id_to_insert, id_to_insert + 1] + self.ranges[end:]

        return end

    def get_new_id(self):
        if len(self.ranges) == 0:
            raise ValueError('there are no available ids')

        ranges_has_holes = self._check_if_ranges_has_holes()

        to_return = self.ranges[0]
        self.ranges[0] += 1

        # check if the first range is finished, if so, remove it
        if self.ranges[0] == self.ranges[1]:
            self.ranges = self.ranges[2:]

        if ranges_has_holes:
            # then the id we are going to return is a hole id.
            # we need to remove the artificial bounds that were set on it
            self._remove_artificial_bounds_on_a_hole_id(to_return)
        return to_return

    def give_id_back(self, id_returned):
        """
        :param id_returned: an id that should be marked as available
        for now this function almost completely trusts the user that a correct id is given back
        (i.e. we only get an id that was given before)
        """
        if id_returned >= self.max_id:
            raise ValueError('the id was never given')

        length_of_ranges_before_insertion = len(self.ranges)
        largest_available_id_before_insertion = self.ranges[GlobalDataManager.LOCATION_OF_LARGEST_AVAILABLE_ID]

        index_inserted = self._insert_id_into_ranges(id_returned)

        # now check if we can merge adjacent ranges
        # first check if the range can be merged backwards
        if index_inserted > 0:
            if self.ranges[index_inserted] == self.ranges[index_inserted - 1]:
                self.ranges[index_inserted - 1] = self.ranges[index_inserted + 1]

                # delete the irrelevant range end and begin
                self.ranges = self.ranges[:index_inserted] + self.ranges[index_inserted + 2:]

                # now update index_inserted to a correct value
                index_inserted -= 2

        # now check if the range can be merged forwards
        index_inserted += 1
        if index_inserted < len(self.ranges) - 1:
            if self.ranges[index_inserted] == self.ranges[index_inserted + 1]:
                self.ranges[index_inserted + 1] = self.ranges[index_inserted - 1]

                # delete the irrelevant range end and begin
                self.ranges = self.ranges[:index_inserted] + self.ranges[index_inserted + 2:]

        # before finishing there are a couple of checks to make.
        # first check if the id_returned merged the 2 final ranges
        # (for example ranges was [0,1,5,9,10,max] and we inserted 9 then now ranges is [0,1,5,max])
        # if that happened then we can reduce the number of variables in the input query
        # (for example, in the state [0,1,5,9,10,max] we held ids 5,6,7,8 as hole ids, and after inserting 9
        # we can reduce the number of used variables in the input query to 5 (0,1,2,3,4) (with 0 being a hole id))
        if length_of_ranges_before_insertion > GlobalDataManager.LENGTH_OF_SIMPLE_RANGE:
            # if the length_of_ranges_before_insertion was 2 then we couldn't have "merge the 2 final ranges"
            # since there were no 2 final ranges.
            # so this subsequence would only run when there is a possibility of merger.
            current_largest_available_id = self.ranges[GlobalDataManager.LOCATION_OF_LARGEST_AVAILABLE_ID]
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
            if len(self.ranges) == GlobalDataManager.LENGTH_OF_SIMPLE_RANGE:
                # then the id we inserted did not create a new hole,
                # the only way it could happen is if the id returned was the largest id given
                # so we can simply reduce the number of used variables by 1 (since we gave up our largest used id)
                self.reset_number_of_variables_in_input_query()
            else:
                # the inserted id should be treated as a hole id
                self._set_artificial_bounds_on_a_hole_id(id_returned)

    def get_maximum_id_used(self):
        """
        :return: the maximum id that was given away
        if no ids were given it returns -1
        """
        return self.ranges[GlobalDataManager.LOCATION_OF_LARGEST_AVAILABLE_ID] - 1

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
