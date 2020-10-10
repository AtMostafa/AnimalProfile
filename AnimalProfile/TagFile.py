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

    def write_animal_tag_file(root,animal,until_date='',overwrite=False):
        
        tagFile=os.path.join(root,animal,animal+'.tag')
        
        #compute the valid session list
        sessionList=[os.path.basename(expPath) for expPath in 
                    glob.glob(os.path.join(root,animal,"Experiments",animal+'*'))]
        sessionList=sorted(sessionList)
        try:
            untilDate=datetime.datetime.strptime(until_date,"%Y_%m_%d")
            for idx,session in enumerate(sessionList):
                sessionDate=datetime.datetime.strptime(session,animal+"_%Y_%m_%d_%H_%M")
                if sessionDate > untilDate:
                    sessionList=sessionList[:idx]
                    break
        except:
            pass
        if len(sessionList)<1:
            logging.warning("no session included:"+animal)
            return False
        withBehav=has_behavior(root,animal,sessionList)
        sessionList=[goodSession for idx,goodSession in enumerate(sessionList) if withBehav[idx] is True]
        if len(sessionList)<1:
            logging.warning("no session included:"+animal)
            return False

        #check or write the tag header
        isHeaderReady=update_tag_header(root,animal,sessionList,overwrite)
        if isHeaderReady is False:
            return False

        #Getting the last written session
        lastLine=read_last_line(tagFile,maxLineLength=200)
        sessionName=lastLine.find('%')
        lastWrittenTag=''
        lastWrittenSpeed=''
        if sessionName>=0:
            lastWrittenSession=lastLine[sessionName+1:].split('\t')[0]
            lastWrittenTag    =lastLine[sessionName+1:].split('\t')[1]
            lastWrittenSpeed  =lastLine[sessionName+1:].split('\t')[2]
            idx=sessionList.index(lastWrittenSession)
            if idx+1<len(sessionList):
                sessionList=sessionList[idx+1:]
            elif idx+1==len(sessionList):
                logging.info('No need to update the tag file')
                return False
            else:
                logging.warning("session list inconsistent!")
                return False
        
        
        #data structure:sessions*[tag|speed|type|event]
        data=[]
        #filling the data matrix
        
        for ID,session in enumerate(sessionList):
            sessionInfo=[]
            
            #===============TAG FILE COLUMNS===========================================
            
            #"Session" name
            sessionInfo.append(session)
            
            #"Tag" value
            if sessionName>=0:
                tag=lastWrittenTag
            elif ID==0:
                try:
                    with open(os.path.join(root,animal,'Tag')) as f:
                        tag=f.readline()
                except:
                    tag=input("type the tag for "+animal+" and press ENTER:")
            else:
                tag=data[-1][1]
            sessionInfo.append(tag)
            #----------------------------------------------
            #"Speed" value (MUST be integer or a string):
            spdValues=read_in_file(os.path.join(root,animal,'Experiments',session,session),"computed treadmill speed",valueType=float)
            spdMODE=scipy.stats.mode(spdValues,nan_policy='omit')
            spd=spdMODE.mode[0]
            spdCOUNT=spdMODE.count[0]
            if spdCOUNT<len(spdValues)/2:
                sessionInfo.append('var')
            else:
                sessionInfo.append(str(int(spd)))
            #----------------------------------------------
            #"Type" value:
            sessionInfo.append('Good')
            #----------------------------------------------
            #"Event" value:
            event='-'
            if ID>0:
                if sessionInfo[2] != data[-1][2]:
                    event="SpeedChange"
            elif sessionName>=0 and lastWrittenTag != sessionInfo[1]:
                event='TagChange'
            elif sessionName>=0 and lastWrittenSpeed != sessionInfo[2]:
                event="SpeedChange"
            sessionInfo.append(event)
            #----------------------------------------------
            #"Label" value: (for later manual manipulation)
            sessionInfo.append('NA')
            #----------------------------------------------
            #Add other columns to the tag file below:
            #...
            #...
            #...
            #sessionInfo.append(newColumn)
            #=================TAG FILE END================================================
            data.append(sessionInfo)
        
        #writing the data to the tag file
        isFileWritten=write_session_info(tagFile,data)
        if isFileWritten is False:
            logging.info("couldn not write")
            return False
        logging.info("tag file is written for: "+animal)
        return True


if __name__ == "__main__":
    from Root import Root
    a = TagFile(root=Root(), animal='Rat111')
    print(a)
