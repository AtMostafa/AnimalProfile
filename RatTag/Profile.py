import logging


class Profile:
    """
    this class operates on profile files:
    updating them, and collecting the defined values
    to give a simpler interface to the user
    """
    FREEZE = False

    def __init__(self, *, root):
        self._root = root
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

    def __add__(self, other):
        assert isinstance(other, type(self)), f'only {type(self)}s can be added.'
        out = Profile(root=self._root)
        for key in self.keys():
            if getattr(self, key) is [None]:
                setattr(out, key, getattr(other, key))
            elif getattr(other, key) is [None]:
                setattr(out, key, getattr(self, key))
            else:
                setattr(out, key,
                        list(
                            set(
                                getattr(self, key) + getattr(other, key)
                            )))
        return out

    def _define_fields(self):
        try:
            for field in self._headerFields:
                setattr(self, field, [])
            for field in self._tableFields:
                setattr(self, field, [])
        except SyntaxError:
            logging.critical('field names MUST be valid variable names in python.')

    def from_dict(self, profileDict: dict):
        for key, val in profileDict.items():
            if key in self.__dict__:
                setattr(self, key, val)
        return self

    def keys(self):
        keys = [key for key in self._headerFields]
        keys.extend([key for key in self._tableFields])
        return tuple(keys)


class EventProfile:
    """
    holds the results of the 'batch_get_event' function
    """
    def __init__(self, profile1: Profile, profile2: Profile):
        assert self.is_single_animal(profile1) and self.is_single_animal(profile2),\
            'Sessions of the inputs must be from a single animal.'
        self.before = profile1
        self.after = profile2

    def is_single_animal(self, profile: Profile):
        prefixL = len(profile._prefix)
        animals = [session[: prefixL + 3] for session in profile.Sessions]
        if len(set(animals)) > 1:
            return False
        return True


if __name__ == "__main__":
    from Root import Root
    a = Profile(root=Root())
    print(a)
