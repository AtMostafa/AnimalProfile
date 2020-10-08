import os, sys
from pathlib import Path
from RatTag.Root import Root
import RatTag.session as session
import RatTag.TagFile as TagFile
import RatTag.Profile as Profile


root = Root()
profile = root.get_profile()
profile.Speed = '150'
# profile.Event = 'SpeedChange'
profile.rewardType = 'Progressive'
tagfile = TagFile.TagFile(root, 'Rat111')
s = session.batch_get_session_list(root, ['Rat111', 'Rat112'], profile)
# s = tagfile.read_tag_table()
print(s)

