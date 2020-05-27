# cegar_python
the first implementation of cegar in python 

based on the paper "An Abstraction-Based Framework for Neural Network Verification" by Yizhak Yisrael Elboher, Justin Gottschlich, Guy Katz
https://arxiv.org/abs/1910.14574

this is the first implementation of cegar in python. the intent of this implementation is to provide a working cegar program that can easily be converted into CPP form before finally merging with Marabou https://github.com/guykatzz/Marabou
as such the implementation of cegar is CPP oriented and not python oriented, i.e. I avoided (as much as possible) using python libraries and functions which can't be replicated easily in CPP, as the intent is to migrate the implementation to CPP.


the idea behind this implementation is to support a plethora of actions in a single united data structure
while allowing outer algorithms to determine which operations should take place and in what order.
in other words, we focus on separating between the implementation and actual decisions made.


Each neural network would be represented by both a real live network that can be used for computation and experiments,
and the inner representation, which is cegar oriented, which we would implement here.

each network inner representation would be implemented as a system of nested managers:

network > layer managers > table managers > nodes > node edges
