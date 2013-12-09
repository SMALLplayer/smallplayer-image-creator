# coding:UTF-8
import sys
import os
import re

import xbmcgui

print "============================================================="
print sys.argv
print __file__

addonPath = sys.argv[1]

addonInfo = os.path.realpath(os.path.join(addonPath, "addon.xml"))
addonHandle = file(addonInfo)
addonXml = addonHandle.read()
addonHandle.close()

inputDialog = xbmcgui.Dialog()
names = ["XOT-Uzg.v3", "Gemist", "Gemist op TV", "Uitzending Gemist.v3", "Uitzendinggemist.v3", "XBMC Online TV"]
nameIndex = inputDialog.select("Select preferred add-on display name", names)
if nameIndex >= 0:
    newXml = re.sub('name="([^"]+)"', 'name="%s"' % (names[nameIndex], ), addonXml, 1)

    addonHandle = open(addonInfo, "w+")
    addonHandle.write(newXml)
    addonHandle.close()

print "============================================================="
