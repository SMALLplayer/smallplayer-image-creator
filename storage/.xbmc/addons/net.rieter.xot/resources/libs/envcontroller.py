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
import sys

import xbmc

from xbmcwrapper import XbmcWrapper
from logger import Logger
from environments import Environments

from helpers.languagehelper import LanguageHelper


class EnvController:
    """Controller class for getting all kinds of information about the
    XBMC environment."""

    def __init__(self, logger=None):
        """Class to determine platform depended stuff

        Keyword Arguments:
        logger : Logger - a logger object that is used to log information to

        """

        self.logger = logger
        pass

    def GetPythonVersion(self):
        """Returns the current python version

        Returns:
        Python version in the #.#.# format

        """

        major = sys.version_info[0]
        minor = sys.version_info[1]
        build = sys.version_info[2]
        return "%s.%s.%s" % (major, minor, build)

    def GetEnvironmentFolder(self):
        """Returns the correct environment folder to import libraries from

        Returns:
        A folder name that can be used append to the Python path to import platform
        dependent packages from for current environment:

        * Linux   - Normal Linux packages
        * Linux64 - 64-bit Linux packages
        * OS X    - For Apple devices
        * win32   - Windows / Native Xbox packages

        If the Python version is higher than 2.4, then a non standard XBMC Python is used
        from which we import packages. In that case we return "".

        """

        major = sys.version_info[0]
        minor = sys.version_info[1]

        if major > 2 or minor > 4:
            # this is not the default XBMC python, so use it's own modules
            return ""
        else:
            return self.GetEnvironment()

    def GetEnvironment(self):
        """Gets the type of environment

        Returns:
        A string defining the OS:
        * Linux   - Normal Linux
        * Linux64 - 64-bit Linux
        * OS X    - For Apple decices
        * win32   - Windows / Native Xbox

        """

        env = os.environ.get("OS", "win32")
        if env == "Linux":
#            (bits, type) = platform.architecture()
#            if bits.count("64") > 0:
#                # first the bits of platform.architecture is checked
#                return "Linux64"
            if sys.maxint >> 33:
                # double check using the sys.maxint
                # and see if more than 32 bits are present
                return "Linux64"
            else:
                return "Linux"
        elif env == "OS X":
            return "OS X"
        else:
            return "win32"

    def IsInstallMethodValid(self, config):
        """ Validates that XOT-uzg.v3 is installed using the repository. If not
        it will popup a dialog box.

        Arguments:
        config : Config - The XOT-Uzg.v3 config object.

        """

        repoAvailable = self.__IsRepoAvailable(config)

        if (not repoAvailable):
            # show alert
            if self.logger:
                self.logger.Warning("No Respository installed. Reminding user to install it.")

            XbmcWrapper.ShowDialog(LanguageHelper.GetLocalizedString(LanguageHelper.RepoWarningId), LanguageHelper.GetLocalizedString(LanguageHelper.RepoWarningDetailId))

        return repoAvailable

    def DirectoryPrinter(self, config, settingInfo):
        """Prints out all the XOT related directories to the logFile.

        This method is mainly used for debugging purposes to provide developers a better insight
        into the system of the user.

        """

        try:
            directory = "<Unknown>"
            # in order to minimize the number of method resolves for os.path.join
            # we create a shortcut for it.
            ospathjoin = os.path.join

            version = xbmc.getInfoLabel("system.buildversion")
            buildDate = xbmc.getInfoLabel("system.builddate")

            repoName = self.__IsRepoAvailable(config, returnName=True)

            envCtrl = EnvController()
            env = envCtrl.GetEnvironment()

            infoString = "%s: %s" % ("Version", version)
            infoString = "%s\n%s: %s" % (infoString, "BuildDate", buildDate)
            infoString = "%s\n%s: %s (folder=\libs\%s)" % (infoString, "Environment", env, envCtrl.GetEnvironmentFolder())
            infoString = "%s\n%s: %s" % (infoString, "Platform", envCtrl.GetPlatform(True))
            infoString = "%s\n%s: %s" % (infoString, "Python Version", envCtrl.GetPythonVersion())
            infoString = "%s\n%s: %s" % (infoString, "XOT-Uzg.v3 Version", config.Version)
            infoString = "%s\n%s: %s" % (infoString, "AddonID", config.addonId)
            infoString = "%s\n%s: %s" % (infoString, "Path", config.rootDir)
            infoString = "%s\n%s: %s" % (infoString, "ProfilePath", config.profileDir)
            infoString = "%s\n%s: %s" % (infoString, "PathDetection", config.pathDetection)
            infoString = "%s\n%s: %s" % (infoString, "Encoding", sys.getdefaultencoding())
            infoString = "%s\n%s: %s" % (infoString, "Repository", repoName)
            self.logger.Info("XBMC Information:\n%s", infoString)

            # log the settings
            self.logger.Info("XOT-Uzg Settings:\n%s", settingInfo)

            if settingInfo.GetLogLevel() > 10:
                return

            # get the script directory
            dirScript = config.addonDir
            walkSourcePath = os.path.abspath(ospathjoin(config.rootDir, ".."))
            dirPrint = "Folder Structure of %s (%s)" % (config.appName, dirScript)

            # instead of walking all directories and files and then see if the
            # folders is in the exclude list, we first list the first children.
            # Then if the child folders contains the dirScript then, walk all
            # the subfolders and files. This greatly improves performance.
            for currentPath in os.listdir(walkSourcePath):
                self.logger.Trace("Checking %s", currentPath)
                if dirScript in currentPath:
                    self.logger.Trace("Now walking DirectoryPrinter")
                    # excludePattern = ospathjoin('a','.svn').replace("a","") -> we now have GIT and no more nested .SVN
                    dirWalker = os.walk(ospathjoin(walkSourcePath, currentPath))

                    for directory, folders, files in dirWalker:  # @UnusedVariables
                        # if directory.count(excludePattern) == 0:
                        if directory.count("BUILD") == 0:
                            for fileName in files:
                                if not fileName.startswith(".") and not fileName.endswith(".pyo"):
                                    dirPrint = "%s\n%s" % (dirPrint, ospathjoin(directory, fileName))
            self.logger.Debug("%s" % (dirPrint))
        except:
            self.logger.Critical("Error printing folder %s", directory, exc_info=True)
    #===========================================================================
    @staticmethod
    def GetPlatform(returnName=False):
        """Returns the platform that XBMC returns as it's host:

        Keyword Arguments:
        returnName : boolean - If true a string value is returned

        Returns:
        A string representing the host OS:
        * linux   - Normal Linux
        * Xbox    - Native Xbox
        * OS X    - Apple OS
        * Windows - Windows OS
        * unknown - in case it's undetermined

        """

        platform = Environments.Unknown

        # it's in the .\xbmc\GUIInfoManager.cpp
        if xbmc.getCondVisibility("system.platform.linux"):
            platform = Environments.Linux
        elif xbmc.getCondVisibility("system.platform.xbox"):
            platform = Environments.Xbox
        elif xbmc.getCondVisibility("system.platform.windows"):
            platform = Environments.Windows
        elif xbmc.getCondVisibility("system.platform.ios"):
            platform = Environments.IOS
        elif xbmc.getCondVisibility("system.platform.atv2"):
            platform = Environments.ATV2
        elif xbmc.getCondVisibility("system.platform.osx"):
            platform = Environments.OSX
        elif xbmc.getCondVisibility("system.platform.android"):
            platform = Environments.Android

        if (returnName):
            return Environments.Name(platform)
        else:
            return platform

    @staticmethod
    def IsPlatform(platform):
        """Checks if the current platform matches the requested on

        Arguments:
        platform : string - The requested platform

        Returns:
        True if the <platform> matches EnvController.GetPlatform().

        """

        plat = EnvController.GetPlatform()

        # check if the actual platform is in the platform bitmask
        # return plat & platform  == platform
        return platform & plat == plat

    @staticmethod
    def GetSkinFolder(rootDir, logFile):
        """Returns the folder that matches the currently active XBMC skin

        Arguments:
        rootDir : String - rootfolder of XOT
        logFile : Logger - logger to write logging to

        Returns:
        The name of the skinfolder that best matches the XBMC skin.

        It looks at the current XBMC skin folder name and tries to match it to
        a skin in the resources/skins/skin.<skin> or resources/skins/<skin> path.
        If a match was found that foldername is returned. If no match was found
        the default skin for XOT (skin.xot) is returned.

        """

        skinName = xbmc.getSkinDir()
        if (os.path.exists(os.path.join(rootDir, "resources", "skins", skinName))):
            skinFolder = skinName
        elif (os.path.exists(os.path.join(rootDir, "resources", "skins", "skin." + skinName.lower()))):
            skinFolder = "skin.%s" % (skinName.lower(),)
        else:
            skinFolder = "skin.xot"
        Logger.Info("Setting Skin to: " + skinFolder)
        return skinFolder

    def __IsRepoAvailable(self, config, returnName=False):
        """ Checks if the repository is available in XBMC and returns it's name.

        Arguments:
        config     : Config  - The configuration object of XOT-Uzg.v3

        Keyword Arguments:
        returnName : Boolean - [opt] If set to True the name of the repository will
                               be returned or a label with the reason why no repo
                               was found.

        """

        NOT_INSTALLED = "<not installed>"
        UNKWOWN = "<data only available in Eden builds>"

        if (EnvController.IsPlatform(Environments.Xbox)):
            if self.logger:
                self.logger.Debug("Skipping repository check on Xbox.")

            if returnName:
                # on Xbox it's never installed.
                return NOT_INSTALLED
            else:
                # always return True for Xbox
                return True

        if (xbmc.getInfoLabel("system.buildversion").startswith("10.")):
            if self.logger:
                self.logger.Debug("Skipping repository check on 10.x builds.")

            if returnName:
                return UNKWOWN
            else:
                # always return True
                return True

        try:
            repoName = "%s.repository" % (config.addonId,)
            repoAvailable = xbmc.getCondVisibility('System.HasAddon("%s")' % (repoName,)) == 1

            if self.logger:
                self.logger.Debug("Checking repository '%s'. Repository available=%s", repoName, repoAvailable)

            if not returnName:
                # return a boolean
                return repoAvailable
            elif repoAvailable:
                # return the name if it was available
                return repoName
            else:
                # return not installed if non was available
                return NOT_INSTALLED
        except:
            self.logger.Error("Error determining Repository Status", exc_info=True)
            if not returnName:
                # in case of error, return True
                return True
            else:
                return "<error>"
