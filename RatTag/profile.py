import logging


class Profile:
    """
    this class operates on profile files:
    updating them, and collecting the defined values
    to give a simpler interface to the user
    """
    FREEZE = False

    def __init__(self, *, root):
        self._root = root.root
        self._prefix = root.prefix
        self._headerFields = root.header
        self._tableFields = root.body

        self._define_fields()

        # The last line of the INIT method
        self.FREEZE = True

    def __setattr__(self, name, value):
        if not self.FREEZE:
            super().__setattr__(name, value)
        elif name in self._headerFields or name in self._tableFields:
            assert isinstance(value, (str, list, tuple, type(None))), f"values must be string/list/tuple, not {type(value)}"
            super().__setattr__(name, value)
        else:
            logging.error(f'Field "{name}" does not exist in profiles')
    
    def _define_fields(self):
        try:
            for field in self._headerFields:
                setattr(self, field, None)
            for field in self._tableFields:
                setattr(self, field, None)
        except SyntaxError:
            logging.critical('field names MUST be valid variable names in python.')

    def get_all_animals(self):
        return sorted(self._root.glob(f'{self._prefix}???/'))

    def from_dict(self, profileDict: dict):
        for key, val in profileDict.items():
            if key in self.__dict__:
                setattr(self, key, val)
        return self

if __name__ == "__main__":
    from root import Root
    a = Profile(root=Root())
    print(a)
