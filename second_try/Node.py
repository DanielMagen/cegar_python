class Node:
    """
    this class would represent a node that would work under the assumptions detailed in
    the ASSUMPTIONS file
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

        the following arguments given are explained in assumption (4)

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
