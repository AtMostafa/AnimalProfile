import sys
from pathlib import Path
import json
import logging
from .Profile import Profile
from .File import File


class Root:
    """
    This class initializes root, and variables if found,
    otherwise lets the user to set up a new profile system.
    """
    SETTING_FILE = 'AnimalProfile.setup'

    def __init__(self, *, root: str = None,):
        self.root = root
        if self.root is None:
            if sys.platform.startswith('linux'):
                self.root = Path('/data')
            elif sys.platform.startswith('win'):
                self.root = Path('c:/data')
            else:
                self.root = Path('/data')
        elif isinstance(self.root, str):
            self.root = Path(self.root)
        else:
            assert ("root' must be an string, or None")

        self._read_root()

    def __str__(self):
        return f'AnimalProfile profile at: {self.settingPath}'

    def __repr__(self):
        return self.__str__()

    def _read_root(self):
        self.settingPath = self.root / self.SETTING_FILE
        if not self.settingPath.is_file():
            self._set_up()
        with open(self.settingPath, 'r') as f:
            setting = json.load(f)
        self.__dict__.update(setting)
        self.body.insert(0, 'Sessions')
        self.body.insert(1, 'Tag')

    def _set_up(self):
        """
        No tag system was found in the 'root' so user is asked
        to provide the necessary information to set everything up
        and write to the 'SETTING_FILE'.
        This is done once and at the beginning
        """
        prefix = input("""What is the descriptive prefix of the data structure?\n
        E.g., Rat in Rat123, Rat124, etc.\n
        Follow python variable naming rules in all the parameters: """)
        prefix = prefix.split(maxsplit=2)[0]

        print('Header: parameters defined once for each animal, e.g., name (added automatically).')
        Nheader = int(input('\nNumber of header parameters (int):'))
        header = []
        for i in range(Nheader):
            h = input(f'name of header param #{i+1}:')
            header.append(h.split(maxsplit=2)[0])

        print("""Body: parameters defined per session for each animal.
        "Session":session name, and "Tag":experiment tag are added automatically.""")
        Nbody = int(input('\nNumber of body parameters (int):'))
        body = []
        for i in range(Nbody):
            b = input(f'name of body param #{i+1}:')
            body.append(b.split(maxsplit=2)[0])

        out = {'prefix': prefix, 'header': header, 'body': body}
        with open(self.settingPath, 'w') as f:
            json.dump(out, f, indent=4, sort_keys=True)
        logging.info(f'Written: {self.settingPath}')

    def get_profile(self):
        """
        return a profile object for this root
        """
        return Profile(root=self)

    def get_all_animals(self):
        animalPaths = sorted(self.root.glob(f'{self.prefix}???/'))
        animalList = [animal.name for animal in animalPaths]
        return sorted(animalList)

    def update(self, animal: str):
        """
        updates the profile file of the animal using File.write()
        """
        tagFile = File(self, animal)
        isWritten = tagFile.write()
        if isWritten:
            logging.info(f'Profile file updated for {animal}')
        else:
            logging.info(f'{animal} profile did not update.')

        return isWritten


if __name__ == "__main__":
    a = Root(root='/data')
    print(a)
