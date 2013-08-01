#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================
import os.path
import sys
import traceback

import xbmc
import xbmcgui

# setup the paths in Python
from initializer import Initializer
Initializer.SetUnicode()
currentPath = Initializer.SetupPythonPaths()


#===============================================================================
# Handles an AttributeError during intialization
#===============================================================================
def HandleInitAttributeError(loadedModules):
    if(Logger.Exists()):
        Logger.Critical("AtrributeError during intialization", exc_info=True)
        if ("config" in loadedModules):
            Logger.Debug("'config' was imported from %s", Config.__file__)
        if ("logger" in loadedModules):
            Logger.Debug("'logger' was imported from %s", Logger.__file__)
        if ("UriHandler" in loadedModules):
            Logger.Debug("'UriHandler' was imported from %s", UriHandler.__file__)
        if ("common" in loadedModules):
            Logger.Debug("'common' was imported from %s", common.__file__)
        if ("update" in loadedModules):
            Logger.Debug("'update' was imported from %s", update.__file__)
    else:
        traceback.print_exception(sys.exc_info()[0], sys.exc_info()[1], sys.exc_info()[2])
        if ("config" in loadedModules):
            print("'config' was imported from %s" % Config.__file__)
        if ("logger" in loadedModules):
            print("'logger' was imported from %s" % Logger.__file__)
        if ("UriHandler" in loadedModules):
            print("'UriHandler' was imported from %s" % UriHandler.__file__)
        if ("common" in loadedModules):
            print("'common' was imported from %s" % common.__file__)
        if ("update" in loadedModules):
            print("'update' was imported from %s" % update.__file__)
    return


def RunPlugin():
    """ Runs XOT-Uzg.v3 as a Video Add-On """

    try:
        from config import Config
        from helpers.sessionhelper import SessionHelper

        # get a logger up and running
        from logger import Logger

        # only append if there are not arguments (main add-on call) and we have
        # no active session (in that case we came back to the channel list
        if sys.argv[2].strip('?') == "" and not SessionHelper.IsSessionActive():
            # first call in the cycle, so cleanup log
            appendLogFile = False
        else:
            appendLogFile = True
        Logger.CreateLogger(os.path.join(Config.rootDir, Config.logFileNamePlugin), Config.logDual, Config.appName, append=appendLogFile, memoryInfoProvider=xbmc.getFreeMem)

        from urihandler import UriHandler
        import addonsettings

        # set the pluginmode
        addonsettings.AddonSettings.SetPluginMode(True)

        # update the loglevel
        Logger.Instance().minLogLevel = addonsettings.AddonSettings().GetLogLevel()

        # useProgressBars = not envcontroller.EnvController.IsPlatform(envcontroller.Environments.Xbox)
        useCaching = addonsettings.AddonSettings().CacheHttpResponses()
        UriHandler.CreateUriHandler(useProgressBars=False, useCaching=useCaching)

        # set skin folder
        import envcontroller
        Config.skinFolder = envcontroller.EnvController.GetSkinFolder(Config.rootDir, Logger.Instance())

        # log the type
        # from helpers.statistics import Statistics
        # Statistics.RegisterRunType("Plugin")

        # run the plugin
        import plugin
        plugin.XotPlugin(sys.argv[0], sys.argv[2], sys.argv[1])

        # close the log to prevent locking on next call
        Logger.Instance().CloseLog()

        # make sure we leave no references behind
        addonsettings.AddonSettings.ClearCachedAddonSettingsObject()
    except AttributeError:
        HandleInitAttributeError(dir())
    except:
        # globalLogger.Critical("Error initializing %s plugin", Config.appName, exc_info=True)
        try:
            orgEx = sys.exc_info()
            Logger.Critical("Error initializing %s plugin", Config.appName, exc_info=True)
        except:
            print "Exception during the initialisation of the script. No logging information was present because the logger was not loaded."
            traceback.print_exception(orgEx[0], orgEx[1], orgEx[2])

#===============================================================================
# Here the script starts
#===============================================================================
# Check for function: Plugin or Script
if hasattr(sys, "argv") and len(sys.argv) > 1:
    #===============================================================================
    # PLUGIN: Import XOT stuff
    #===============================================================================
    # import profile
    # import cProfile
    # For PC
    # statsPath = os.path.abspath(os.path.join(currentPath, "../data/xot-uzg.v3.pc.pstats"))
    # cProfile.run("RunPlugin()", statsPath)
    # For ATV
    # cProfile.run("RunPlugin()", os.path.abspath("xot-uzg.v3.atv2.pstats"))
    # Normal run
    RunPlugin()
else:
    #===============================================================================
    # SCRIPT: Setup the script
    #===============================================================================
    try:
        pb = xbmcgui.DialogProgress()
        from config import Config  # @Reimport
        pb.create("Initialising %s" % (Config.appName), "Importing configuration")

        pb.update(10, "Initialising Logger")
        from logger import Logger  # @Reimport
        Logger.CreateLogger(os.path.join(Config.rootDir, Config.logFileName), Config.logDual, Config.appName, memoryInfoProvider=xbmc.getFreeMem)

        # from here on we we can use the translations as we have a Logger which is needed by the AddonSettings

        pb.update(20, "Loading regional data.")
        from helpers.languagehelper import LanguageHelper

        pb.update(25, "%s UriHandler" % LanguageHelper.GetLocalizedString(LanguageHelper.InitializingId))
        from urihandler import UriHandler  # @Reimport
        import addonsettings  # @Reimport
        # set the pluginmode
        addonsettings.AddonSettings.SetPluginMode(False)

        # update the loglevel
        Logger.Instance().minLogLevel = addonsettings.AddonSettings().GetLogLevel()

        useCaching = addonsettings.AddonSettings().CacheHttpResponses()
        UriHandler.CreateUriHandler(useCaching=useCaching)

        pb.update(35, LanguageHelper.GetLocalizedString(LanguageHelper.ImportCommonId))
        import common
        import envcontroller  # @Reimport
        envCntrl = envcontroller.EnvController(Logger.Instance())
        envCntrl.DirectoryPrinter(Config, addonsettings.AddonSettings())

        pb.update(50, LanguageHelper.GetLocalizedString(LanguageHelper.DeterminSkinId))
        Config.skinFolder = envcontroller.EnvController.GetSkinFolder(Config.rootDir, Logger.Instance())

        Logger.Info("************** Starting %s version v%s **************", Config.appName, Config.Version)
        Logger.Info("Skinfolder = %s", Config.skinFolder)
        print("************** Starting %s version v%s **************" % (Config.appName, Config.Version))

        # check for updates
        pb.update(60, LanguageHelper.GetLocalizedString(LanguageHelper.CheckForUpdatesId))
        import update
        try:
            update.CheckVersion(Config.Version, Config.updateUrl)
            pass
        except:
            Logger.Critical("Error checking for updates", exc_info=True)

        pb.update(70, LanguageHelper.GetLocalizedString(LanguageHelper.RepoVerificationId))
        envCntrl.IsInstallMethodValid(Config)

        pb.update(80, LanguageHelper.GetLocalizedString(LanguageHelper.CacheCheckId))
        common.CacheCheck()

        pb.update(90, LanguageHelper.GetLocalizedString(LanguageHelper.CacheCleanupId))

        # cleanup the cachefolder
        aSet = addonsettings.AddonSettings()
        common.CacheCleanUp(Config.cacheDir, Config.cacheValidTime)
        common.CacheCleanUp(aSet.GetUzgCachePath(), aSet.GetUzgCacheDuration() * 24 * 3600, "xot.*")

        pb.close()

        #===============================================================================
        # Now starting the real app
        #===============================================================================
        if not pb.iscanceled():
            import progwindow
            MyWindow = progwindow.GUI(Config.appSkin, Config.rootDir, Config.skinFolder)

            # log the type
            from helpers.statistics import Statistics
            Statistics.RegisterRunType("Script", Initializer.StartTime)

            MyWindow.doModal()
            del MyWindow

            # make sure we leave no references behind
            addonsettings.AddonSettings.ClearCachedAddonSettingsObject()
        else:
            # close the log to prevent locking on next call
            Logger.Instance().CloseLog()

    except AttributeError:
        HandleInitAttributeError(dir())
    except:
        try:
            orgEx = sys.exc_info()
            Logger.Critical("Error initializing %s script", Config.appName, exc_info=True)

            # close the log to prevent locking on next call
            Logger.Instance().CloseLog()
        except:
            print "Exception during the initialisation of the script. No logging information was present because the logger was not loaded."
            traceback.print_exception(orgEx[0], orgEx[1], orgEx[2])
        pb.close()
