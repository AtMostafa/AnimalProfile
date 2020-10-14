__all__ = ('get_session_list',
           'get_animal_list',
           'get_event',
           'get_tag_pattern',
           'get_pattern_animalList',
           'get_current_animals')

import datetime
import logging
from .. import Root
from .. import File
from .. import Profile
from ..Profile import EventProfile
from .singleAnimal import *


def get_session_list(root: Root,
                     animalList: list = None,
                     profile: Profile = None):
    """
    This function returns list of sessions with certain 'profile' for all the animals
    in animalList. if animalList=Nonr, it will search all the animals.
    """
    if profile is None:
        profile = Profile(root=root)

    if animalList is None or animalList == '' or animalList == []:
        animalList = root.get_all_animals()

    profileOut = Profile(root=root)
    for animal in animalList:
        tagFile = File(root, animal)
        sessionProfile = tagFile.get_profile_session_list(profile)
        profileOut += sessionProfile
    return profileOut


def get_animal_list(root: Root, profile: Profile = None):
    """
    this function returns list of animals with at least one session matching the "profile"
    """
    if profile is None:
        profile = Profile(root=root)

    allProfiles = get_session_list(root, animalList=None, profile=profile)
    sessionList = allProfiles.Sessions

    animalList = []
    for session in sessionList:
        animalList.append(session[:len(profile._prefix) + 3])
    animalList = list(set(animalList))
    return sorted(animalList)


def get_event(root: Root,
              profile1: Profile,
              profile2: Profile,
              badAnimals: list = None):
    """
    This function finds the animals that match both profile1 and profile2 IN SUCCESSION
    I.E., when the conditions changed
    """
    if badAnimals is None:
        badAnimals = []
    animalList1 = get_animal_list(root, profile1)
    animalList2 = get_animal_list(root, profile2)
    animalList0 = set(animalList1).intersection(set(animalList2))
    animalList0 = [animal for animal in animalList0 if animal not in badAnimals]  # remove bad animals from animalList0
    animalList0.sort()

    eventProfile = EventProfile(profile1, profile2)
    for animal in animalList0:
        sessionProfile1 = get_session_list(root, animalList=[animal], profile=profile1)
        sessionProfile2 = get_session_list(root, animalList=[animal], profile=profile2)
        sessionTotal = get_session_list(root, animalList=[animal], profile=root.get_profile())
        try:
            index = sessionTotal.Sessions.index(sessionProfile1.Sessions[-1])
            if sessionProfile2.Sessions[0] == sessionTotal.Sessions[index + 1]:
                # Two profiles succeed, meaning the Event happended.
                eventProfile.append(sessionProfile1.Sessions, sessionProfile2.Sessions)
        except Exception:
            pass
    return eventProfile


def get_tag_pattern(root: Root,
                    animalList: list = None,
                    tagPattern: str = '*'):
    """
    applies 'get_pattern_session_list' to a list of animals
    """
    if animalList is None or animalList == []:
        animalList = root.get_all_animals()

    profileDict = root.get_profile()
    for animal in animalList:
        tagFile = File(root, animal)
        profileDict += tagFile.get_pattern_session_list(tagPattern=tagPattern)
    return profileDict


def get_pattern_animalList(root: Root, tagPattern: str):
    """
    this function returns list of animals with at least one session matching the 'tagPattern'
    """
    allProfile = get_tag_pattern(root, animalList=None, tagPattern=tagPattern)
    sessionList = allProfile.Sessions

    animalList = []
    for session in sessionList:
        animalList.append(session[:len(root.prefix) + 3])
    animalList = list(set(animalList))
    return sorted(animalList)


def get_current_animals(root: Root, days_passed: int = 4):
    """
    this function returns the list of animals with a new session
    within the last few ('days_passed') days
    """
    now = datetime.datetime.now()
    all_animals = root.get_all_animals()
    if all_animals == []:
        logging.warning('No animal found!')
        return []

    animalList = []
    for animal in all_animals:
        animalTag = File(root, animal)
        sessionList = animalTag.get_all_sessions()
        if not sessionList:
            continue

        lastSessionDate = animalTag.get_session_date(sessionList[-1])
        if (now - lastSessionDate).days <= days_passed:
            animalList.append(animal)

    return animalList
