from maraboupy import MarabouCore
import copy


class InputQueryFacade:
    def __init__(self):
        self.input_query_reference = MarabouCore.InputQuery()

    def copy(self):
        copy.deepcopy(self)

    def get_marabou_input_query_object(self):
        return self.input_query_reference

    def addEquation(self, equation):
        self.input_query_reference.addEquation(equation)

    def removeEquation(self, equation):
        self.input_query_reference.removeEquation(equation)

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

    def setNumberOfVariables(self, number_of_variables):
        self.input_query_reference.setNumberOfVariables(number_of_variables)
