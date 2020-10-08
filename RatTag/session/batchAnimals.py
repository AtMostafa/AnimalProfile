__all__ = ('batch_get_session_list', 'batch_get_animal_list')
from .. import Root
from .. import TagFile
from .. import Profile
from .singleAnimal import *


def batch_get_session_list(root: Root.Root,
                        animalList: list = None,
                        profile: Profile.Profile = None):
    """
    This function returns list of sessions with certain 'profile' for all the animals
    in animalList. if animalList=Nonr, it will search all the animals.
    """
    if profile is None:
        profile = Profile.Profile(root=root)

    if animalList is None or animalList == '' or animalList == []:
        animalPaths = sorted(root.root.glob(f'{profile._prefix}???/'))
        animalList = [animal.name for animal in animalPaths]

    profileOut = Profile.Profile(root=root)
    for animal in animalList:
        tagFile = TagFile.TagFile(root, animal)
        sessionProfile = get_session_list(tagFile, profile)
        profileOut += sessionProfile
    return profileOut


def batch_get_animal_list(root: Root.Root, profile: Profile.Profile = None):
    """
    this function returns list of animals with at least one session matching the "profile"
    """
    if profile is None:
        profile = Profile.Profile(root=root)

    allProfiles = batch_get_session_list(root, animalList=None, profile=profile)
    sessionList = allProfiles.Sessions

    animalList = []
    for session in sessionList:
        animalList.append(session[:len(profile._prefix) + 3])
    animalList = list(set(animalList))
    return sorted(animalList)


def batch_get_event(root: Root.Root,
                    profile1: Profile.Profile,
                    profile2: Profile.Profile,
                    badAnimals: list = None):
    """
    This function finds the animals that match both profile1 and profile2 IN SUCCESSION
    I.E., when the conditions changed
    """
    if badAnimals is None:
        badAnimals = []
    animalList1 = batch_get_animal_list(root, profile1)
    animalList2 = batch_get_animal_list(root, profile2)
    animalList0 = set(animalList1).intersection(set(animalList2))
    animalList0 = [animal for animal in animalList0 if animal not in badAnimals]  #remove bad animals from animalList0
    sessionDic = {key: [[],[]] for key in animalList0}
    animalList = []
    for animal in animalList0:
        sessionListProfile1 = batch_get_session_list(root, animalList=[animal], profile=profile1, until_date='')
        sessionListProfile2 = batch_get_session_list(root, animalList=[animal], profile=profile2, until_date='')
        sessionListTotal = batch_get_session_list(root, animalList=[animal], profile={'Type': 'Good'}, until_date='')
        try:
            index = sessionListTotal['Sessions'].index(sessionListProfile1['Sessions'][-1])
            if sessionListProfile2['Sessions'][0] == sessionListTotal['Sessions'][index + 1]:
                animalList.append(animal)
                sessionDic[animal][0] = sessionListProfile1['Sessions']
                sessionDic[animal][1] = sessionListProfile2['Sessions']
        except Exception as e:
            logging.warning(repr(e))
    return animalList, sessionDic
