from src.Tables.Table import AbstractTable
from src.Tables import TableSupportsDeletion
from src.Tables import TableDoesntSupportsDeletion
from src.Tables import ARNodeTable
import random


def create_tables_of_same_type(t, num_to_create):
    to_return = [t]
    for i in range(num_to_create):
        t = t.create_table_below_of_same_type()
        to_return.append(t)

    return to_return


def get_TableSupportsDeletion(number_of_tables):
    t1 = TableSupportsDeletion.TableSupportsDeletion(0, AbstractTable.NO_PREVIOUS_TABLE,
                                                     AbstractTable.NO_NEXT_TABLE)
    return create_tables_of_same_type(t1, number_of_tables - 1)


def get_TableDoesntSupportsDeletion(number_of_tables):
    t1 = TableDoesntSupportsDeletion.TableDoesntSupportsDeletion(0, AbstractTable.NO_PREVIOUS_TABLE,
                                                                 AbstractTable.NO_NEXT_TABLE)
    return create_tables_of_same_type(t1, number_of_tables - 1)


def get_ARNodeTable(number_of_tables):
    t1 = ARNodeTable.ARNodeTable(0, AbstractTable.NO_PREVIOUS_TABLE,
                                 AbstractTable.NO_NEXT_TABLE)
    return create_tables_of_same_type(t1, number_of_tables - 1)


def check_all_tables_have_zero_nodes(tables):
    for t in tables:
        assert t.get_number_of_nodes_in_table() == 0


def check_starting_index_is_not_initialized(tables):
    for t in tables:
        t.decrease_starting_node_index()

    for t in tables:
        assert t.table_starting_index == AbstractTable.INDEX_OF_START_IF_NO_NODES_IN_TABLE

    for t in tables:
        t.increase_starting_node_index()

    for t in tables:
        assert t.table_starting_index == AbstractTable.INDEX_OF_START_IF_NO_NODES_IN_TABLE

    for t in tables:
        assert t.get_number_of_nodes_after_table_ends() == 0


def check_adding_and_removing_nodes(tables):
    def get_tables_starting_indices():
        return list(map(lambda t: t.table_starting_index, tables))

    number_of_tables_in_previous_layer = random.randint(1, 15)
    number_of_tables_in_next_layer = random.randint(1, 15)

    starting_indices = get_tables_starting_indices()

    tables[0].create_new_node_and_add_to_table(number_of_tables_in_previous_layer, number_of_tables_in_next_layer)
    starting_indices[0] = 0
    assert get_tables_starting_indices() == starting_indices

    # adding more nodes to the same table does not change its starting index
    tables[0].create_new_node_and_add_to_table(number_of_tables_in_previous_layer, number_of_tables_in_next_layer)
    assert get_tables_starting_indices() == starting_indices

    # deleting 1 of 2 nodes does not change the starting index of the table
    tables[0].delete_node(0)
    assert get_tables_starting_indices() == starting_indices

    # deleting the second node should change the starting index
    tables[0].delete_node(1)
    starting_indices[0] = AbstractTable.INDEX_OF_START_IF_NO_NODES_IN_TABLE
    assert get_tables_starting_indices() == starting_indices

    # check that adding and removing nodes transfers well between tables
    tables[0].create_new_node_and_add_to_table(number_of_tables_in_previous_layer, number_of_tables_in_next_layer)
    tables[0].create_new_node_and_add_to_table(number_of_tables_in_previous_layer, number_of_tables_in_next_layer)
    tables[4].create_new_node_and_add_to_table(number_of_tables_in_previous_layer, number_of_tables_in_next_layer)
    starting_indices[0] = 0
    starting_indices[4] = 2
    assert get_tables_starting_indices() == starting_indices

    tables[0].delete_node(0)
    starting_indices[4] -= 1
    assert get_tables_starting_indices() == starting_indices


num_of_tables = random.randint(5, 7)
tables = get_TableSupportsDeletion(num_of_tables)
check_all_tables_have_zero_nodes(tables)
check_starting_index_is_not_initialized(tables)
check_adding_and_removing_nodes(tables)
