__all__ = ('get_session_profile',)
from .. import Root
from .. import TagFile
from .. import Profile


def get_session_profile(root: Root.Root, animal: str, session: str):
    """
    get the profile of a single session
    """

    tagFile = TagFile.TagFile(root, animal)
    table = tagFile.read_tag_table()
    header = tagFile.read_tag_header()
    try:
        index = table.Sessions.index(session)
    except Exception:
        return Profile.Profile(root=root)
    profile = {key: getattr(table, key)[index] for key in table._tableFields}
    profile.update({key: header[key] for key in table._headerFields})

    return Profile.Profile(root=root).from_dict(profile)