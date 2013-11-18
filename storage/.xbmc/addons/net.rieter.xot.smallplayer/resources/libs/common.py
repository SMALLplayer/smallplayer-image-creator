#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================

import os
import glob
import time

from config import Config
from logger import Logger


def CacheCheck():
    """Checks if the cache folder exists. If it does not exists
    It will be created.

    Returns False it the folder initially did not exist

    """

    # check for cache folder. If not present. Create it!
    if not os.path.exists(Config.cacheDir):
        Logger.Info("Creating cache folder at: %s", Config.cacheDir)
        os.makedirs(Config.cacheDir)
        return False

    return True


def CacheCleanUp(path, cacheTime, mask="*.*"):
    """Cleans up the XOT cache folder.

    Check the cache files create timestamp and compares it with the current datetime extended
    with the amount of seconds as defined in cacheTime.

    Expired items are deleted.

    """

    try:
        Logger.Info("Cleaning up cache in '%s' that is older than %s days", path, cacheTime / 24 / 3600)
        if not os.path.exists(path):
            Logger.Info("Did not cleanup cache: folder does not exist")
            return

        deleteCount = 0
        fileCount = 0

        #for item in os.listdir(path):
        pathMask = os.path.join(path, mask)
        for item in glob.glob(pathMask):
            fileName = os.path.join(path, item)
            if os.path.isfile(fileName):
                Logger.Trace(fileName)
                fileCount = fileCount + 1
                createTime = os.path.getctime(fileName)
                if createTime + cacheTime < time.time():
                    os.remove(fileName)
                    Logger.Debug("Removed file: %s", fileName)
                    deleteCount = deleteCount + 1
        Logger.Info("Removed %s of %s files from cache in: '%s'", deleteCount, fileCount, pathMask)
    except:
        Logger.Critical("Error cleaning the cachefolder: %s", path, exc_info=True)
