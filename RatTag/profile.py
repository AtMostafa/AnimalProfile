class Profile:
    """
    this class operates on profile files:
    updating them, and collecting the defined values
    to give a simpler interface to the user
    """

    def __init__(self, *, root):
        self.root = root.root
        self.prefix = root.prefix
        self.headerFields = root.fix
        self.tableFields = root.variable

        self.allAnimals = self.get_all_animals(self)
        

    def get_all_animals(self):
        return sorted(self.root.glob(f'{self.prefix}???/'))

