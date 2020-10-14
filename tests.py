import os
import sys
from pathlib import Path
import AnimalProfile
import AnimalProfile.session as session


root = AnimalProfile.Root()
profile1 = root.get_profile()
profile1.Speed = '10'
profile1.Type = 'Good'
profile2 = root.get_profile()
profile2.Speed = '15'
profile2.Type = 'Good'
# profile.Event = 'SpeedChange'
# profile.rewardType = 'Progressive'
# tagfile = AnimalProfile.File(root, 'Rat112')
s = session.get_session_list(root, ['Rat111', 'Rat112'], profile1)
# s = session.batch_get_tag_pattern(root,)
# s = session.batch_get_event(root, profile1, profile2)
# s = tagfile.read_body()
# s.keep_sessions([2, 3])
# s = tagfile.write()
# s = session.get_current_animals(root, 20000)
print(s)
