__all__ = (,)
from .. import Root
from .. import TagFile
from .. import Profile
from .singleAnimal import *


def batch_get_session_list(root,animalList=None,profile={},until_date=''):
    """
    This function returns list of sessions with certain 'profile' for all the animals
    in animalList. if animalList=[], it will search all the animals
    """
    clearScreen=False
    if animalList is None or animalList=='' or animalList==[]:
        animalPaths=glob.glob(os.path.join(root,'Rat*'))
        animalList=[os.path.basename(animalPaths[i]) for i,_ in enumerate(animalPaths)]
        clearScreen=True
    animalList=sorted(animalList)
    sessionList=[]
    profileDict={}
    for animal in animalList:
        tagPath=os.path.join(root,animal,animal+'.tag')
        sessionProfile=get_session_list(tagFile=tagPath,profile=profile,until_date=until_date)
        for key in sessionProfile:
            if key not in profileDict:
                profileDict[key]=[]
            profileDict[key].extend(sessionProfile[key])
    
    if clearScreen:
        clear_output()
        
    return profileDict