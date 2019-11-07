class NodeEdges:
    """
    this class would be used to hold and manage 1-sided node edges
    i.e. it will only hold either outgoing or incoming edges
    it would work under the assumptions detailed in the ASSUMPTIONS file
    """

    def __init__(self, number_of_tables_in_layer_connected_to, number_of_tables_that_support_deletion):
        """
        the following arguments given are explained in assumption (2)

        :param number_of_tables_in_layer_connected_to:
        :param number_of_tables_that_support_deletion:
        """
