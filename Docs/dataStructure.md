# Data structure

## Root
Everything starts from the folder in which all the data is located.
This folder is referred to as _root_ and defined as following:
```
import AnimalProfile
root = AnimalProfile.Root(root=" /PathToYourDataFolder")
```
The default _PathToYourDataFolder_ for linux is `'/data'` (for Windows, it is `r'C:\data'`).

## Animals

After initialisation, __AnimalProfile__ will make a json file called `AnimalProfile.setup` in this folder.
Inside _root_, there must be one folder per animal, named following this rule:
> \<prefix>\<XXX> 

for instance, animals could be called Rat123, Rat124, Rat125, ... or MOU234, MOU235, ...
Any other file/folder will be ignored.

## Sessions

Inside each animal directory, there must be one folder called __Experiments__ (capital E, plural).
All the data is to be located within this folder.

Inside the __Experiments__ folder, there must be one folder per experimental session.
The content of these subfolders are irrelevant to _AnimalProfile_ and depend on your setup.
Each session folder must be named following this rule:
> \<prefix>\<XXX>_YYYY_MM_DD_hh_mm

That is, the animal name, followed by the date and time of the experiment.
For example, __Rat123_2020_01_02_14_28__ contains the data acquired from __Rat123__ on January 2nd, 2020, at 14:28.

Overall, the data structure looks like this:
(_AnimalProfile_ creates the `AnimalProfile.setup` and `*.profile` files.)
```
root directory is called 'data'

data
|   AnimalProfile.setup
└───Rat001
|   |   Rat001.profile
|   └───Experiments
|       └───Rat001_2020_01_01_08_00
|           |   …data
|       └───Rat001_2020_01_02_12_01
|           |   …data
|       └───⋮ (other sessions)
└───Rat002
|   |   Rat002.profile
|   └───Experiments
|       └───Rat002_2020_01_11_18_59
|           |   …data
|       └───Rat002_2020_12_01_18_00
|           |   …data
|       └───⋮ (other sessions)
└───Rat003
|   |   Rat003.profile
|   └───Experiments
|       └───⋮ (sessions)
|   ⋮ 
└───RatXXX
|   ⋮
```

Go to [README](../README.md)