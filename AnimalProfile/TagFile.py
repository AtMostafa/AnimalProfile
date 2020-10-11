import os
import logging
import pandas as pd
import fnmatch
from .Profile import Profile


class TagFile:
    """
    This class represents a tag file and functions to deal with it
    """

    def __init__(self, root, animal: str,):
        self.root = root
        self.animal = animal
        self.path = self.root.root / animal / animal
        self.path = self.path.with_suffix('.profile')

    def _read_last_line(self, maxLineLength=200):
        """
        This function returns the last line of a text file
        maxLineLength: maximum assumable line length in BYTES
        """
        try:
            with open(self.path, 'rb') as f:
                fileSize = os.fstat(f.fileno()).st_size
                if maxLineLength > fileSize:
                    maxLineLength = fileSize - 1
                f.seek(-abs(maxLineLength)-1, os.SEEK_END)
                lines = f.readlines()
        except Exception as e:
            logging.warning('couldn\'t open file:' + self.path)
            logging.info(repr(e))
            return False
        return lines[-1].decode()

    def _is_tag_valid(self,):
        if not self.path.is_file():
            return False    # tag not available
        header = self._read_tag_header(self.path)
        if isinstance(header, bool):
            return False    # tag header not correct
        if header['name'] != self.animal:
            return False     # tag animal name not correct
        return True
    
    def read_tag_header(self):
        out = dict()
        try:
            with open(self.path, 'r') as f:
                for line in f:
                    if line[0] == '#':
                        items = line.split(':')
                        out[items[0][1:]] = items[1][:-1]
                    else:
                        break
        except Exception:
            return None
        return out

    def read_tag_table(self, headerSize=None):
        """
        This function return the whole table of sessions
        in a tag file as a dictionary
        """
        if headerSize is None:
            headerSize = len(self.root.header) + 2  # +2 for header and name fields
        try:
            table = pd.read_csv(self.path,
                                delim_whitespace=True,
                                skiprows=headerSize,
                                dtype=str)
        except Exception as e:
            logging.warning(repr(e))
            return Profile(root=self.root)
        table.replace(to_replace={'Sessions': {'%': ''}}, regex=True, inplace=True)
        out = {label: list(column) for label, column in zip(table.columns.values, table.values.T)}
        return Profile(root=self.root).from_dict(out)

    def get_pattern_session_list(self, tagPattern='*'):
        """
        This function returns the list of the sessions with the 'Tag'
        field conforming to the pattern in 'tagPattern'.
        Usual shell-style Wildcards are accepted
        (defined in the 'fnmatch' module of python standard library).
        """
        table = self.read_tag_table()
        goodSessions = fnmatch.filter(table.Tag, tagPattern)
        goodIndex = [x for x, s in enumerate(table.Tag) if s in goodSessions]
        table = table.keep_sessions(goodIndex)
        return table

    def get_sesisonList(self):
        """
        returns the list of folders inside Experiments folder,
        They must follow the pattern:
        <prefix><XXX>_YYYY_MM_DD_HH_MM
        """
        expPath = self.path.parent / 'Experiments'
        sessionList = [path.name for path in expPath.glob(f'{self.animal}_20??_??_??_??_??')]
        sessionList = sorted(sessionList)
        return sessionList

    def _write_tag_header(self, profile: Profile):
        content = f"""#info:\n#name:{self.animal}"""

        for key in self.root.header:
            val = getattr(profile, key)
            content += f'\n#{key}:{val}'

        for key in self.root.body:
            content += f'{key}\t'
        content = content[:-1]  # remove the trailing \t
        content += '\n'

        try:
            with open(self.path, 'w') as f:
                f.write(content)
        except Exception:
            return False
        return True

    def _update_tag_header(self, overwrite):
        if not self.is_tag_valid() or overwrite:
            # Ask user for header fields
            profile = self.root.get_profile()
            for header in profile._headerFields:
                h = input(f'{header}: ')
                setattr(profile, header, h)

            isHeaderWritten = self._write_tag_header(profile)
            if not isHeaderWritten:
                logging.error('failed to write the tag header')
                return False
        return True

    def _write_session_info(self, profile: Profile):
        fixedText = ''
        for key in profile._tableFields:
            if key == 'Sessions':
                continue
            fixedText += f'{getattr(profile, key)}\t'
        fixedText = fixedText[:-1]  # remove trailing \t
        try:
            with open(self.path, 'a') as f:
                for session in profile.Sessions:
                    f.write('%' + session + '\t' + fixedText + '\n')
        except Exception:
            return False
        return True

    def write_profile_file(self, overwrite=False):
        """
        This method writes (overwrites) the profile for the animal
        by reading the sessions in the 'Experiments' folder and
        adding them to the profile.
        """

        # compute the valid session list
        sessionList = self.get_sesisonList()

        if len(sessionList) < 1:
            logging.error("no session found for:" + self.animal)
            return False

        # check or write the tag header
        isHeaderReady = self._update_tag_header(sessionList, overwrite)
        if isHeaderReady is False:
            return False

        # Getting the last written session
        lastLine = self._read_last_line(maxLineLength=200)
        sessionName = lastLine.find('%')
        profileLastSession = self.root.get_profile()
        if sessionName >= 0:
            for i, key in enumerate(profileLastSession._tableFields):
                setattr(profileLastSession, key, lastLine[sessionName + 1:].split('\t')[i])

            idx = sessionList.index(profileLastSession.Sessions[-1])
            if idx + 1 < len(sessionList):
                sessionList = sessionList[idx + 1:]
            elif idx + 1 == len(sessionList):
                logging.info('No need to update the tag file')
                return False
            else:
                logging.warning("session list inconsistent!")
                return False
        else:
            for key in profileLastSession._tableFields:
                setattr(profileLastSession, key, '{key}_Temp')

        profileLastSession.Sessions = sessionList

        # writing the data to the tag file
        isFileWritten = self._write_session_info(profileLastSession)
        if isFileWritten is False:
            logging.error("couldn not write")
            return False
        logging.info("tag file is written for: " + self.animal)
        return True


if __name__ == "__main__":
    from Root import Root
    a = TagFile(root=Root(), animal='Rat111')
    print(a)
