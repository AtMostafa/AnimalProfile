import os, sys
from pathlib import Path
from RatTag.Root import Root
import RatTag.session as session


root = Root(root='/data')
a = session.get_session_profile(root, 'Rat111', 'Rat111_2016_08_01_13_37')

print(a)