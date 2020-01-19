
class IDManager:
    LOCATION_OF_LARGEST_AVAILABLE_ID = -2
    LENGTH_OF_SIMPLE_RANGE = 2  # if self.ranges is of that length then its of the form [a, max]

    """
    currently this class does not support reaching the end of its available id range.
    if we exhaust the ids, then the class behavior is no defined. it would make errors. 
    so do not exhaust the id ranges in it!
    """

    def __init__(self, max_id_non_exclusive):
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

    def _check_if_ranges_has_holes(self):
        """
        :return: true if the range of free ids has holes in it, i.e. if self.ranges is not
        of the form [a, max_id_non_exclusive]
        """
        # since the only time the ranges wont have holes is when it is in the form [a, max_id_non_exclusive]
        # we simply need to check if its length is different than 2
        return len(self.ranges) != 2

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

        # check if the first range is finished, if so, remove it
        if self.ranges[0] == self.ranges[1]:
            self.ranges = self.ranges[2:]

        return to_return

    def give_id_back(self, id_returned):
        """
        :param id_returned: an id that should be marked as available
        for now this function almost completely trusts the user that a correct id is given back
        (i.e. we only get an id that was given before)

        also, this function assumes that the user "cleaned" the id before returning it.
        i.e. no bounds, relu constraints, or any other kind of things are related to the id.
        so the user should not expect that this function will "clean" the id for him. this fact is used in outside
        classes, so be very careful if you want to change it.
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

    def get_maximum_id_used(self):
        """
        :return: the maximum id that was given away
        if no ids were given it returns -1
        """
        return self.ranges[IDManager.LOCATION_OF_LARGEST_AVAILABLE_ID] - 1

