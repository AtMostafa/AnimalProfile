import os, sys
from pathlib import Path
from RatTag.Root import Root
import RatTag.session as session
import RatTag.TagFile as TagFile
import RatTag.Profile as Profile


root = Root()
profile = Profile.Profile(root=root)
profile.Speed = '15.0'
profile.Event = 'SpeedChange'
tagfile = TagFile.TagFile(root, 'Rat111')
s = session.get_session_list(tagfile, profile)
# s = tagfile.read_tag_table()
print(s)
