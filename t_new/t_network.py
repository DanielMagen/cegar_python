from src.MarabouDataManagers.NNetReader import NNetReader
from src.Cegar import *

which_acas_output = 2
file_name = f'C:\\Users\\Daniel\\PycharmProjects\\cegar_python\\nnets\\ACASXU_run2a_1_1_tiny_{which_acas_output}.nnet'

reader = NNetReader(file_name)

printing = False
if printing:
    att_names = ['numLayers',
                 'layerSizes',
                 'inputSize',
                 'outputSize',
                 'maxLayersize',
                 'inputMinimums',
                 'inputMaximums',
                 'inputMeans',
                 'inputRanges',
                 'weights',
                 'biases']

    att = [reader.numLayers,
           reader.layerSizes,
           reader.inputSize,
           reader.outputSize,
           reader.maxLayersize,
           reader.inputMinimums,
           reader.inputMaximums,
           reader.inputMeans,
           reader.inputRanges,
           reader.weights,
           reader.biases]

    for i in range(len(att)):
        print(att_names[i], att[i])


run_cegar_naive(reader, which_acas_output)