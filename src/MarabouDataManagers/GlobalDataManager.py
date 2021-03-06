from src.IDManager import IDManager
from src.MarabouDataManagers.InputQueryFacade import InputQueryFacade

"""
manage some of the global data which is required for the marabou system

- global ids : can automatically reduce the number of used variables or set bounds on 
"artificial variables" which are not being used.

- input query

- equation
"""


class GlobalDataManager(IDManager):
    UNSAT = False
    SAT = True

    CODE_FOR_NODE = 0
    CODE_FOR_ARNODE = 1

    def __init__(self):
        """
        this class would give available ids in increasing order
        """
        super().__init__()

        self.input_query = InputQueryFacade()

        # this set would hold triplets of the form (layer_number, table_number, key_in_table, SOME_CODE)
        # for nodes that dont have valid equations.
        # the CODE would be either CODE_FOR_NODE or CODE_FOR_ARNODE
        # if this set is not empty, then the solving process can not take place
        self.set_of_nodes_locations_that_dont_have_valid_equations = set([])

    def add_location_of_node_that_dont_have_valid_equation(self, layer_number, table_number, key_in_table,
                                                           is_arnode):
        if is_arnode:
            self.set_of_nodes_locations_that_dont_have_valid_equations.add(
                (layer_number, table_number, key_in_table, GlobalDataManager.CODE_FOR_ARNODE))
        else:
            self.set_of_nodes_locations_that_dont_have_valid_equations.add(
                (layer_number, table_number, key_in_table, GlobalDataManager.CODE_FOR_NODE))

    def check_if_node_has_invalid_equations(self, layer_number, table_number, key_in_table, is_arnode):
        """
        :param layer_number:
        :param table_number:
        :param key_in_table:
        :param is_arnode:
        :return: true if the given node has an invalid equation
        """
        if is_arnode:
            return (layer_number,
                    table_number,
                    key_in_table,
                    GlobalDataManager.CODE_FOR_ARNODE) in self.set_of_nodes_locations_that_dont_have_valid_equations
        else:
            return (layer_number,
                    table_number,
                    key_in_table,
                    GlobalDataManager.CODE_FOR_NODE) in self.set_of_nodes_locations_that_dont_have_valid_equations

    def remove_location_of_node_that_dont_have_valid_equation(self, layer_number, table_number, key_in_table,
                                                              is_arnode):
        # discard ignores removal of items that are not in the set, so if we are given a node which is not listed
        # we simply ignore it
        if is_arnode:
            self.set_of_nodes_locations_that_dont_have_valid_equations.discard(
                (layer_number, table_number, key_in_table, GlobalDataManager.CODE_FOR_ARNODE))
        else:
            self.set_of_nodes_locations_that_dont_have_valid_equations.discard(
                (layer_number, table_number, key_in_table, GlobalDataManager.CODE_FOR_NODE))

    def get_new_equation(self):
        return self.input_query.get_new_equation()

    def addEquation(self, equation):
        self.input_query.addEquation(equation)

    def removeEquation(self, equation):
        self.input_query.removeEquation(equation)

    def setLowerBound(self, node_global_incoming_id, lower_bound):
        self.input_query.setLowerBound(node_global_incoming_id, lower_bound)

    def setUpperBound(self, node_global_incoming_id, upper_bound):
        self.input_query.setUpperBound(node_global_incoming_id, upper_bound)

    def getLowerBound(self, node_global_incoming_id):
        return self.input_query.getLowerBound(node_global_incoming_id)

    def getUpperBound(self, node_global_incoming_id):
        return self.input_query.getUpperBound(node_global_incoming_id)

    def removeBounds(self, node_global_incoming_id):
        return self.input_query.removeBounds(node_global_incoming_id)

    def addReluConstraint(self, id1, id2):
        self.input_query.addReluConstraint(id1, id2)

    def removeReluConstraint(self, id1, id2):
        self.input_query.removeReluConstraint(id1, id2)

    def get_list_of_nodes_that_dont_have_valid_equations(self):
        """
        :return: a list of the location data of the nodes that don't have a valid equation
        note that this data is not the same as the regular location data
        the data is of form (layer_number, table_number, key_in_table, CODE)
        where CODE = CODE_FOR_NODE if the node is a regular node
        and CODE = CODE_FOR_ARNODE if the node is an arnode
        """
        return list(self.set_of_nodes_locations_that_dont_have_valid_equations)

    def _set_artificial_bounds_on_a_hole_id(self, hole_id):
        """
        :param hole_id: an id that is currently in the range of possible ids to give, such that its presence makes
        a hole in self.ranges
        it artificially sets a bound of 0,0 on it
        """
        self.input_query.setLowerBound(hole_id, 0)
        self.input_query.setUpperBound(hole_id, 0)

    def _remove_artificial_bounds_on_a_hole_id(self, hole_id):
        """
        :param hole_id: an id that is currently in the range of possible ids to give, such that its presence makes
        a hole in self.ranges
        removes the artificial bounds that were set on the hole id
        """
        self.input_query.removeBounds(hole_id)

    def get_new_id(self):
        ranges_had_holes = self._check_if_ranges_has_holes()
        to_return = super().get_new_id()

        if ranges_had_holes:
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
        classes, so be very careful if you want to change it (if you clean the id some function might not work)
        """

        length_of_ranges_before_insertion = len(self.ranges)
        largest_available_id_before_insertion = self.ranges[IDManager.LOCATION_OF_LARGEST_AVAILABLE_ID]

        super().give_id_back(id_returned)

        # now there are a couple of checks to make.
        # first check if the id_returned merged the 2 final ranges
        # (for example ranges was [0,1,5,9,10,max] and we inserted 9 then now ranges is [0,1,5,max])
        # if that happened then we can reduce the number of hole ids
        # (for example, in the state [0,1,5,9,10,max] we held ids 5,6,7,8 as hole ids, and after inserting 9
        # the hole ids 5,6,7,8,9 need to be erased
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
        else:
            # check for holes
            if len(self.ranges) != IDManager.LENGTH_OF_SIMPLE_RANGE:
                # the inserted id should be treated as a hole id
                self._set_artificial_bounds_on_a_hole_id(id_returned)
