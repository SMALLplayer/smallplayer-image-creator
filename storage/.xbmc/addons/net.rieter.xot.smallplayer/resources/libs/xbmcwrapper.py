#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================
import time
import os

#===============================================================================
# Import the default modules
#===============================================================================
import xbmcgui
import xbmc

from config import Config

class XbmcWrapper:
    """ Wraps some basic XBMC methods """

    Error = "error"
    Warning = "warning"
    Info = "info"

    @staticmethod
    def ShowNotification(title, lines, notificationType=Info, displayTime=1500, fallback=True, logger=None):
        """ Shows an XBMC Notification

        Arguments:
        titel   : String - The title to show
        content : String - The content to show

        Keyword Arguments:
        notificationType  : String - The type of notification: info, error, warning
        displayTime       : int    - Time to display the notification. Defaults to 1500 ms.
        fallback          : bool   - Should we fallback on XbmcWrapper.ShowDialog on error?

        """

        # check for a title
        if title:
            notificationTitle = "%s - %s" % (Config.appName, title)
        else:
            notificationTitle = Config.appName

        # check for content and merge multiple lines. This is to stay compatible
        # with the LanguageHelper.GetLocalizedString that returns strings as arrays
        # if they are multiple lines (this is because XbmcWrapper.ShowDialog needs
        # this for multi-line dialog boxes.
        if not lines:
            notificationContent = ""
        else:
            if isinstance(lines, (tuple, list)):
                notificationContent = " ".join(lines)
            else:
                notificationContent = lines

        # determine the duration
        notificationType = notificationType.lower()
        if notificationType == XbmcWrapper.Warning and displayTime < 2500:
            displayTime = 2500
        elif notificationType == XbmcWrapper.Info and displayTime < 5000:
            displayTime = 5000
        elif displayTime < 1500:
            # cannot be smaller then 1500 (API limit)
            displayTime = 1500

        # Get an icon
        notificationIcon = os.path.join(Config.rootDir, "icon.png")
        if os.path.exists(notificationIcon):
            # change the separators
            notificationIcon = notificationIcon.replace("\\", "/")
        else:
            notificationIcon = notificationType

        if logger:
            logger.Debug("Showing notification: %s - %s", notificationTitle, notificationContent)

        command = '{"id": 1,"jsonrpc":"2.0","method":"GUI.ShowNotification","params":{"title":"%s","message":"%s", "image":"%s", "displaytime": %s}}' % (notificationTitle, notificationContent, notificationIcon, displayTime)
        try:
            if logger:
                logger.Trace("Sending command: %s", command)
            response = xbmc.executeJSONRPC(command)
            return response
        except:
            if fallback:
                XbmcWrapper.ShowDialog(title or "", lines or "")
            # no reason to worry if this does not work on older XBMC's
            return False

    @staticmethod
    def ShowDialog(title, lines):
        """ Shows a dialog box with title and text

        Arguments:
        title : string       - the title of the box
        text  : List[string] - the lines to display

        """

        # let's just unlock the interface, in case it's locked.
        xbmc.executebuiltin("Dialog.Close(busydialog)")

        msgBox = xbmcgui.Dialog()
        if (title == ""):
            header = Config.appName
        else:
            header = "%s - %s" % (Config.appName, title)

        if len(lines) == 0:
            ok = msgBox.ok(header, "")
        elif isinstance(lines, basestring):
            # it was just a string, no list or tuple
            ok = msgBox.ok(header, lines)
        elif len(lines) == 1:
            ok = msgBox.ok(header, lines[0])
        elif len(lines) == 2:
            ok = msgBox.ok(header, lines[0], lines[1])
        else:
            ok = msgBox.ok(header, lines[0], lines[1], lines[2])
        return ok

    @staticmethod
    def WaitForPlayerToStart(player, timeout=10, logger=None):
        """ waits for the status of the player to start

        Arguments:
        timeout : integer - the maximum wait time
        logger  : Logger  - A logger to log to.

        Requires: <import addon="xbmc.python" version="2.0"/>

        """
        return XbmcWrapper.__WaitForPlayer(player, 1, timeout, logger)

    @staticmethod
    def WaitForPlayerToEnd(player, timeout=10, logger=None):
        """ waits for the status of the player to end

        Arguments:
        timeout : integer - the maximum wait time
        logger  : Logger  - A logger to log to.

        Requires: <import addon="xbmc.python" version="2.0"/>

        """

        return XbmcWrapper.__WaitForPlayer(player, 0, timeout, logger)

    @staticmethod
    def __WaitForPlayer(player, toStart, timeout, logger):
        """ waits for the status of the player to be the desired value

        Arguments:
        toStart : integer - the desired value (1 = start, 0 = stop)
        timeout : integer - the maximum wait time
        logger  : Logger  - A logger to log to.

        Requires: <import addon="xbmc.python" version="2.0"/>

        """

        start = time.time()

        if logger:
            logger.Debug("player.isPlaying is %s, preferred value is %s", player.isPlaying(), toStart)

        while (time.time() - start < timeout):
            if (player.isPlaying() == toStart):
                # the player stopped in time
                logger.Debug("player.isPlaying obtained the desired value %s", toStart)
                return True

            if logger:
                logger.Debug("player.isPlaying is %s, waiting a cycle for it to become %s", player.isPlaying(), toStart)
            time.sleep(1.)

        # a time out occurred
        return False
