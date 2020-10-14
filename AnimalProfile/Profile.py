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
        str1 = '\t'.join([f'{field}={getattr(self,field)}' for field in self._headerFields])
        str2 = '\t'.join([f'{field}={getattr(self,field)}' for field in self._tableFields])
        return f'\nHeader:\n{str1};\n\nBody:\n{str2}'

    def __repr__(self):
        return self.__str__()

    def __setattr__(self, name, value):
        if not self.FREEZE:
            super().__setattr__(name, value)
        elif name in self._headerFields or name in self._tableFields:
            if isinstance(value, (str, int, float)):
                value = [str(value)]
            elif hasattr(value, '__iter__'):
                for val in value:
                    assert isinstance(val, str), \
                        f"values must be a string, not {type(val)}"

            super().__setattr__(name, list(value))
        else:
            logging.error(f'Field "{name}" does not exist in profiles')

    def __add__(self, other):
        assert isinstance(other, type(self)), f'only {type(self)}s can be added.'
        out = Profile(root=self._root)
        for key in self.keys():
            setattr(out, key,
                    sorted(list(
                        set(
                            getattr(self, key) + getattr(other, key)
                        ))))
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

    def keep_sessions(self, goodIndex: list):
        """
        This method removes every session other than those with their index in 'goodIndex'
        """

        # Make sure length of different body fields are equal
        L = len(self.Sessions)
        for key in self._tableFields:
            assert L == len(getattr(self, key)),\
                'Profile fields have different lengths.'
        for key in self._tableFields:
            setattr(self, key, [getattr(self, key)[val] for val in goodIndex])
        return self


class EventProfile:
    """
    holds the results of the 'get_event' function
    """
    def __init__(self, profile1: Profile, profile2: Profile):
        self.profile1 = profile1
        self.profile2 = profile2
        self.animalList = []
        self.beforeSessions = []
        self.afterSessions = []

    def __str__(self):
        s = ''
        for i, animal in enumerate(self.animalList):
            s += f"{animal}: {self.beforeSessions[i][-1]} -> {self.afterSessions[i][0]}\n"
        return s

    def append(self, beforeSessionList: list, afterSessionList: list):
        self._find_animal(beforeSessionList, afterSessionList)
        self.beforeSessions.append(beforeSessionList)
        self.afterSessions.append(afterSessionList)

    def _find_animal(self, beforeSessionList: list, afterSessionList: list):
        prefixL = len(self.profile1._prefix)
        beforeAnimals = [session[: prefixL + 3] for session in beforeSessionList]
        afterAnimals = [session[: prefixL + 3] for session in afterSessionList]
        assert len(set(beforeAnimals + afterAnimals)) == 1,\
            'before and after sessions do not belong to the same animal'
        self.animalList.append(afterAnimals[0])

if __name__ == "__main__":
    from Root import Root
    a = Profile(root=Root())
    print(a)
