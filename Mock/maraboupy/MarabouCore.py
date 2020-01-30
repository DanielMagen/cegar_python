# this is a mock class that is intended to receive the calls for marabou


class mock_equation:
    def __init__(self):
        self.EquationType = 1
        self.addendList = []
        self.scalar = 1

    def addAddend(self, weight, id):
        pass

    def setScalar(self, bias):
        pass


class mock_input_query:
    def setNumberOfVariables(self, number_of_nodes):
        pass

    def markInputVariable(self, inputVar, inputIndex):
        pass

    def markOutputVariable(self, outputVar, outputIndex):
        pass

    def addEquation(self, eq):
        pass


def InputQuery():
    return mock_input_query()


def Equation(EquationType='are there 2 possible equation functions? one function receive input and the other doesnt'):
    return mock_equation()


def addReluConstraint(InputQuery_object, var1, var2):
    pass


def solve(InputQuery_object, options, filename_to_save_log_in):
    return {}, ''
