#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================

from config import Config
from helpers.languagehelper import LanguageHelper
from xbmcwrapper import XbmcWrapper
from logger import Logger
from urihandler import UriHandler


#===============================================================================
def CheckVersion(version, updateUrl, verbose=False):
    """Checks if the current version is the most recent one

    Arguments:
    version   : string - the current version in the x.x.x format.
    updateUrl : string - the URL to check for updates.

    Keyword Arguments:
    verbose   : [opt] boolean - if verbose is specified a message is also shown if
                                no updates where found. Defaults to False.

    If a newer version is available a pop-up is shown. If no update is available
    a pop-up is shown only if <verbose> is set to True.

    """

    if updateUrl == "" or updateUrl == None:
        return

    recentVersion = GetLatestVersion(version, updateUrl)
    if recentVersion != 0:
        Logger.Info("New version available: %s", recentVersion)

        # get lines
        lines = LanguageHelper.GetLocalizedString(LanguageHelper.NewVersion2Id, False) % (Config.appName, recentVersion)
        lines = lines.split("|")
        XbmcWrapper.ShowNotification(LanguageHelper.GetLocalizedString(LanguageHelper.NewVersionId), lines, XbmcWrapper.Info, 10000)
    elif verbose:
        XbmcWrapper.ShowNotification(LanguageHelper.GetLocalizedString(LanguageHelper.NoUpdatesId), LanguageHelper.GetLocalizedString(LanguageHelper.NewFrameworkId), XbmcWrapper.Info)
    return


def GetLatestVersion(currentVersion, updateUrl):
    """Calls the XOT update url and returns the response data.

    Arguments:
    currentVersion : string - the current version in the x.x.x format.
    updateUrl      : string - the URL to check for updates.

    The URL returns 0 is the most recent version is installed. If not
    the URL returns the most recent version in the x.x.x format.

    """

    _newVersion = False
    _url = updateUrl + str(currentVersion)

    data = UriHandler.Open(_url, pb=False)
    if data == "" or data == "0":
        return 0
    else:
        return data
