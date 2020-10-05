import sys
from pathlib import Path
import json


class Root:
    """
    This class initializes root, and variables if found, otherwise lets the user to set up a new profile system.
    """
    SettingFile = 'RatTag.setup'

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

    def _read_root(self):
        self.settingPath = self.root / self.SettingFile
        if not self.settingPath.is_file():
            self.initialize()
        with open(self.settingPath, 'r') as f:
            self.setting = json.load(f)
        

    def initialize(self):
        """
        No tag system was found in the 'root' so user is asked
        to provide the necessary information to set everything up
        and write to the 'SettingFile'.
        This is tun once and at the beginning
        """
        pass


if __name__ == "__main__":
    a=Root(root='/data')
    print(a.setting)