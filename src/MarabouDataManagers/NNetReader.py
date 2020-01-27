# copied from the MarabouNetworkNNet class in marabou
class NNetReader:
    def __init__(self, file_name):
        with open(file_name) as f:
            line = f.readline()
            cnt = 1
            while line[0:2] == "//":
                line = f.readline()
                cnt += 1
            # numLayers does't include the input layer!
            numLayers, inputSize, outputSize, maxLayersize = [int(x) for x in line.strip().split(",")[:-1]]
            line = f.readline()

            # input layer size, layer1size, layer2size...
            layerSizes = [int(x) for x in line.strip().split(",")[:-1]]

            line = f.readline()
            symmetric = int(line.strip().split(",")[0])

            line = f.readline()
            inputMinimums = [float(x) for x in line.strip().split(",")[:-1]]

            line = f.readline()
            inputMaximums = [float(x) for x in line.strip().split(",")[:-1]]

            line = f.readline()
            inputMeans = [float(x) for x in line.strip().split(",")[:-1]]

            line = f.readline()
            inputRanges = [float(x) for x in line.strip().split(",")[:-1]]

            weights = []
            biases = []
            for layernum in range(numLayers):

                previousLayerSize = layerSizes[layernum]
                currentLayerSize = layerSizes[layernum + 1]
                # weights
                weights.append([])
                biases.append([])
                # weights
                for i in range(currentLayerSize):
                    line = f.readline()
                    aux = [float(x) for x in line.strip().split(",")[:-1]]
                    weights[layernum].append([])
                    for j in range(previousLayerSize):
                        weights[layernum][i].append(aux[j])
                # biases
                for i in range(currentLayerSize):
                    line = f.readline()
                    x = float(line.strip().split(",")[0])
                    biases[layernum].append(x)

            self.numLayers = numLayers
            self.layerSizes = layerSizes
            self.inputSize = inputSize
            self.outputSize = outputSize
            self.maxLayersize = maxLayersize
            self.inputMinimums = inputMinimums
            self.inputMaximums = inputMaximums
            self.inputMeans = inputMeans
            self.inputRanges = inputRanges
            self.weights = weights
            self.biases = biases

    """
    those are functions that can read the data from an acasNnet object
    do not delete them because they explain how to integrate acasNnet with our code, which would be necessary when
    the code would be transferred to cpp
    
    def get_bias_for_node(layer_number, index_in_layer_of_node):
        ""
        :param layer_number:
        :param index_in_layer_of_node:
        :return: the bias for the (index_in_layer_of_node)th node in the given layer
        ""
        if layer_number == Network.LOCATION_OF_FIRST_LAYER:
            return Node.NO_BIAS
        return matrix[layer_number - 1][LOCATION_OF_BIASES][index_in_layer_of_node][0]

    def get_weight_of_connection(layer_number, index_in_layer_of_node, index_in_previous_layer_of_node):
        ""
        :param layer_number:
        :param index_in_layer_of_node:
        :param index_in_previous_layer_of_node:
        :return: the weight of connection between (index_in_layer_of_node)th node in the given layer
        and (index_in_next_layer_of_node)th node in the previous layer
        ""
        return matrix[layer_number][LOCATION_OF_WEIGHTS][index_in_layer_of_node][index_in_previous_layer_of_node]
    """

    def get_bias_for_node(self, layer_number, index_in_layer_of_node):
        pass

    def get_weight_of_connection(self, layer_number, index_in_layer_of_node, index_in_previous_layer_of_node):
        pass