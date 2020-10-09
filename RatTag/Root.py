import sys
from pathlib import Path
import json
from .Profile import Profile


class Root:
    """
    This class initializes root, and variables if found,
    otherwise lets the user to set up a new profile system.
    """
    SETTING_FILE = 'RatTag.setup'

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
        return f'RatTag profile at: {self.settingPath}'

    def _read_root(self):
        self.settingPath = self.root / self.SETTING_FILE
        if not self.settingPath.is_file():
            self.initialize()
        with open(self.settingPath, 'r') as f:
            setting = json.load(f)
        self.__dict__.update(setting)
        self.body.insert(0,'Sessions')
        self.body.insert(1,'Tag')

    def initialize(self):
        """
        No tag system was found in the 'root' so user is asked
        to provide the necessary information to set everything up
        and write to the 'SETTING_FILE'.
        This is tun once and at the beginning
        """
        raise NotImplementedError('To be added soon')

    def get_profile(self):
        """
        return a profile object for this root
        """
        return Profile(root=self)

    def get_all_animals(self):
        animalPaths = sorted(self.root.glob(f'{self.prefix}???/'))
        animalList = [animal.name for animal in animalPaths]
        return sorted(animalList)



if __name__ == "__main__":
    a = Root(root='/data')
    print(a)
