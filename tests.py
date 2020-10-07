import os, sys
from pathlib import Path
from RatTag.Root import Root
import RatTag.session as session


s = session.get_session_profile(Root(), 'Rat111', 'Rat111_2016_08_01_13_37')
print(s)
