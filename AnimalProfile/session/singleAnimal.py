__all__ = ('get_session_profile','get_session_list',)
from .. import Root
from .. import File
from .. import Profile


def get_session_profile(root: Root, animal: str, session: str):
    """
    get the profile of a single session
    """

    tagFile = File(root, animal)
    table = tagFile.read_body()
    header = tagFile.read_header()
    try:
        index = table.Sessions.index(session)
    except Exception:
        return Profile(root=root)
    profile = {key: getattr(table, key)[index] for key in table._tableFields}
    profile.update({key: header[key] for key in table._headerFields})

    return Profile(root=root).from_dict(profile)


def get_session_list(tagFile: File, profile: Profile = None):
    """
    This function returns the list of the sessions within a profile file
    meeting all the conditions in 'profile', 
    EX: profile={'Speed':['10','20'],'rewardType':'Progressive,'Tag':'Early-DLS_Lesion','Type':'Good'}
    """
    table = tagFile.read_body()
    if table.Sessions == []:
        return Profile(root=tagFile.root)
    if profile is None:
        profile = Profile(root=tagFile.root)

    # Reject bad header
    header = tagFile.read_header()
    for key in profile._headerFields:
        if str(header[key]) not in getattr(profile, key) and len(getattr(profile, key)) >= 1:
            return Profile(root=tagFile.root)

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
    return Profile(root=tagFile.root).from_dict(goodSessionsProfile)
