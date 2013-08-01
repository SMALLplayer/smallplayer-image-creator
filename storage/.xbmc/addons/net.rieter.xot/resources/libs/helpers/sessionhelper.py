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
import time

from config import Config


class SessionHelper:
    def __init__(self):
        # static only
        raise NotImplementedError()

    @staticmethod
    def CreateSession(logger=None):
        """ Creates a session file in the add-on data folder. This file indicates
        that we passed the channel selection screen. It's main purpose is to be
        able to distinguish between coming back to the channel selection screen
        (in which case a session file was present) or starting the add-on and
        getting to the channel screen. In the latter case we want to show some
        extra data.

        """

        if not SessionHelper.IsSessionActive() and logger:
            logger.Debug("Creating session at '%s'", SessionHelper.__GetSessionPath())
        elif logger:
            logger.Debug("Updating session at '%s'", SessionHelper.__GetSessionPath())
        open(SessionHelper.__GetSessionPath(), 'w').close()

    @staticmethod
    def ClearSession(logger=None):
        """ Clears the active session indicator by deleting the file """

        if os.path.exists(SessionHelper.__GetSessionPath()):
            if logger:
                logger.Warning("Clearing session at '%s'", SessionHelper.__GetSessionPath())
            os.remove(SessionHelper.__GetSessionPath())
        elif logger:
            logger.Debug("No session to clear")

        return

    @staticmethod
    def IsSessionActive(logger=None):
        """ Returns True if an active session file is found """

        if logger:
            logger.Debug("Checking for existing sessions.")

        if not os.path.exists(SessionHelper.__GetSessionPath()):
            if logger:
                logger.Debug("No active sessions found.")
            return False

        timeStamp = os.path.getmtime(SessionHelper.__GetSessionPath())
        nowStamp = time.time()
        if logger:
            logger.Debug("Found active session at '%s' which was modified %.2f minutes (%.2f hours) ago", SessionHelper.__GetSessionPath(), (nowStamp - timeStamp) / 60, (nowStamp - timeStamp) / 3600.0)
        modifiedInLastHours = (nowStamp - 2 * 60 * 60) < timeStamp
        return modifiedInLastHours

    @staticmethod
    def __GetSessionPath():
        """ Returns the session file path """

        return os.path.join(Config.profileDir, "xot.session.lock")
