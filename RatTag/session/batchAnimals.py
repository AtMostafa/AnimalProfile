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
    return animalList
