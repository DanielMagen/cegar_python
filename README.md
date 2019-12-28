# cegar_python
first implementation of cegar in python 

cegar would first be implemented in python in full or close to full and then migrate to cpp before finally merging with marbou.
as such the implementation here is cpp oriented and not python oriented.


the idea is to support a plethora of actions in a single united data structure
and to allow outer algorithms to determine which operations to take and in what order.
in other words, separate between the implementation and decisions making.


each network would be represented by both a real live network that can be used for computation and experiments,
and the inner representation which we would implement here

each network inner representation would be implemented as a system of nested managers
network managers > layer managers > table managers > nodes > node edges

