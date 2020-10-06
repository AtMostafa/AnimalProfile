import os
import logging
import pandas as pd


class TagFile:
    """
    This class represents a tag file and functions to deal with it
    """

    def __init__(self, root, animal,):
        self.root = root
        self.animal = animal
        self.path = self.root.root / animal / animal+'.profile'

    def _read_last_line(self, maxLineLength=200):
        """
        This function returns the last line of a text file
        maxLineLength: maximum assumable line length in BYTES
        """
        try:
            with open(self.path, 'rb') as f:
                fileSize = os.fstat(f.fileno()).st_size
                if maxLineLength > fileSize:
                    maxLineLength = fileSize-1
                f.seek(-abs(maxLineLength)-1, os.SEEK_END)
                lines = f.readlines()
        except Exception as e:
            logging.warning('couldn\'t open file:' + self.path)
            logging.info(repr(e))
            return False
        return lines[-1].decode()
    
    def _read_tag_header(self):
        out = dict()
        try:
            with open(self.path, 'r') as f:
                for line in f:
                    if line[0] == '#':
                        items = line.split(':')
                        out[items[0][1:]]=items[1][:-1]
                    else:
                        break
        except Exception:
            return False
        
        return out

    def _is_tag_valid(self,):
        if not self.path.is_file():
            return False    # tag not available
        header = self._read_tag_header(self.path)
        if isinstance(header, bool):
            return False    # tag header not correct
        if header['name'] != self.animal:
            return False     # tag animal name not correct
        return True

    def read_tag_table(self, headerSize=None):
        """
        This function return the whole table of sessions
        in a tag file as a dictionary
        """
        if headerSize is None:
            headerSize = len(self.root.fix)+2 # +2 for header and name fields
        try:
            table = pd.read_csv(self.path, 
                                delim_whitespace=True,
                                skiprows=headerSize)
        except Exception as e:
            logging.warning(repr(e))
            return {'Sessions':[],'Tag':'','Speed':'','Type':'','Event':'','Label':''}
        table.replace(to_replace= {'Sessions': {'%': ''}},regex=True,inplace=True)
        out = {label: list(column) for label, column in zip(table.columns.values, table.values.T)}
        return out
