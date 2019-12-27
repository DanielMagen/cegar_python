class GlobalDataManager:
    def __init__(self, max_id_non_exclusive, marabou_core, input_query):
        """
        this class would give available ids in increasing order
        :param max_id_non_exclusive: the maximum id that can be given
        """
        self.max_id = max_id_non_exclusive
        """
        the list will hold an ordered list of ranges of the form [a,b],[c,d],[e,f],...
        (such that for the range [a,b] valid ids to give would be a,a+1,..., b-1)
        in order to save space declaring useless lists the ranges will be held
        consecutively as such: a,b,c,d,e,f,...
        """
        self.ranges = [0, max_id_non_exclusive]

        self.marabou_core_reference = marabou_core
        self.input_query_reference = input_query

    def get_input_query_reference(self):
        return self.input_query_reference

    def get_marabou_core_reference(self):
        return self.marabou_core_reference

    def _insert_id_into_ranges(self, id_to_insert):
        """
        uses a binary insertion algorithm
        :param id_to_insert:
        :return the index in self.ranges that the id was inserted in
        """
        start = 0
        end = len(self.ranges)

        while start + 1 < end:
            to_check = (start + end) // 2

            if self.ranges[to_check] > id_to_insert:
                end = to_check
            else:
                start = to_check

        #  the end variable will hold the location to push the new range
        #  make sure it is a valid starting location (a valid one is divisible by 2)
        if end % 2 != 0:
            end -= 1

        # now push the "range" [id, id+1] to the vector
        self.ranges = self.ranges[:end] + [id_to_insert, id_to_insert + 1] + self.ranges[end:]

        return end

    def get_new_id(self):
        if len(self.ranges) == 0:
            raise ValueError('there are no available ids')

        to_return = self.ranges[0]
        self.ranges[0] += 1

        # check if you
        if self.ranges[0] == self.ranges[1]:
            self.ranges = self.ranges[2:]

        return to_return

    def give_id_back(self, id_returned):
        """
        :param id_returned: an id that should be marked as available
        """
        if id_returned >= self.max_id:
            raise ValueError('the id was never given')

        index_inserted = self._insert_id_into_ranges(id_returned)

        # now check if we can merge adjacent ranges
        # first check if the range can be merged backwards
        if index_inserted > 0:
            if self.ranges[index_inserted] == self.ranges[index_inserted - 1]:
                self.ranges[index_inserted - 1] = self.ranges[index_inserted + 1]

                # delete the irrelevant range end and begin
                self.ranges = self.ranges[:index_inserted] + self.ranges[index_inserted + 2:]

                # now update index_inserted to a correct value
                index_inserted -= 2

        # now check if the range can be merged forwards
        index_inserted += 1
        if index_inserted < len(self.ranges) - 1:
            if self.ranges[index_inserted] == self.ranges[index_inserted + 1]:
                self.ranges[index_inserted + 1] = self.ranges[index_inserted - 1]

                # delete the irrelevant range end and begin
                self.ranges = self.ranges[:index_inserted] + self.ranges[index_inserted + 2:]

    def get_maximum_number_used(self):
        """
        :return: the maximum id that was given away
        if no ids were given it returns -1
        """
        return self.ranges[-2] - 1

    def set_number_of_variables(self, number_of_variables):
        self.input_query_reference.setNumberOfVariables(number_of_variables)

    def reset_number_of_variables_in_input_query(self):
        """
        check what is the maximum id that was given away and sets the number of variables in the system to be
        it + 1
        :return: how many variables there are in the system right now
        """
        num_of_variables_in_system = self.get_maximum_number_used() + 1
        self.input_query_reference.setNumberOfVariables(num_of_variables_in_system)

        return num_of_variables_in_system
