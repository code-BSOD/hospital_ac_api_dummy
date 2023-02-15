tempgetset_get = """
Parameter Name: req. REQUIRED = Yes
User need to input an integer value ranging from 1 to 5

---> Arguments and their Tasks <---

1. req = 1: Get the current Temp in C and F
2. req = 2: Get the currently set Target Temp in C and F
3. req = 3: Get the current humidity in percentage
4. req = 4: Get the currently set Target humidity
5. req = 5: Listing all currently existing presets
"""


tempgetset_post = """
We have 4 parameters. req, targettemp, targethum, presetname
Parameter: req. REQUIRED = YES

---> Arguments and their Tasks <---
* req = 1: Set the Target Temp
Required Parameters: req, targettemp
* req = 2: Set the target humidity to specific level
Required parameters: req, targethum
* req = 3: Select and activate a preset
Required parameters: req, presetname
* req = 4: Create a new preset
Required parameters: req, presetname, targettemp, targethum

"""


presetdel_delete = """
Parameter: name. REQUIRED = YES

* We need to suppy a preset name in order to delete it from the preset list.
"""
