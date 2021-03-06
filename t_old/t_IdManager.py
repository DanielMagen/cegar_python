from src.IDManager import IDManager

"""
tests only the id manager part of the global data manager
"""


id_giver = IDManager()
for i in range(11):
    id_giver.get_new_id()

assert id_giver.ranges == [11, float('inf')]

id_giver.give_id_back(5)
id_giver.give_id_back(7)
id_giver.give_id_back(6)
assert id_giver.ranges == [5, 8, 11, float('inf')]

id_giver.give_id_back(1)
id_giver.give_id_back(3)
id_giver.give_id_back(2)
assert id_giver.ranges == [1, 4, 5, 8, 11, float('inf')]

id_giver.give_id_back(4)
assert id_giver.ranges == [1, 8, 11, float('inf')]

id_giver.give_id_back(0)
assert id_giver.ranges == [0, 8, 11, float('inf')]

id_giver.give_id_back(8)
id_giver.give_id_back(9)
assert id_giver.ranges == [0, 10, 11, float('inf')]

id_giver.give_id_back(10)
assert id_giver.ranges == [0, float('inf')]
