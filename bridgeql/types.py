class DBRows(list):
    # override count method of list
    def count(self):
        return len(self)
