import os
import logging
import pandas as pd
import fnmatch
import datetime
from .Profile import Profile


class File:
    """
    This class represents a tag file and functions to deal with it
    """

    def __init__(self, root: 'Root', animal: str,):
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
                f.seek(-abs(maxLineLength) - 1, os.SEEK_END)
                lines = f.readlines()
        except Exception as e:
            logging.warning('couldn\'t open file:' + self.path)
            logging.info(repr(e))
            return False
        return lines[-1].decode()

    def _is_profile_valid(self,):
        if not self.path.is_file():
            return False    # tag not available
        header = self.read_header()
        if isinstance(header, bool):
            return False    # tag header not correct
        if header['name'] != self.animal:
            return False     # tag animal name not correct
        return True
    
    def read_header(self):
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
            return False
        return out

    def read_body(self, headerSize=None):
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

    def _write_header(self, profile: Profile):
        content = f"""#info:\n#name:{self.animal}"""

        for key in self.root.header:
            val = getattr(profile, key)[0]
            content += f'\n#{key}:{val}'
        content += '\n'

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

    def _update_header(self, overwrite):
        if not self._is_profile_valid() or overwrite:
            # Ask user for header fields
            profile = self.root.get_profile()
            for header in profile._headerFields:
                h = input(f'{header}: ')
                setattr(profile, header, h)

            isHeaderWritten = self._write_header(profile)
            if not isHeaderWritten:
                logging.error('failed to write the tag header')
                return False
        return True

    def _write_session_info(self, profile: Profile):
        fixedText = '\t'.join([f'{getattr(profile, key)[0]}'
                               for key in profile._tableFields if key != 'Sessions'])
        try:
            with open(self.path, 'a') as f:
                for session in profile.Sessions:
                    f.write(f'%{session}\t{fixedText}\n')
        except Exception:
            return False
        return True

    def write(self, overwrite=False):
        """
        This method writes, overwrites, or appends the profile for the animal
        by reading the sessions in the 'Experiments' folder and
        adding them to the profile.
        """
        # compute the valid session list
        sessionList = self.get_all_sessions()

        if len(sessionList) < 1:
            logging.error("no session found for:" + self.animal)
            return False

        # check or write the tag header
        isHeaderReady = self._update_header(overwrite)
        if isHeaderReady is False:
            logging.error('error in writting the header')
            return False

        # Getting the last written session
        lastLine = self._read_last_line(maxLineLength=200).strip('\n')
        sessionName = lastLine.find('%')
        profileLastSession = self.root.get_profile()
        if sessionName >= 0:
            for i, key in enumerate(profileLastSession._tableFields):
                setattr(profileLastSession, key, lastLine[sessionName + 1:].split('\t')[i])

            lastSessionDate = self.get_session_date(profileLastSession.Sessions[-1])
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
                setattr(profileLastSession, key, f'{key}_Temp')

        profileLastSession.Sessions = sessionList

        # writing the data to the tag file
        isFileWritten = self._write_session_info(profileLastSession)
        if isFileWritten is False:
            logging.error("could not write")
            return False
        logging.info("profile file is written for: " + self.animal)
        return True

    def get_pattern_session_list(self, tagPattern='*'):
        """
        This function returns the list of the sessions with the 'Tag'
        field conforming to the pattern in 'tagPattern'.
        Usual shell-style Wildcards are accepted
        (defined in the 'fnmatch' module of python standard library).
        """
        table = self.read_body()
        goodSessions = fnmatch.filter(table.Tag, tagPattern)
        goodIndex = [x for x, s in enumerate(table.Tag) if s in goodSessions]
        table = table.keep_sessions(goodIndex)
        return table

    def get_all_sessions(self):
        """
        returns the list of folders inside Experiments folder,
        They must follow the pattern:
        <prefix><XXX>_YYYY_MM_DD_HH_MM
        """
        expPath = self.path.parent / 'Experiments'
        sessionList = [path.name for path in expPath.glob(f'{self.animal}_20??_??_??_??_??')]
        sessionList = sorted(sessionList)
        return sessionList

    def get_profile_session_list(self, profile: Profile = None):
        """
        This function returns the list of the sessions within a profile file
        meeting all the conditions in 'profile', 
        """
        table = self.read_body()
        if table.Sessions == []:
            return Profile(root=self.root)
        if profile is None:
            profile = Profile(root=self.root)

        # Reject bad header
        header = self.read_header()
        for key in profile._headerFields:
            if str(header[key]) not in getattr(profile, key) and len(getattr(profile, key)) >= 1:
                return Profile(root=self.root)

        goodSessions = []
        for index, session in enumerate(sorted(table.Sessions)):
            try:
                for key in table._tableFields:
                    check = False
                    if str(getattr(table, key)[index]) in getattr(profile, key) \
                            or len(getattr(profile, key)) == 0:
                        check = True
                    if not check:
                        raise NameError
                goodSessions.append(session)
            except Exception:
                continue

        goodIndex = [x for x, s in enumerate(table.Sessions) if s in goodSessions]
        goodSessionsProfile = {key: [str(getattr(table, key)[idx]) for idx in goodIndex] for key in table._tableFields}
        goodSessionsProfile.update({key: header[key] for key in table._headerFields})

        return Profile(root=self.root).from_dict(goodSessionsProfile)

    def get_session_date(self, session: str):
        sessionDate = datetime.datetime.strptime(session, f"{self.animal}_%Y_%m_%d_%H_%M")
        return sessionDate


if __name__ == "__main__":
    from Root import Root
    a = File(root=Root(), animal='Rat111')
    print(a)
