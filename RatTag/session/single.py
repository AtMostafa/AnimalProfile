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
    try:
        index = table['Sessions'].index(session)
    except Exception:
        return Profile.Profile(root=root)
    profile = {key: table[key][index] for key in table.keys()}
    
    return Profile.Profile(root=root).from_dict(profile)