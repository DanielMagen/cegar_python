class Node:
    """
    this class would represent a node that would work under the following assumptions:
    1) each layer containing the nodes would be segmented into a consecutive list of tables, and the number of such
    tables per layer would be known and unchanging by the time this node is created.

    2) the node can not be moved to another layer

    3) nodes are not connected to other nodes in the same layer

    4) the tables of each layer would be of 2 kinds:
    a) tables in which nodes can never be deleted from
    b) tables in which nodes can be deleted from

    we will assume that the tables will be ordered such that all tables of type a occur before tables of type b
    (the tables are ordered by assumption (1))

    the node would be told how many tables support deletion in the layers its connected to

    5) nodes that are added to tables of type a will be added at the bottom of the table and
    will never move or be deleted once added. as such for the nodes that reside in those tables,
    the nodes index_in_table would serve as an absolute unchanging id


    """

    def __init__(self,
                 number_of_tables_the_previous_layer_is_segmented_to,
                 number_of_tables_the_next_layer_is_segmented_to,
                 number_of_tables_that_support_deletion_in_previous_layer,
                 number_of_tables_that_support_deletion_in_next_layer,
                 layer_number, table_number, index_in_table):
        """

        note that from assumption (3) we do need to care about tables in the current layer
        since we have no connections to nodes in the current layer

        :param number_of_tables_the_previous_layer_is_segmented_to:
        :param number_of_tables_the_next_layer_is_segmented_to:
        :param number_of_tables_that_support_deletion_in_previous_layer:
        :param number_of_tables_that_support_deletion_in_next_layer:


        :param layer_number:
        :param table_number:
        :param index_in_table:
        """

        self.layer_number = layer_number  # use assumption (2) and do not create a set_layer_number function
        self.table_number = table_number
        self.index_in_table = index_in_table
        self.location_can_not_be_changed = False

    def set_in_stone(self):
        """
        removes the ability to change the node layer, table and index in the table
        """
        self.location_can_not_be_changed = True

    def get_location(self):
        """
        :return: [table_number, index_in_table]
        """
        # using assumption (2), since the node can not be moved to another layer we do not include the layer number
        # in the id. hence the node id is unique only in the preview of the layer its in
        return [self.table_number, self.index_in_table]

    def _check_location_can_be_changed(self):
        """
        if the node location can not be changed it raises an error
        otherwise it does nothing
        """
        if self.location_can_not_be_changed:
            raise Exception("the node location cannot be changed")

    def notify_all_neighbors_that_location_changed(self, previous_location):
        """
        :param previous_location:
        goes over all neighbors of the node and notifies them that this node has been moved to another location
        within the layer (using assumption (2))
        """
        pass

    def set_table_and_index_in_table(self, table_number, index_in_table):
        self._check_location_can_be_changed()

        previous_id = self.get_location()
        self.table_number = table_number
        self.index_in_table = index_in_table

        self.notify_all_neighbors_that_location_changed(previous_id)
