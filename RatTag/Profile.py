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
    
    def __str__(self):
        str1 = '\n'.join([f'{field}={getattr(self,field)}' for field in self._headerFields])
        str2 = '\n'.join([f'{field}={getattr(self,field)}' for field in self._tableFields])
        return f'\nHeader: {str1};\n\nBody: {str2}'

    def __repr__(self):
        return self.__str__()

    def __setattr__(self, name, value):
        if not self.FREEZE:
            super().__setattr__(name, value)
        elif name in self._headerFields or name in self._tableFields:
            assert isinstance(value, (str, list, tuple, type(None))), f"values must be string/list/tuple, not {type(value)}"
            if isinstance(value, (str, type(None))):
                value = [value]
            super().__setattr__(name, list(value))
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

    def keys(self):
        keys = [key for key in self._headerFields]
        keys.extend([key for key in self._tableFields])
        return tuple(keys)


if __name__ == "__main__":
    from Root import Root
    a = Profile(root=Root())
    print(a)
