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
import cPickle as pickle
import base64
import inspect
import urllib

import xbmcplugin
import xbmc

#===============================================================================
# Import XOT stuff
#===============================================================================
try:
    import common
    import settings
    import addonsettings
    import update
    import envcontroller

    from locker import LockWithDialog
    from config import Config
    from xbmcwrapper import XbmcWrapper
    from environments import Environments
    from initializer import Initializer
    from helpers.channelimporter import ChannelImporter
    from helpers.languagehelper import LanguageHelper
    from helpers import stopwatch
    from helpers.statistics import Statistics
    from helpers.sessionhelper import SessionHelper

    #===========================================================================
    # Make global object available
    #===========================================================================
    from logger import Logger
except:
    Logger.Critical("Error initializing %s", Config.appName, exc_info=True)


#===============================================================================
# Main Plugin Class
#===============================================================================
class XotPlugin:
    """Main Plugin Class

    This class makes it possible to access all the XOT channels as a XBMC plugin
    instead of a script. s

    """

    def __init__(self, pluginName, params, handle=0):
        """Initialises the plugin with given arguments."""

        # some constants
        self.actionDownloadVideo = "downloadVideo".lower()          # : Action used to download a video item
        self.actionFavorites = "favorites".lower()                  # : Action used to show favorites for a channel
        self.actionRemoveFavorite = "removefromfavorites".lower()   # : Action used to remove items from favorites
        self.actionAddFavorite = "addtofavorites".lower()           # : Action used to add items to favorites
        self.actionPlayVideo = "playvideo".lower()                  # : Action used to play a video item
        self.actionUpdateChannels = "updatechannels".lower()        # : Action used to update channels
        self.actionParseMainList = "mainlist".lower()               # : Action used to show the mainlist
        self.actionListFolder = "listfolder".lower()                # : Action used to list a folder

        self.keywordPickle = "pickle".lower()                       # : Keyword used for the pickle item
        self.keywordAction = "action".lower()                       # : Keyword used for the action item
        self.keywordChannel = "channel".lower()                     # : Keyword used for the channel
        self.keywordChannelCode = "channelcode".lower()             # : Keyword used for the channelcode

        self.pluginName = pluginName
        self.handle = int(handle)

        self.settings = addonsettings.AddonSettings()

        # channel objects
        self.channelObject = ""
        self.channelFile = ""
        self.channelCode = None
        self.channelObject = ""

        self.contentType = "movies"
        self.bulkInsert = True         # : if set to true, xbmcplugin.addDirectoryItems will be used instead of xbmcplugin.addDirectoryItem
        self.quotedPlus = False        # : Should we use urllib.quote_plus to create url's. It is very slow!
        self.pickleContainer = dict()  # : storage for pickled items to prevent duplicate pickling
        self.methodContainer = dict()  # : storage for the inspect.getmembers(channel) method. Improves performance
        self.base64chars = {"\n": "-", "=": "%3d", "/": "%2f", "+": "%2b"}

        # determine the query parameters
        self.params = self.__GetParameters(params)

        Logger.Info("*********** Starting %s plugin version v%s ***********", Config.appName, Config.Version)
        Logger.Debug("Plugin Params: %s (%s) [handle=%s, name=%s, query=%s]", self.params, len(self.params), self.handle, self.pluginName, params)

        #===============================================================================
        #        Start the plugin version of progwindow
        #===============================================================================
        if len(self.params) == 0:
            envCtrl = envcontroller.EnvController(Logger.Instance())

            # do add-on start stuff
            sessionActive = SessionHelper.IsSessionActive(Logger)
            if not sessionActive:
                Logger.Info("Add-On start detected. Performing startup actions.")

                # print the folder structure
                envCtrl.DirectoryPrinter(Config, addonsettings.AddonSettings())

                # show notification
                XbmcWrapper.ShowNotification(None, LanguageHelper.GetLocalizedString(LanguageHelper.StartingAddonId) % (Config.appName,), fallback=False, logger=Logger)

            # clear the session to indicate we have a clean start
            SessionHelper.ClearSession()

            # check for updates
            update.CheckVersion(Config.Version, Config.updateUrl)

            # check if the repository is available
            envCtrl.IsInstallMethodValid(Config)

            # check for cache folder
            common.CacheCheck()

            # do some cache cleanup
            common.CacheCleanUp(Config.cacheDir, Config.cacheValidTime)
            common.CacheCleanUp(self.settings.GetUzgCachePath(), self.settings.GetUzgCacheDuration() * 24 * 3600, "xot.*")

            # Show initial start if not in a session
            # now show the list
            self.ShowChannelList()

            if not sessionActive:
                # log the type
                Statistics.RegisterRunType("Plugin", Initializer.StartTime)

        #===============================================================================
        #        Start the plugin verion of the episode window
        #===============================================================================
        else:
            # check for cache folder
            common.CacheCheck()

            # create a session
            SessionHelper.CreateSession()

            try:
                # Determine what stage we are in. Check that there are more than 2 Parameters
                if len(self.params) > 1:
                    # retrieve channel characteristics
                    self.channelFile = os.path.splitext(self.params[self.keywordChannel])[0]
                    self.channelCode = self.params[self.keywordChannelCode]
                    Logger.Debug("Found Channel data in URL: channel='%s', code='%s'", self.channelFile, self.channelCode)

                    # import the channel
                    channelRegister = ChannelImporter.GetRegister()
                    channel = channelRegister.GetSingleChannel(self.channelFile, self.channelCode)

                    if not channel is None:
                        self.channelObject = channel
                    else:
                        Logger.Critical("None or more than one channels were found, unable to continue.")
                        return

                    # init the channel as plugin
                    self.channelObject.InitPlugin()
                    Logger.Info("Loaded: %s", self.channelObject.channelName)
                else:
                    Logger.Critical("Error determining Plugin action")
                    return

                #===============================================================================
                # See what needs to be done.
                #===============================================================================
                if (not self.keywordAction in self.params):
                    Logger.Critical("Action parameters missing from request. Parameters=%s", self.params)
                    return

                if self.params[self.keywordAction] == self.actionParseMainList:
                    # only the channelName and code is present, so ParseMainList is needed
                    self.ParseMainList()

                elif self.params[self.keywordAction] == self.actionFavorites:
                    # we should show the favorites
                    self.ParseMainList(showFavorites=True)

                elif self.params[self.keywordAction] == self.actionUpdateChannels:
                    self.UpdateChannels()

                elif self.params[self.keywordAction] == self.actionListFolder:
                    # channelName and URL is present, Parse the folder
                    self.ProcessFolderList()

                elif self.params[self.keywordAction] == self.actionRemoveFavorite:
                    self.RemoveFavorite()

                elif self.params[self.keywordAction] == self.actionAddFavorite:
                    self.AddFavorite()

                elif self.params[self.keywordAction] == self.actionPlayVideo:
                    self.PlayVideoItem()

                elif not self.params[self.keywordAction] == "":
                    self.OnActionFromContextMenu(self.params[self.keywordAction])

                else:
                    Logger.Warning("Number of parameters (%s) or parameter (%s) values not implemented", len(self.params), self.params)

            except:
                Logger.Critical("Error parsing for add-on", exc_info=True)

    def ShowChannelList(self):
        """Displays the channels that are currently available in XOT as a directory
        listing."""

        Logger.Info("Plugin::ShowChannelList")
        try:
            # import ProgWindow
            ok = False

            # only display channels
            channelRegister = ChannelImporter.GetRegister()
            channels = channelRegister.GetChannels(infoOnly=True)

            xbmcItems = []
            for channel in channels:
                item = channel.GetXBMCItem()

                contextMenuItems = self.__GetContextMenuItems(channel)
                item.addContextMenuItems(contextMenuItems)

                url = self.__CreateActionUrl(channel, action=self.actionParseMainList)

                if self.bulkInsert:
                    xbmcItems.append((url, item, True))
                else:
                    ok = xbmcplugin.addDirectoryItem(self.handle, url, item, isFolder=True, totalItems=len(channels))
                    if (not ok):
                            break

            if self.bulkInsert:
                ok = xbmcplugin.addDirectoryItems(self.handle, xbmcItems, len(xbmcItems))

            xbmcplugin.addSortMethod(handle=self.handle, sortMethod=xbmcplugin.SORT_METHOD_TRACKNUM)
            # xbmcplugin.setContent(handle=self.handle, content=self.contentType)
            # xbmcplugin.addSortMethod(handle=self.handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)

            xbmcplugin.endOfDirectory(self.handle, ok)
        except:
            xbmcplugin.endOfDirectory(self.handle, False)
            Logger.Critical("Error fetching channels for plugin", exc_info=True)

    def ParseMainList(self, showFavorites=False, replaceExisting=False):
        """Wraps the channel.ParseMainList

        Keyword Arguments:
        showFavorites : boolean - if True it will show the favorites instead of all the items

        """

        Logger.Info("Plugin::ParseMainList")
        stopWatch = stopwatch.StopWatch("Plugin Mainlist timer", Logger.Instance())
        try:
            ok = False

            # only the channelName and code is present, so ParseMainList is needed
            if showFavorites:
                Logger.Info("Showing Favorites")

                # self.favoriteItems = settings.LoadFavorites(self.activeChannelGUI)
                # self.ShowListItems(self.favoriteItems)
                episodeItems = settings.LoadFavorites(self.channelObject)
                if len(episodeItems) == 0:
                    Logger.Info("No favorites available")
                    XbmcWrapper.ShowNotification(LanguageHelper.GetLocalizedString(LanguageHelper.ErrorId), LanguageHelper.GetLocalizedString(LanguageHelper.NoFavsId), XbmcWrapper.Warning)

                # Logger.Debug(episodeItems)
                # nothing to show, set to true
                ok = True
                pass
            else:
                Logger.Info("Showing normal program list")

                episodeItems = self.channelObject.ParseMainList()

            stopWatch.Lap("Items retrieved")

            # create the XBMC items
            xbmcItems = map(lambda episodeItem: self.__ConvertMainlistItemToXbmcItem(episodeItem, showFavorites), episodeItems)
            # xbmcItems = [self.__ConvertMainlistItemToXbmcItem(episodeItem, showFavorites) for episodeItem in episodeItems]
            stopWatch.Lap("Items for XBMC generated")

            # add them to XBMC
            ok = xbmcplugin.addDirectoryItems(self.handle, xbmcItems, len(xbmcItems)) and len(xbmcItems) > 0
            stopWatch.Lap("items send to XBMC")

            self.__AddSortMethodToHandle(self.handle, episodeItems)

            # set the content
            xbmcplugin.setContent(handle=self.handle, content=self.contentType)

            # close the directory
            if showFavorites:
                Logger.Debug("Plugin::Favorites completed")
                # make sure we do not cache this one to disc!
                xbmcplugin.endOfDirectory(self.handle, succeeded=ok, updateListing=replaceExisting, cacheToDisc=False)
            else:
                Logger.Debug("Plugin::Processing Mainlist completed. Returned %s items", len(episodeItems))
                xbmcplugin.endOfDirectory(self.handle, succeeded=ok, updateListing=replaceExisting)

                # call for statistics
                Statistics.RegisterChannelOpen(self.channelObject, Initializer.StartTime)
                stopWatch.Lap("Statistics send")

            # stop the timer
            stopWatch.Stop()
        except:
            Logger.Error("Plugin::Error parsing mainlist", exc_info=True)
            xbmcplugin.endOfDirectory(self.handle, False)

    def ProcessFolderList(self):
        """Wraps the channel.ProcessFolderList"""

        Logger.Info("Plugin::ProcessFolderList Doing ProcessFolderList")
        try:
            ok = False

            selectedItem = self.__DePickleMediaItem(self.params[self.keywordPickle])

            watcher = stopwatch.StopWatch("Plugin ProcessFolderList", Logger.Instance())
            episodeItems = self.channelObject.ProcessFolderList(selectedItem)
            watcher.Lap("Class ProcessFolderList finished")

            Logger.Debug("ProcessFolderList returned %s items", len(episodeItems))
            xbmcItems = []
            for episodeItem in episodeItems:
                # Logger.Debug("Adding: %s", episodeItem)

                if episodeItem.type == 'folder' or episodeItem.type == 'append' or episodeItem.type == "page":
                    # it's a folder page or append style. Append as an XBMC folder
                    item = episodeItem.GetXBMCItem(True)

                    contextMenuItems = self.__GetContextMenuItems(self.channelObject, item=episodeItem)
                    item.addContextMenuItems(contextMenuItems)

                    url = self.__CreateActionUrl(self.channelObject, self.actionListFolder, item=episodeItem)

                    if self.bulkInsert:
                        xbmcItems.append((url, item, True))
                    else:
                        ok = xbmcplugin.addDirectoryItem(self.handle, url, item, isFolder=True, totalItems=len(episodeItems))

                # elif episodeItem.type=="video":
                elif episodeItem.IsPlayable():
                    # we will process the videoitem as a playlist and add contextmenu's
                    item = episodeItem.GetXBMCItem(pluginMode=True)

                    contextMenuItems = self.__GetContextMenuItems(self.channelObject, item=episodeItem)
                    item.addContextMenuItems(contextMenuItems)

                    url = self.__CreateActionUrl(self.channelObject, action=self.actionPlayVideo, item=episodeItem)

                    if self.bulkInsert:
                        xbmcItems.append((url, item, False))
                    else:
                        ok = xbmcplugin.addDirectoryItem(int(self.handle), url, item, totalItems=len(episodeItems))

                else:
                    Logger.Critical("Plugin::ProcessFolderList: Cannot determine what to add")

                if (not ok and not self.bulkInsert):
                    break

            watcher.Lap("XBMC Items generated")
            if self.bulkInsert:
                ok = xbmcplugin.addDirectoryItems(self.handle, xbmcItems, len(xbmcItems))

            if (len(episodeItems) == 0):
                XbmcWrapper.ShowNotification(LanguageHelper.GetLocalizedString(LanguageHelper.ErrorId), LanguageHelper.GetLocalizedString(LanguageHelper.NoVideosId), XbmcWrapper.Error)
                ok = False

            watcher.Stop()

            self.__AddSortMethodToHandle(self.handle, episodeItems)

            # set the content
            xbmcplugin.setContent(handle=self.handle, content=self.contentType)

            xbmcplugin.endOfDirectory(self.handle, ok)
        except:
            xbmcplugin.endOfDirectory(self.handle, False)
            Logger.Error("Plugin::Error Processing FolderList", exc_info=True)

    @LockWithDialog(logger=Logger.Instance())
    def RemoveFavorite(self):
        """Removes an item from the favorites"""

        Logger.Debug("Removing favorite")

        # remove the item
        item = self.__DePickleMediaItem(self.params[self.keywordPickle])
        settings.RemoveFromFavorites(item, self.channelObject)

        # refresh the list
        self.ParseMainList(showFavorites=True, replaceExisting=True)
        pass

    @LockWithDialog(logger=Logger.Instance())
    def AddFavorite(self):
        """Adds an item to the favorites"""

        Logger.Debug("Adding favorite")

        # remove the item
        item = self.__DePickleMediaItem(self.params[self.keywordPickle])
        settings.AddToFavorites(item, self.channelObject)

        # we are finished, so just return
        return self.ParseMainList(showFavorites=True)

    @LockWithDialog(logger=Logger.Instance())
    def PlayVideoItem(self):
        """Starts the videoitem using a playlist. """

        Logger.Debug("Playing videoitem using PlayListMethod")

        item = self.__DePickleMediaItem(self.params[self.keywordPickle])

        if not item.complete:
            item = self.channelObject.UpdateVideoItem(item)

        # validated the updated item
        if not item.complete:
            Logger.Warning("UpdateVideoItem returned an item that had item.complete = False:\n%s", item)

        if not item.HasMediaItemParts():
            # the update failed or no items where found. Don't play
            XbmcWrapper.ShowNotification(LanguageHelper.GetLocalizedString(LanguageHelper.ErrorId), LanguageHelper.GetLocalizedString(LanguageHelper.NoStreamsId), XbmcWrapper.Error)
            Logger.Warning("Could not start playback due to missing streams. Item:\n%s", item)
            return

        playData = self.channelObject.PlayVideoItem(item, pluginMode=True)
        Logger.Debug("Continuing playback in plugin.py")
        if not playData:
            Logger.Warning("PlayVideoItem did not return valid playdata")
            return
        else:
            (playList, srt, xbmcPlayer) = playData

        # now we force the busy dialog to close, else the video will not play and the
        # setResolved will not work.
        xbmc.executebuiltin("Dialog.Close(busydialog)")

        if item.IsResolvable():
            # now set the resolve to the first URL
            startIndex = playList.getposition()  # the current location
            if startIndex < 0:
                startIndex = 0
            Logger.Info("Playing stream @ playlist index %s using setResolvedUrl method", startIndex)
            xbmcplugin.setResolvedUrl(self.handle, True, playList[startIndex])
        else:
            # playlist do not use the setResolvedUrl
            Logger.Info("Playing stream using Playlist method")
            xbmcPlayer.play(playList)

        # the set the subtitles
        showSubs = addonsettings.AddonSettings().UseSubtitle()
        if srt and (srt != ""):
            Logger.Info("Adding subtitle: %s and setting showSubtitles to %s", srt, showSubs)
            XbmcWrapper.WaitForPlayerToStart(xbmcPlayer, 10, Logger.Instance())

            xbmcPlayer.setSubtitles(srt)
            xbmcPlayer.showSubtitles(showSubs)
        return

    def UpdateChannels(self):
        """Shows the XOT Channel update dialog (only for XBMC4Xbox).

        Arguments:
        selectedIndex : integer - the index of the currently selected item this
                                  one is not used here.

        """
        import updater

        updaterWindow = updater.Updater(Config.updaterSkin, Config.rootDir, Config.skinFolder)
        updaterWindow .doModal()
        del updaterWindow

    def OnActionFromContextMenu(self, action):
        """Peforms the action from a custom contextmenu

        Arguments:
        action : String - The name of the method to call

        """
        Logger.Debug("Performing Custom Contextmenu command: %s", action)

        item = self.__DePickleMediaItem(self.params[self.keywordPickle])
        if not item.complete and self.__ContextActionRequiredCompletedItem(action):
            Logger.Debug("The contextmenu action requires a completed item. Updating %s", item)
            item = self.channelObject.UpdateVideoItem(item)

            if not item.complete:
                Logger.Warning("UpdateVideoItem returned an item that had item.complete = False:\n%s", item)

        # invoke
        functionString = "returnItem = self.channelObject.%s(item)" % (action,)
        Logger.Debug("Calling '%s'", functionString)
        try:
            exec(functionString)
        except:
            Logger.Error("OnActionFromContextMenu :: Cannot execute '%s'.", functionString, exc_info=True)
        return



    def __PickleMediaItem(self, item):
        """Serialises a mediaitem

        Arguments:
        item : MediaItem - the item that should be serialized

        Returns:
        A pickled and base64 encoded serialization of the <item>.

        """

        if item.guid in self.pickleContainer:
            # Logger.Trace("Pickle Container cache hit")
            return self.pickleContainer[item.guid]

        pickleString = pickle.dumps(item)
        # Logger.Trace("Pickle: PickleString: %s", pickleString)
        hexString = base64.b64encode(pickleString)

        # if not unquoted, we must replace the \n's for the URL
        if not self.quotedPlus:
            hexString = reduce(lambda x, y: x.replace(y, self.base64chars[y]), self.base64chars, hexString)

        # Logger.Trace("Pickle: HexString: %s", hexString)

        self.pickleContainer[item.guid] = hexString
        return hexString

    def __DePickleMediaItem(self, hexString):
        """De-serializes a serialized mediaitem

        Arguments:
        hexString : string - Base64 encoded string that should be decoded.

        Returns:
        The object that was Pickled and Base64 encoded.

        """

        hexString = hexString.rstrip(' ')
        if not self.quotedPlus:
            hexString = reduce(lambda x, y: x.replace(self.base64chars[y], y), self.base64chars, hexString)
            # hexString = urllib.unquote_plus(hexString).replace("-", "\n").replace("%3D", "=").replace("%2F", "/").replace("%2B","+")

        Logger.Debug("DePickle: HexString: %s", hexString)

        # Logger.Trace("DePickle: HexString: %s", hexString)
        pickleString = base64.b64decode(hexString)
        # Logger.Trace("DePickle: PickleString: %s", pickleString)
        pickleItem = pickle.loads(pickleString)
        return pickleItem

    def __ConvertMainlistItemToXbmcItem(self, episodeItem, showFavorites):
        item = episodeItem.GetXBMCItem(pluginMode=True)

        # add the remove from favorites item:
        if showFavorites:
            # XBMC.Container.Refresh refreshes the container and replaces the last history
            # XBMC.Container.Update updates the container and but appends the new list to the history
            contextMenuItems = self.__GetContextMenuItems(self.channelObject, item=episodeItem, favoritesList=True)
        else:
            contextMenuItems = self.__GetContextMenuItems(self.channelObject, item=episodeItem)

            # add the show favorites here
            cmdUrl = self.__CreateActionUrl(self.channelObject, action=self.actionFavorites)
            cmd = "XBMC.Container.Update(%s)" % (cmdUrl,)
            favs = LanguageHelper.GetLocalizedString(LanguageHelper.FavouritesId)
            show = LanguageHelper.GetLocalizedString(LanguageHelper.ShowId)
            contextMenuItems.append(('XOT: %s %s' % (show, favs), cmd))

        item.addContextMenuItems(contextMenuItems)

        url = self.__CreateActionUrl(self.channelObject, self.actionListFolder, item=episodeItem)

        return (url, item, True)

    def __AddSortMethodToHandle(self, handle, items=None):
        """ Add a sort method to the plugin output. It takes the Add-On settings into
        account. But if none of the items have a date, it is forced to sort by name.

        Arguments:
        handle : int        - The handle to add the sortmethod to
        items  : MediaItems - The items that need to be sorted

        """

        sortAlgorthim = addonsettings.AddonSettings().GetSortAlgorithm()

        if sortAlgorthim == "date":
            # if we had a list, check it for dates. Else assume that there are no dates!
            if items:
                hasDates = len(filter(lambda i: i.HasDate(), items)) > 0
            else:
                hasDates = True

            if hasDates:
                Logger.Debug("Sorting method default: Dates")
                xbmcplugin.addSortMethod(handle=handle, sortMethod=xbmcplugin.SORT_METHOD_DATE)
                xbmcplugin.addSortMethod(handle=handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
                xbmcplugin.addSortMethod(handle=handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            else:
                Logger.Debug("Sorting method default: Dates, but no dates are available, sorting by name")
                xbmcplugin.addSortMethod(handle=handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
                xbmcplugin.addSortMethod(handle=handle, sortMethod=xbmcplugin.SORT_METHOD_DATE)
                xbmcplugin.addSortMethod(handle=handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)

        elif sortAlgorthim == "name":
            Logger.Debug("Sorting method default: Names")
            xbmcplugin.addSortMethod(handle=handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
            xbmcplugin.addSortMethod(handle=handle, sortMethod=xbmcplugin.SORT_METHOD_DATE)
            xbmcplugin.addSortMethod(handle=handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)

        else:
            Logger.Debug("Sorting method default: None")
            xbmcplugin.addSortMethod(handle=handle, sortMethod=xbmcplugin.SORT_METHOD_UNSORTED)
            xbmcplugin.addSortMethod(handle=handle, sortMethod=xbmcplugin.SORT_METHOD_LABEL)
            xbmcplugin.addSortMethod(handle=handle, sortMethod=xbmcplugin.SORT_METHOD_DATE)
        return

    def __ContextActionRequiredCompletedItem(self, action):
        """Get the current context menu and returns if it requires
        an complete MediaItem

        Arguments:
        action : string - the Action that the contextmenu should perform

        """

        for menuItem in self.channelObject.contextMenuItems:
            if menuItem.functionName == action:
                if menuItem.completeStatus is None:
                    return False
                else:
                    # if complete status = False, we don't need a completed one
                    # if complete status = True, we do need one
                    return menuItem.completeStatus

        Logger.Warning("ContextMenuAction [%s] not found in channel", action)
        return False

    def __CreateActionUrl(self, channel, action, item=None):
        """Creates an URL that includes an action

        Arguments:
        channel : Channel - The channel object to use for the URL
        action  : string  - Action to create an url for

        Keyword Arguments:
        item : MediaItem - The media item to add

        """
        if (action is None):
            raise "action is required"

        params = dict()
        params[self.keywordChannel] = channel.moduleName
        if channel.channelCode:
            params[self.keywordChannelCode] = channel.channelCode
        params[self.keywordAction] = action

        # it might have an item or not
        if not item is None:
            params[self.keywordPickle] = self.__PickleMediaItem(item)

        url = "%s?" % (self.pluginName)
        for k in params.keys():
            if (self.quotedPlus):
                url = "%s%s=%s&" % (url, k, urllib.quote_plus(params[k]))
            else:
                url = "%s%s=%s&" % (url, k, params[k])

        url = url.strip('&')
        #Logger.Trace("Created url: '%s'", url)
        return url

    def __GetContextMenuItems(self, channel, item=None, favoritesList=False):
        """Retrieves the context menu items to display

        Arguments:
        channel : Channel - The channel from which to get the context menu items

        Keyword Arguments
        item          : MediaItem - The item to which the context menu belongs.
        favoritesList : Boolean   - Indication that the menu is for the favorites
        """

        contextMenuItems = []

        favs = LanguageHelper.GetLocalizedString(LanguageHelper.FavouritesId)

        if item is None:
            # it's just the channel, so only add the favorites
            cmdUrl = self.__CreateActionUrl(channel, action=self.actionFavorites)
            cmd = "XBMC.Container.Update(%s)" % (cmdUrl,)
            #Logger.Trace("Adding command: %s", cmd)
            show = LanguageHelper.GetLocalizedString(LanguageHelper.ShowId)
            contextMenuItems.append(("XOT: %s %s" % (show, favs), cmd))

            if envcontroller.EnvController.IsPlatform(Environments.Xbox):
                # we need to run RunPlugin here instead of Refresh as we don't want to refresh any lists
                # the refreshing results in empty lists in XBMC4Xbox.
                cmdUrl = self.__CreateActionUrl(channel, action=self.actionUpdateChannels)
                cmd = "XBMC.RunPlugin(%s)" % (cmdUrl,)
                Logger.Trace("Adding command: %s", cmd)
                channels = LanguageHelper.GetLocalizedString(LanguageHelper.ChannelsId)
                contextMenuItems.append(("XOT: Update %s" % (channels,), cmd))

            return contextMenuItems

        # add a default enqueu list
        cmd = "XBMC.Action(Queue)"
        enqueue = LanguageHelper.GetLocalizedString(LanguageHelper.QueueItemId)
        contextMenuItems.append(("%s" % (enqueue,), cmd))
        #Logger.Trace("Adding command: %s", cmd[:100])

        # add a default refresh list
        cmd = "XBMC.Container.Refresh()"
        refresh = LanguageHelper.GetLocalizedString(LanguageHelper.RefreshListId)
        contextMenuItems.append(("XOT: %s" % (refresh,), cmd))
        #Logger.Trace("Adding command: %s", cmd)

        # we have an item
        if favoritesList:
            # we have list of favorites
            cmdUrl = self.__CreateActionUrl(self.channelObject, action=self.actionRemoveFavorite, item=item)
            cmd = "XBMC.Container.Update(%s)" % (cmdUrl,)
            #Logger.Trace("Adding command: %s", cmd)

            remove = LanguageHelper.GetLocalizedString(LanguageHelper.RemoveId)
            fav = LanguageHelper.GetLocalizedString(LanguageHelper.FavouriteId)
            contextMenuItems.append(("XOT: %s %s" % (remove, fav), cmd))

        elif item.type == "folder":
            # we need to run RunPlugin here instead of Refresh as we don't want to refresh any lists
            # the refreshing results in empty lists in XBMC4Xbox.
            cmdUrl = self.__CreateActionUrl(channel, action=self.actionAddFavorite, item=item)
            # cmd = "XBMC.RunPlugin(%s)" % (cmdUrl,)
            cmd = "XBMC.Container.Update(%s)" % (cmdUrl,)
            #Logger.Trace("Adding command: %s", cmd)
            addTo = LanguageHelper.GetLocalizedString(LanguageHelper.AddToId)
            contextMenuItems.append(("XOT: %s %s" % (addTo, favs), cmd))

        # now we process the other items
        possibleMethods = self.__GetMembers(channel)
        # Logger.Debug(possibleMethods)

        for menuItem in channel.contextMenuItems:
            # Logger.Debug(menuItem)
            if not menuItem.plugin:
                continue

            if menuItem.itemTypes == None or item.type in menuItem.itemTypes:
                # We don't care for complete here!
                # if menuItem.completeStatus == None or menuItem.completeStatus == item.complete:

                # see if the method is available
                methodAvailable = False

                for method in possibleMethods:
                    if method[0] == menuItem.functionName:
                        methodAvailable = True
                        # break from the method loop
                        break

                if not methodAvailable:
                    Logger.Warning("No method for: %s", menuItem)
                    continue

                cmdUrl = self.__CreateActionUrl(channel, action=menuItem.functionName, item=item)
                cmd = "XBMC.RunPlugin(%s)" % (cmdUrl,)
                title = "XOT: %s" % (menuItem.label,)
                Logger.Trace("Adding command: %s | %s", title, cmd)
                contextMenuItems.append((title, cmd))

        return contextMenuItems

    def __GetMembers(self, channel):
        """ Caches the inspect.getmembers(channel) method for performance
        matters

        """

        if not channel.guid in self.methodContainer:
            self.methodContainer[channel.guid] = inspect.getmembers(channel)

        return self.methodContainer[channel.guid]

    def __GetParameters(self, queryString):
        """ Extracts the actual parameters as a dictionary from the passed in
        querystring. This method takes the self.quotedPlus into account.

        Arguments:
        queryString : String - The querystring

        Returns:
        dict() of keywords and values.

        """
        result = dict()
        queryString = queryString.strip('?')
        if (queryString != ''):
            try:
                for pair in queryString.split("&"):
                    (k, v) = pair.split("=")
                    if (self.quotedPlus):
                        result[k] = urllib.unquote_plus(v)
                    else:
                        result[k] = v

                # if the channelcode was empty, it was stripped, add it again.
                if not self.keywordChannelCode in result:
                    Logger.Debug("Adding ChannelCode=None as it was missing from the dict: %s", result)
                    result[self.keywordChannelCode] = None
            except:
                Logger.Critical("Cannot determine query strings from %s", queryString, exc_info=True)
                raise

        return result
