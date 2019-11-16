from src.Layer import *


class Network:
    NUMBER_OF_TABLES_IN_LAYER = Layer.NUMBER_OF_REGULAR_TABLES_THAT_DO_NOT_SUPPORT_DELETION + 1

    def __init__(self, number_of_layers_in_network):
        self.number_of_layers_in_network = number_of_layers_in_network

        if number_of_layers_in_network > 1:
            self.layers = [Layer(0, Network.NUMBER_OF_TABLES_IN_LAYER)]
            self.layers.extend([Layer(Network.NUMBER_OF_TABLES_IN_LAYER, Network.NUMBER_OF_TABLES_IN_LAYER) for _ in
                                range(number_of_layers_in_network - 2)])
            self.layers.append(Layer(Network.NUMBER_OF_TABLES_IN_LAYER, 0))
        else:
            self.layers = [Layer(0, 0)]

        self.last_layer_not_preprocessed = number_of_layers_in_network - 1

    def preprocess_more_layers(self, number_of_layers_to_preprocess):
        """
        :param number_of_layers_to_preprocess:
        preprocess 'number_of_layers_to_preprocess' network layers which were not already preprocessed
        the preprocess procedure is carried from end to start
        """
        for i in range(self.last_layer_not_preprocessed,
                       max(-1, self.last_layer_not_preprocessed - number_of_layers_to_preprocess), -1):
            self.layers[i].preprocess_entire_layer()
            self.last_layer_not_preprocessed -= 1

    # add more functions to enable operations on the entire network
