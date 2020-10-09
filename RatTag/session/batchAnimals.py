__all__ = ('batch_get_session_list',
        'batch_get_animal_list',
        'batch_get_event',
        'batch_get_tag_pattern')

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
        animalList = root.get_all_animals()

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
    animalList0 = [animal for animal in animalList0 if animal not in badAnimals]  # remove bad animals from animalList0
    animalList0.sort()

    eventProfile = Profile.EventProfile(profile1, profile2)
    for animal in animalList0:
        sessionProfile1 = batch_get_session_list(root, animalList=[animal], profile=profile1)
        sessionProfile2 = batch_get_session_list(root, animalList=[animal], profile=profile2)
        sessionTotal = batch_get_session_list(root, animalList=[animal], profile=root.get_profile())
        try:
            index = sessionTotal.Sessions.index(sessionProfile1.Sessions[-1])
            if sessionProfile2.Sessions[0] == sessionTotal.Sessions[index + 1]:
                # Two profiles succeed, meaning the Event happended.
                eventProfile.append(sessionProfile1.Sessions, sessionProfile2.Sessions)
        except Exception:
            pass
    return eventProfile


def batch_get_tag_pattern(root: Root.Root,
                           animalList: list = None,
                           tagPattern='*'):
    """
    applies 'get_pattern_session_list' to a list of animals
    """
    if animalList is None:
        animalList = root.get_all_animals()

    profileDict = root.get_profile()
    for animal in animalList:
        tagFile = TagFile.TagFile(root, animal)
        profileDict += tagFile.get_pattern_session_list(tagPattern=tagPattern)
    return profileDict
