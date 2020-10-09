import os, sys
from pathlib import Path
from RatTag.Root import Root
import RatTag.session as session
import RatTag.TagFile as TagFile
import RatTag.Profile as Profile


root = Root()
profile1 = root.get_profile()
profile1.Speed = '10'
profile1.Type = 'Good'
profile2 = root.get_profile()
profile2.Speed = '15'
profile2.Type = 'Good'
# profile.Event = 'SpeedChange'
# profile.rewardType = 'Progressive'
tagfile = TagFile.TagFile(root, 'Rat111')
# s = session.batch_get_session_list(root, ['Rat111', 'Rat112'], profile1)
s = session.batch_get_tag_pattern(root,)
# s = tagfile.read_tag_table()
# s.keep_sessions([2, 3])
print(s)
