from second_try.Layer import *


class Network:
    def __init__(self, number_of_layers_in_network):
        self.layers = [Layer() for _ in range(number_of_layers_in_network)]

    def preprocess_network_up_to_minimal_layer(self, number_of_layers_to_preprocess):
        """
        :param number_of_layers_to_preprocess: the
        :return:
        """

    # add more functions to enable operations on the entire network
