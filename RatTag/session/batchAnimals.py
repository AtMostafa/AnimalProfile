__all__ = ('batch_get_session_list',)
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
        animalPaths = sorted(root.glob(f'{self._prefix}???/'))
        animalList = [k.name for animal in animalPaths]

    profileOut = Profile.Profile(root=root)
    for animal in animalList:
        tagFile = TagFile.TagFile(root, animal)
        sessionProfile = get_session_list(tagFile, profile)
        profileOut += sessionProfile
    return profileOut
