# this is a mock class that is intended to receive the calls for marabou

class mock_input_query:
    pass


class mock_equation:
    pass


def InputQuery():
    return mock_input_query()


def Equation(EquationType='are there 2 possible equation functions? one function receive input and the other doesnt'):
    return mock_equation()


def addReluConstraint(InputQuery_object, var1, var2):
    pass


def solve(InputQuery_object, options, filename_to_save_log_in):
    return {}, ''
