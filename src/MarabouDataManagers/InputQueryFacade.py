from Mock.maraboupy import MarabouCore
# in real implementation replace with "from maraboupy import MarabouCore"
import copy


class InputQueryFacade:
    REALLY_BIG_NUMBER = 2 ** 16 - 1
    INFINITE_UPPER_BOUND = REALLY_BIG_NUMBER
    INFINITE_LOWER_BOUND = -REALLY_BIG_NUMBER

    def __init__(self):
        self.equList = []
        self.reluList = []
        self.lowerBounds = dict()
        self.upperBounds = dict()

    def copy(self):
        copy.deepcopy(self)

    def get_new_marabou_input_query_object(self, number_of_nodes, input_nodes_global_incoming_ids,
                                           output_nodes_global_incoming_ids):
        # copied/based on MarabouNetwork class from the marabou project

        ipq = MarabouCore.InputQuery()
        ipq.setNumberOfVariables(number_of_nodes)

        for inputIndex, inputVar in enumerate(input_nodes_global_incoming_ids):
            ipq.markInputVariable(inputVar, inputIndex)

        for outputIndex, outputVar in enumerate(output_nodes_global_incoming_ids):
            ipq.markOutputVariable(outputVar, outputIndex)

        for e in self.equList:
            eq = MarabouCore.Equation(e.EquationType)
            for (c, v) in e.addendList:
                assert v < number_of_nodes
                eq.addAddend(c, v)
            eq.setScalar(e.scalar)
            ipq.addEquation(eq)

        for r in self.reluList:
            ################################################ assert r[1] < number_of_nodes and r[0] < number_of_nodes
            MarabouCore.addReluConstraint(ipq, r[0], r[1])

        for l in self.lowerBounds:
            assert l < number_of_nodes
            ipq.setLowerBound(l, self.lowerBounds[l])

        for u in self.upperBounds:
            assert u < number_of_nodes
            ipq.setUpperBound(u, self.upperBounds[u])

        return ipq

    def addEquation(self, equation):
        self.equList.append(equation)

    def removeEquation(self, equation):
        if equation in self.equList:
            self.equList.remove(equation)

    def setLowerBound(self, node_global_incoming_id, lower_bound):
        """
        given a node global incoming id, it places the given lower bound on it
        :param node_global_incoming_id:
        :param lower_bound: if its -infinity it does not set any bound
        :return:
        """
        if lower_bound != float('-inf'):
            self.lowerBounds[node_global_incoming_id] = lower_bound
        else:
            self.lowerBounds[node_global_incoming_id] = InputQueryFacade.INFINITE_LOWER_BOUND

    def setUpperBound(self, node_global_incoming_id, upper_bound):
        """
        given a node global incoming id, it places the given upper bound on it
        :param node_global_incoming_id:
        :param upper_bound: if its infinity it does not set any bound
        :return:
        """
        if upper_bound != float('inf'):
            self.upperBounds[node_global_incoming_id] = upper_bound
        else:
            self.upperBounds[node_global_incoming_id] = InputQueryFacade.INFINITE_UPPER_BOUND

    def getLowerBound(self, node_global_incoming_id):
        """
        given a node global incoming id, it returns the lower bound placed on it
        :param node_global_incoming_id:
        :return: if the lower bound does not exist it returns -infinity (do not change that, we rely on this fact)
        """
        to_return = float('-inf')
        if node_global_incoming_id in self.lowerBounds:
            to_return = self.lowerBounds[node_global_incoming_id]
            if to_return == InputQueryFacade.INFINITE_LOWER_BOUND:
                to_return = float('-inf')
        return to_return

    def getUpperBound(self, node_global_incoming_id):
        """
        given a node global incoming id, it returns the upper bound placed on it
        :param node_global_incoming_id:
        :return: if the upper bound does not exist it returns infinity (do not change that, we rely on this fact)
        """
        to_return = float('-inf')
        if node_global_incoming_id in self.upperBounds:
            to_return = self.upperBounds[node_global_incoming_id]
            if to_return == InputQueryFacade.INFINITE_UPPER_BOUND:
                to_return = float('-inf')
        return to_return

    def removeBounds(self, node_global_incoming_id):
        """
        given a node global incoming id, it removes the upper and lower bounds set on it
        :param node_global_incoming_id:
        :return:
        """
        try:
            del self.lowerBounds[node_global_incoming_id]
        except KeyError:
            pass
        try:
            del self.upperBounds[node_global_incoming_id]
        except KeyError:
            pass

    def addReluConstraint(self, id1, id2):
        self.reluList.append((id1, id2))

    def removeReluConstraint(self, id1, id2):
        if (id1, id2) in self.reluList:
            self.reluList.remove((id1, id2))

    @staticmethod
    def get_new_equation():
        return MarabouCore.Equation()
