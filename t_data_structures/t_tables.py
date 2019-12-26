from src.Tables.Table import AbstractTable
from src.Tables import TableSupportsDeletion
from src.Tables import TableDoesntSupportsDeletion
from src.Tables import ARNodeTable
from src.Nodes.Node import Node
import random


def create_tables_of_same_type(t, num_to_create):
    to_return = [t]
    for i in range(num_to_create):
        t = t.create_table_below_of_same_type()
        to_return.append(t)

    return to_return


def get_TableSupportsDeletion(number_of_tables):
    t1 = TableSupportsDeletion.TableSupportsDeletion(0)
    return create_tables_of_same_type(t1, number_of_tables - 1)


def get_TableDoesntSupportsDeletion(number_of_tables):
    t1 = TableDoesntSupportsDeletion.TableDoesntSupportsDeletion(0)
    return create_tables_of_same_type(t1, number_of_tables - 1)


def get_ARNodeTable(number_of_tables):
    t1 = ARNodeTable.ARNodeTable(0)
    return create_tables_of_same_type(t1, number_of_tables - 1)


def check_all_tables_have_zero_nodes(tables):
    for t in tables:
        assert t.get_number_of_nodes_in_table() == 0


if __name__ == "__main__":
    num_of_tables = random.randint(5, 7)
    # first check the tables that support deletion
    function_to_create_tables = get_TableSupportsDeletion
    tables = function_to_create_tables(num_of_tables)
    check_all_tables_have_zero_nodes(tables)

    # now check the tables that don't support deletion
    function_to_create_tables = get_TableDoesntSupportsDeletion
    tables = function_to_create_tables(num_of_tables)
    check_all_tables_have_zero_nodes(tables)

    # testing the arnode tables would be done when we would test the layers since
    # the key functions there would be split and merge functions which would require different layers
    # to test correctly


