#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================

import sys
import os

if __name__ == "__main__":
    # if settings.py is run manually, we should show addon settings.
    if hasattr(sys, "argv") and len(sys.argv) > 1:
        print sys.argv

        # show the requested settings
        addonId = sys.argv[-1]
        callerPath = sys.argv[0]

        # if callerPath is an XBox path, we need to use paths and point to
        # the correct \channels\<scriptname>.channel.<name>\ folder.
        # XBMC4Xbox Log: NOTICE: ['Q:\\scripts\\XOT-Uzg.v3\\resources\\libs\\settings.py', 'net.rieter.xot']
        if (callerPath.lower().startswith("q:")):
            isXbox = True
        else:
            isXbox = False

        if (not isXbox):
            import xbmcaddon
            settings = xbmcaddon.Addon(addonId)
        else:
            import xbmc
            print "Handling Xbox stuff"

            callerPath = callerPath.replace("\\\\", "\\")
            print "CallerPath: %s" % (callerPath,)

            scriptPath = callerPath.replace("\\resources\\libs\\settings.py", "")
            print "ScriptPath: %s" % (scriptPath,)

            scriptName = os.path.split(scriptPath)[-1]
            print "ScriptName: %s" % (scriptName,)

            channelName = addonId[addonId.find(".channel.") + 1:]
            print "ChannelName: %s" % (channelName,)

#            22:25:13 M: 39600128  NOTICE: CallerPath: Q:\scripts\XOT-Uzg.v3\resources\libs\settings.py
#            22:25:13 M: 39600128  NOTICE: ScriptPath: Q:\scripts\XOT-Uzg.v3
#            22:25:13 M: 39600128  NOTICE: ScriptName: XOT-Uzg.v3
            channelPath = os.path.join(scriptPath, "channels", "%s.%s" % (scriptName, channelName))
            settings = xbmc.Settings(path=channelName)

        # now open the settings
        settings.openSettings()
        # perhaps re-open the XOT settings?

    # exit not
    sys.exit(0)
    print "We should not get here."

import re

from logger import Logger
from helpers import database


def CleanupXml(xmlDoc):
    """Cleans up XML to make it look pretty

    Arguments:
    xmlDoc : string - the XML to cleanup

    """

    # cleanup
    prettyXml = xmlDoc.toprettyxml()
    # remove not needed lines with only whitespaces
    prettyXml = re.sub("(?m)^\s+[\n\r]", "", prettyXml,)

    prettyXml = re.sub("[\n\r]+\t+([^<\t]+)[\n\r]+\t+", "\g<1>", prettyXml)
    return prettyXml


def LoadFavorites(channel):
    """Reads the channel favorites into items.

    Arguments:
    channel : Channel - The channel for which the favorites need to be loaded.

    Returns:
    list of MediaItems that were marked as favorites.

    """

    try:
        db = database.DatabaseHandler()
        items = db.LoadFavorites(channel)
        for item in items:
            item.icon = channel.icon
    except:
        Logger.Error("Settings :: Error loading favorites", exc_info=True)

    return items


def AddToFavorites(item, channel):
    """Adds an items to the favorites

    Arguments:
    item    : MediaItem - The MediaItem to add as favorite.
    channel : Channel   - The channel for which the favorites need to be loaded.

    """

    if item.url == "":
        Logger.Warning("Settings :: Cannot add favorite without URL")
        return

    try:
        db = database.DatabaseHandler()
        db.AddFavorite(item.name, item.url, channel)
    except:
        Logger.Error("Settings :: Error adding favorites", exc_info=True)


def RemoveFromFavorites(item, channel):
    """Removes an item from the favorites

    Arguments:
    item    : MediaItem - The MediaItem to be removed
    channel : Channel   - The channel for which it needs to be removed.

    """

    try:
        db = database.DatabaseHandler()
        db.DeleteFavorites(item.name, item.url, channel)
    except:
        Logger.Error("Settings :: Error removing from favorites", exc_info=True)
    return
