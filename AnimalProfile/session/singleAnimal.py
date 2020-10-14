__all__ = ('get_session_profile',)
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
