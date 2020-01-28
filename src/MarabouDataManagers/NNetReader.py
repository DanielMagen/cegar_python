class NNetReader:
    def __init__(self, file_name):
        # copied from the MarabouNetworkNNet class in marabou
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

    def get_bias_for_node(self, layer_number, index_of_node_in_layer):
        """
        :param layer_number:
        :param index_of_node_in_layer:
        :return: the bias for the (index_of_node_in_layer)th node in the given layer
        """
        # if you ever want to get the bias from an acasNnet matrix (which would be necessary when the code
        # would be transferred to cpp)
        # then use this code:
        # LOCATION_OF_BIASES = 0
        #         if layer_number == Network.LOCATION_OF_FIRST_LAYER:
        #             return Node.NO_BIAS
        #         return matrix[layer_number - 1][LOCATION_OF_BIASES][index_in_layer_of_node][0]
        return self.biases[layer_number][index_of_node_in_layer]

    def get_weight_of_connection(self, layer_number, index_of_node_in_layer, index_of_node_in_previous_layer):
        """
        :param layer_number:
        :param index_of_node_in_layer:
        :param index_of_node_in_previous_layer:
        :return: the weight of connection between (index_in_layer_of_node)th node in the given layer
        and (index_of_node_in_previous_layer)th node in the previous layer
        """
        # if you ever want to get the weight from an acasNnet matrix (which would be necessary when the code
        # would be transferred to cpp)
        # then use this code:
        # LOCATION_OF_WEIGHTS = 0
        # return matrix[layer_number][LOCATION_OF_WEIGHTS][index_of_node_in_layer][index_of_node_in_previous_layer]
        return self.weights[layer_number][index_of_node_in_layer][index_of_node_in_previous_layer]
