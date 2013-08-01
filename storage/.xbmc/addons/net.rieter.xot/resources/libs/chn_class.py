#==============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================

#===============================================================================
# Import the default modules
#===============================================================================
import urlparse
import os
from datetime import datetime
# import time

import xbmc
# import xbmcplugin

import mediaitem
import addonsettings
import settings
import guicontroller

from regexer import Regexer
from xbmcwrapper import XbmcWrapper
from config import Config
from initializer import Initializer
# from environments import Environments
from helpers import htmlentityhelper
from helpers import stopwatch
from helpers import encodinghelper
from helpers.jsonhelper import JsonHelper
from helpers.languagehelper import LanguageHelper
from helpers.statistics import Statistics

from logger import Logger
from urihandler import UriHandler


class Channel:
    """
    main class from which all channels inherit
    """

    #==============================================================================
    def __init__(self, channelInfo):
        """Initialisation of the class.

        WindowXMLDialog(self, xmlFilename, scriptPath[, defaultSkin, defaultRes]) -- Create a new WindowXMLDialog script.

        xmlFilename     : string - the name of the xml file to look for.
        scriptPath      : string - path to script. used to fallback to if the xml doesn't exist in the current skin. (eg os.getcwd())
        defaultSkin     : [opt] string - name of the folder in the skins path to look in for the xml. (default='Default')
        defaultRes      : [opt] string - default skins resolution. (default='720p')

        *Note, skin folder structure is eg(resources/skins/Default/720p)

        All class variables should be instantiated here and this method should not
        be overridden by any derived classes.

        """

        self.mainListItems = []
        self.parentItem = None

        # set default icons
        self.folderIcon = "xot_DefaultFolder.png"
        self.folderIconHQ = "xot_DefaultFolderHQ.png"
        self.appendIcon = "xot_DefaultAppend.png"

        self.initialItem = None  # uri that is used for the episodeList. NOT mainListUri
        self.proxy = None
        self.loggedOn = False

        # initialise user defined variables
        self.InitialiseVariables(channelInfo)

        # update image file names: point to local folder if not present in skin
        self.icon = self.GetImageLocation(self.icon)
        self.iconLarge = self.GetImageLocation(self.iconLarge)
        self.folderIcon = self.GetImageLocation(self.folderIcon)
        self.folderIconHQ = self.GetImageLocation(self.folderIconHQ)
        self.appendIcon = self.GetImageLocation(self.appendIcon)
        self.noImage = self.GetImageLocation(self.noImage)
        self.backgroundImage = self.GetImageLocation(self.backgroundImage)
        self.backgroundImage16x9 = self.GetImageLocation(self.backgroundImage16x9)

        # plugin stuff
        self.pluginMode = False

    #===============================================================================
    # define class variables
    #===============================================================================
    def InitialiseVariables(self, channelInfo):
        """Used for the initialisation of user defined parameters.

        All should be present, but can be adjusted. If overridden by derived class
        first call chn_class.Channel.InitialiseVariables(self, channelInfo) to make sure all
        variables are initialised.

        Arguments:
        channelInfo : ChannelInfo - The channel meta data.

        Returns:
        True if OK

        """

        Logger.Trace("Starting IntialiseVariables from chn_class.py")

        # Info from the ChannelInfo
        self.guid = channelInfo.guid
        self.icon = channelInfo.icon
        self.iconLarge = channelInfo.iconLarge
        self.channelName = channelInfo.channelName
        self.channelCode = channelInfo.channelCode
        self.channelDescription = channelInfo.channelDescription
        self.moduleName = channelInfo.moduleName
        self.compatiblePlatforms = channelInfo.compatiblePlatforms
        self.sortOrder = channelInfo.sortOrder
        self.language = channelInfo.language

        self.noImage = ""
        self.backgroundImage = ""                           # : if not specified, the one defined in the skin is used
        self.backgroundImage16x9 = ""                       # : if not specified, the one defined in the skin is used

        self.buttonID = 0
        self.onUpDownUpdateEnabled = True
        self.contextMenuItems = []

        self.mainListUri = ""
        self.baseUrl = ""
        self.playerUrl = ""
        self.defaultPlayer = 'defaultplayer'                # : (defaultplayer, dvdplayer, mplayer)

        self.passWord = ""
        self.userName = ""
        self.logonUrl = ""
        self.requiresLogon = False

        self.asxAsfRegex = '<[^\s]*REF href[^"]+"([^"]+)"'  # : default regex for parsing ASX/ASF files

        self.episodeItemRegex = ''                          # : used for the ParseMainList
        self.episodeItemJson = None                         # : used for the ParseMainList
        self.videoItemRegex = ''                            # : used for the ParseMainList
        self.videoItemJson = None                           # : used for the ParseMainList
        self.folderItemRegex = ''                           # : used for the CreateFolderItem
        self.folderItemJson = None                          # : used for the CreateFolderItem
        self.mediaUrlRegex = ''                             # : used for the UpdateVideoItem
        self.mediaUrlJson = None                            # : used for the UpdateVideoItem

        """
            The ProcessPageNavigation method will parse the current data using the pageNavigationRegex. It will
            create a pageItem using the CreatePageItem method. If no CreatePageItem method is in the channel,
            a default one will be created with the number present in the resultset location specified in the
            pageNavigationRegexIndex and the url from the combined resultset. If that url does not contain http://
            the self.baseUrl will be added.
        """
        self.pageNavigationIndicationRegex = ''
        self.pageNavigationRegex = ''
        self.pageNavigationJson = None
        self.pageNavigationRegexIndex = 0
        self.pageNavigationJsonIndex = None

        self.episodeSort = True
        self.swfUrl = ""

        #==========================================================================
        # non standard items

        return True

    #===============================================================================
    #    Init for plugin and script
    #===============================================================================
    def InitPlugin(self):
        """Initializes the channel for plugin use

        Returns:
        List of MediaItems that should be displayed

        This method is called for each Plugin call and can be used to do some
        channel initialisation. Make sure to set the self.pluginMode = True
        in this methode if overridden.

        """

        self.pluginMode = True

        self.loggedOn = self.LogOn(self.userName, self.passWord)

        if not self.loggedOn:
            Logger.Error('Not logged on...exiting')
            return False

        # set HQ icons
        self.icon = self.iconLarge
        self.folderIcon = self.folderIconHQ

        return self.InitEpisodeList()

    #==============================================================================
    def InitScript(self):
        """Initializes the channel for script use

        Returns:
        The value of self.InitEpisodeList()

        """

        Logger.Debug("LogonCheck")

        self.pluginMode = False

        self.loggedOn = self.LogOn(self.userName, self.passWord)

        if not self.loggedOn:
            Logger.Error('Not logged on...exiting')
            return False

        return self.InitEpisodeList()

    def InitEpisodeList(self):
        """Init method that can be used to do stuff when the channel opens a new episode list

        Returns:
        True if the method completed without errors

        """
        return True

    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def CtMnAddToFavorites(self, item):
        """Add to favorites.

        Arguments:
        item : MediaItem - the item to add to the favorites.

        """

        if item.type != 'folder':
            Logger.Error("AddToFavorites :: Can only add folder items. Got %s-item", item.type)
            return

        settings.AddToFavorites(item, self)
        return

    def CtMnSettings(self, item):  # @UnusedVariable
        """Shows the Addon settings

        Arguments:
        item : MediaItem - the currently selected item

        The <item> argument is not really used here, but is just here for compatibility
        in showing the contextmenu.

        """

        addonsettings.AddonSettings().ShowSettings()
        pass

    def CtMnRefresh(self, item):
        """ refreshes an item's MediaParts

        Arguments:
        item : MediaItem - the items to refresh.

        CAUTION: only use this method if the UpdateVideoItem fetches the MediaParts

        """

        # reset the media item parts, as they will be reloaded.
        if item.HasMediaItemParts():
            item.MediaItemParts = []

        return self.UpdateVideoItem(item)
        pass

    #==============================================================================
    # Custom Methodes, in chronological order
    #==============================================================================
    def ParseMainList(self, returnData=False):
        """Parses the mainlist of the channel and returns a list of MediaItems

        This method creates a list of MediaItems that represent all the different
        programs that are available in the online source. The list is used to fill
        the ProgWindow.

        Keyword parameters:
        returnData : [opt] boolean - If set to true, it will return the retrieved
                                     data as well

        Returns a list of MediaItems that were retrieved.

        """

        items = []
        if len(self.mainListItems) > 1:
            if self.episodeSort:
                # just resort again
                self.mainListItems.sort()

            if returnData:
                return (self.mainListItems, "")
            else:
                return self.mainListItems

        data = UriHandler.Open(self.mainListUri, proxy=self.proxy)
        Logger.Trace("Retrieved %s chars as mainlist data", len(data))

        # first process folder items.
        watch = stopwatch.StopWatch('Mainlist', Logger.Instance())

        episodeItems = []
        if not self.episodeItemRegex == "" and not self.episodeItemRegex is None:
            Logger.Trace("Using Regexer for episodes")
            episodeItems = Regexer.DoRegex(self.episodeItemRegex, data)
            watch.Lap("Mainlist Regex complete")

        elif not self.episodeItemJson is None:
            Logger.Trace("Using JsonHelper for episodes")
            json = JsonHelper(data, Logger.Instance())
            episodeItems = json.GetValue(*self.episodeItemJson)
            watch.Lap("Mainlist Json complete")

        Logger.Debug('Starting CreateEpisodeItem for %s items', len(episodeItems))
        for episodeItem in episodeItems:
            Logger.Trace('Starting CreateEpisodeItem for %s', self.channelName)
            tmpItem = self.CreateEpisodeItem(episodeItem)
            # catch the return of None
            if tmpItem:
                items.append(tmpItem)

        # Filter out the duplicates using the HASH power of a set
        items = list(set(items))

        watch.Lap("MediaItem creation complete")

        # sort by name
        if self.episodeSort:
            items.sort()
            watch.Stop()
        else:
            watch.Stop()

        self.mainListItems = items

        if returnData:
            return (items, data)
        else:
            return items

    #==============================================================================
    def SearchSite(self, url=None):
        """Creates an list of items by searching the site

        Keyword Arguments:
        url : String - Url to use to search with a %s for the search parameters

        Returns:
        A list of MediaItems that should be displayed.

        This method is called when the URL of an item is "searchSite". The channel
        calling this should implement the search functionality. This could also include
        showing of an input keyboard and following actions.

        The %s the url will be replaced with an URL encoded representation of the
        text to search for.

        """

        items = []
        if url is None:
            item = mediaitem.MediaItem("Search Not Implented", "", type='video')
            item.icon = self.icon
            items.append(item)
        else:
            items = []
            keyboard = xbmc.Keyboard('')
            keyboard.doModal()
            if (keyboard.isConfirmed()):
                needle = keyboard.getText()
                Logger.Debug("Searching for '%s'", needle)
                if len(needle) > 0:
                    # convert to HTML
                    needle = htmlentityhelper.HtmlEntityHelper.UrlEncode(needle)
                    searchUrl = url % (needle)
                    temp = mediaitem.MediaItem("Search", searchUrl)
                    return self.ProcessFolderList(temp)

        return items

    #==============================================================================
    def SetRootItem(self, item):
        """Sets the intialItem that is used to fill the channel.

        Arguments:
        item : MediaItem - the item to set as the initial item.

        The <item> is used to load the URL and then process the first folder list
        to display.

        """

        self.initialItem = item
        return

    #==============================================================================
    def GetRootItem(self):
        """returns the first item for the selected program

        Returns:
        The root MediaItem of the channel.

        This methode returns the set self.intialItem and returns that item
        to the caller.

        """

        # the root item
        rootItem = self.initialItem

        # get the image
        if self.initialItem.thumb == "":
            if self.initialItem.thumbUrl == "":
                rootItem.thumb = self.noImage
            else:
                rootItem.thumb = self.CacheThumb(self.initialItem.thumbUrl)

        # get the items
        rootItem.items = self.ProcessFolderList(rootItem)
        return rootItem

    #==============================================================================
    def CreateEpisodeItem(self, resultSet):  # @UnusedVariable
        """Creates a new MediaItem for an episode

        Arguments:
        resultSet : list[string] - the resultSet of the self.episodeItemRegex

        Returns:
        A new MediaItem of type 'folder'

        This method creates a new MediaItem from the Regular Expression or Json
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        """

        # dummy class
        item = mediaitem.MediaItem("No CreateEpisode Implented!", "")
        item.complete = True
        return item

    #==============================================================================
    def PreProcessFolderList(self, data):
        """Performs pre-process actions for data processing/

        Arguments:
        data : string - the retrieve data that was loaded for the current item and URL.

        Returns:
        A tuple of the data and a list of MediaItems that were generated.


        Accepts an data from the ProcessFolderList method, BEFORE the items are
        processed. Allows setting of parameters (like title etc) for the channel.
        Inside this method the <data> could be changed and additional items can
        be created.

        The return values should always be instantiated in at least ("", []).

        """

        Logger.Info("Performing Pre-Processing")
        items = []
        Logger.Debug("Pre-Processing finished")
        return (data, items)

    #==============================================================================
    def ProcessFolderList(self, item=None):
        """Process the selected item and get's it's child items.

        Arguments:
        item : [opt] MediaItem - the selected item

        Returns:
        A list of MediaItems that form the childeren of the <item>.

        Accepts an <item> and returns a list of MediaListems with at least name & url
        set. The following actions are done:

        * loading of the data from the item.url
        * perform pre-processing actions
        * creates a sorted list folder items using self.folderItemRegex and self.CreateFolderItem
        * creates a sorted list of media items using self.videoItemRegex and self.CreateVideoItem
        * create page items using self.ProcessPageNavigation

        if item = None then an empty list is returned.

        """

        if item == None:
            Logger.Warning("ProcessFolderList :: No item was specified. Returning an empty list")
            return []

        if len(item.items) > 0 and not item.url == "searchSite":
            Logger.Debug("ProcessFolderList :: %s Items already available. returning them.", len(item.items))
            return item.items

        self.parentItem = item

        try:
            watch = stopwatch.StopWatch("ProcessFolderList", Logger.Instance())
            preItems = []
            folderItems = []
            videoItems = []
            pageItems = []

            if (item.url == "searchSite"):
                Logger.Debug("Starting to search")
                return self.SearchSite()

            data = UriHandler.Open(item.url, proxy=self.proxy)

            # first of all do the Pre handler
            (data, preItems) = self.PreProcessFolderList(data)

            # then process folder items.
            folders = []
            folderItems = []
            if not self.folderItemRegex == '' and not self.folderItemRegex is None:
                folders = Regexer.DoRegex(self.folderItemRegex, data)
                watch.Lap("Folders Regex complete")

            elif not self.folderItemJson is None:
                folderJson = JsonHelper(data, Logger.Instance())
                folders = folderJson.GetValue(*self.folderItemJson)
                watch.Lap("Folders Json complete")

            Logger.Trace('Starting CreateFolderItem for %s items', len(folders))
            for folder in folders:
                Logger.Trace('Starting CreateFolderItem for %s', self.channelName)
                fItem = self.CreateFolderItem(folder)
                if fItem:
                    folderItems.append(fItem)

            # Filter out the duplicates using the HASH power of a set
            folderItems = list(set(folderItems))

            # sort by name
            watch.Lap("Folders Loaded")
            folderItems.sort()
            watch.Lap("Folders Sorted")

            # now process video items
            videos = []
            videoItems = []
            if not self.videoItemRegex == '' and not self.videoItemRegex is None:
                videos = Regexer.DoRegex(self.videoItemRegex, data)
                watch.Lap("Video Regex complete")

            elif not self.videoItemJson is None:
                videoJson = JsonHelper(data, Logger.Instance())
                videos = videoJson.GetValue(*self.videoItemJson)
                watch.Lap("Video Json complete")

            Logger.Debug('Starting CreateVideoItem for %s items', len(videos))
            for video in videos:
                Logger.Trace('Starting CreateVideoItem for %s', self.channelName)
                vItem = self.CreateVideoItem(video)
                if vItem:
                    videoItems.append(vItem)

            # Filter out the duplicates using the HASH power of a set
            videoItems = list(set(videoItems))

            watch.Lap("Video's Loaded")
            videoItems.sort()
            watch.Lap("Video's Sorted")

            # now process page navigation if a pageNavigationIndication is present
            pageItems = self.ProcessPageNavigation(data)
            watch.Stop()
            return preItems + folderItems + videoItems + pageItems
        except:
            Logger.Critical("Error processing folder", exc_info=True)
            return []

    #==============================================================================
    def ProcessPageNavigation(self, data):
        """Generates a list of pageNavigation items.

        Arguments:
        data : string - the retrieve data that was loaded for the current item and URL.

        Returns:
        A list of MediaItems of type 'page'

        Parses the <data> using the self.pageNavigationRegex and then calls the
        self.CreatePageItem method for each result to create a page item. The
        list of those items is returned.

        """

        Logger.Debug("Starting ProcessPageNavigation")

        pageItems = []
        pages = []

        # try the regex on the current data
        if not self.pageNavigationRegex == "" and not self.pageNavigationRegex is None:
            pages = Regexer.DoRegex(self.pageNavigationRegex, data)

        elif not self.pageNavigationJson is None:
            pageJson = JsonHelper(data, logger=Logger.Instance())
            pages = pageJson.GetValue(*self.pageNavigationJson)

        if len(pages) == 0:
            Logger.Debug("No pages found.")
            return pageItems

        Logger.Debug('Starting CreatePageItem for %s items', len(pages))
        for page in pages:
            Logger.Trace('Starting CreatePageItem for %s', self.channelName)
            item = self.CreatePageItem(page)
            if item:
                pageItems.append(item)

        # Filter out the duplicates using the HASH power of a set
        pageItems = list(set(pageItems))

        # Logger.Debug(pageItems)
        return pageItems

    #==============================================================================
    def CreatePageItem(self, resultSet):
        """Creates a MediaItem of type 'page' using the resultSet from the regex.

        Arguments:
        resultSet : tuple(string) - the resultSet of the self.pageNavigationRegex

        Returns:
        A new MediaItem of type 'page'

        This method creates a new MediaItem from the Regular Expression or Json
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        """

        Logger.Debug("Starting CreatePageItem")
        total = ''

        for result in resultSet:
            total = "%s%s" % (total, result)

        total = htmlentityhelper.HtmlEntityHelper.StripAmp(total)

        if not self.pageNavigationRegexIndex == '':
            item = mediaitem.MediaItem(resultSet[self.pageNavigationRegexIndex], urlparse.urljoin(self.baseUrl, total))
        else:
            item = mediaitem.MediaItem("0", "")

        item.type = "page"
        Logger.Debug("Created '%s' for url %s", item.name, item.url)
        return item

    #==============================================================================
    def CreateFolderItem(self, resultSet):  # @UnusedVariable
        """Creates a MediaItem of type 'folder' using the resultSet from the regex.

        Arguments:
        resultSet : tuple(strig) - the resultSet of the self.folderItemRegex

        Returns:
        A new MediaItem of type 'folder'

        This method creates a new MediaItem from the Regular Expression or Json
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        """

        item = mediaitem.MediaItem("No CreateFolderItem Implented!", "")
        item.complete = True
        return item

    #=============================================================================
    def CreateVideoItem(self, resultSet):  # @UnusedVariable
        """Creates a MediaItem of type 'video' using the resultSet from the regex.

        Arguments:
        resultSet : tuple (string) - the resultSet of the self.videoItemRegex

        Returns:
        A new MediaItem of type 'video' or 'audio' (despite the method's name)

        This method creates a new MediaItem from the Regular Expression or Json
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        If the item is completely processed an no further data needs to be fetched
        the self.complete property should be set to True. If not set to True, the
        self.UpdateVideoItem method is called if the item is focussed or selected
        for playback.

        """

        item = mediaitem.MediaItem("No CreateVideoItem Implented!", "")
        item.thumb = self.noImage
        item.icon = self.icon
        item.complete = True
        return item

    #=============================================================================
    def UpdateVideoItem(self, item):
        """Updates an existing MediaItem with more data.

        Arguments:
        item : MediaItem - the MediaItem that needs to be updated

        Returns:
        The original item with more data added to it's properties.

        Used to update none complete MediaItems (self.complete = False). This
        could include opening the item's URL to fetch more data and then process that
        data or retrieve it's real media-URL.

        The method should at least:
        * cache the thumbnail to disk (use self.noImage if no thumb is available).
        * set at least one MediaItemPart with a single MediaStream.
        * set self.complete = True.

        if the returned item does not have a MediaItemPart then the self.complete flag
        will automatically be set back to False.

        """

        Logger.Debug('Starting UpdateVideoItem for %s (%s)', item.name, self.channelName)

        _data = UriHandler.Open(item.url, pb=False, proxy=self.proxy)

        url = Regexer.DoRegex(self.mediaUrlRegex, _data)[-1]
        part = mediaitem.MediaItemPart(item.name, url)
        item.MediaItemParts.append(part)

        Logger.Info('finishing UpdateVideoItem. MediaItems are %s', item)

        if item.thumbUrl and (item.thumb == self.noImage or not item.thumb):
            # no thumb set yet
            Logger.Debug("Updating thumb from %s to cached version of %s", item.thumb, item.thumbUrl)
            item.thumb = self.CacheThumb(item.thumbUrl)
        elif not item.thumb and self.noImage:
            # no thumb was set yet and no url
            Logger.Debug("Setting thumb to %s", item.thumb, item.thumbUrl)
            item.thumb = self.noImage

        if not item.HasMediaItemParts():
            item.SetErrorState("Update did not result in streams")
        else:
            item.complete = True
        return item

    #==============================================================================
    def DownloadVideoItem(self, item):
        """Downloads an existing MediaItem with more data.

        Arguments:
        item : MediaItem - the MediaItem that should be downloaded.

        Returns:
        The original item with more data added to it's properties.

        Used to download an <item>. If the item is not complete, the self.UpdateVideoItem
        method is called to update the item. The method downloads only the MediaStream
        with the bitrate that was set in the addon settings.

        After downloading the self.downloaded property is set.

        """

        if not item.IsPlayable():
            Logger.Error("Cannot download a folder item.")
            return item

        if item.IsPlayable():
            if item.complete == False:
                Logger.Info("Fetching MediaUrl for PlayableItem[%s]", item.type)
                item = self.UpdateVideoItem(item)

            if item.complete == False or not item.HasMediaItemParts():
                item.SetErrorState("Update did not result in streams")
                Logger.Error("Cannot download incomplete item or item without MediaItemParts")
                return item

            i = 1
            bitrate = self.GetSettingsQuality()
            for mediaItemPart in item.MediaItemParts:
                Logger.Info("Trying to download %s", mediaItemPart)
                stream = mediaItemPart.GetMediaStreamForBitrate(bitrate)
                downloadUrl = stream.Url
                extension = UriHandler.GetExtensionFromUrl(downloadUrl)
                if (len(item.MediaItemParts) > 1):
                    saveFileName = "%s-Part_%s.%s" % (item.name, i, extension)
                else:
                    saveFileName = "%s.%s" % (item.name, extension)
                Logger.Debug(saveFileName)

                agent = mediaItemPart.UserAgent
                UriHandler.Download(downloadUrl, saveFileName, userAgent=agent)
                i = i + 1

            item.downloaded = True

        return item
    #==============================================================================
    def LogOn(self, *args):
        """Logs on to a website, using an url.

        Arguments:
        userName : string - the username to use to log on
        passWord : string - the password to use to log on

        Returns:
        True if successful.

        First checks if the channel requires log on. If so and it's not already
        logged on, it should handle the log on. That part should be implemented
        by the specific channel.

        More arguments can be passed on, but must be handled by custom code.

        After a successful log on the self.loggedOn property is set to True and
        True is returned.

        """

        if not self.requiresLogon:
            Logger.Debug("No login required of %s", self.channelName)
            return True

        if self.loggedOn:
            Logger.Info("Already logged in")
            return True

        _rtrn = False
        _passWord = args["userName"]
        _userName = args["passWord"]
        return _rtrn

    #==============================================================================
    def PlayVideoItem(self, item, player="", bitrate=None, pluginMode=False):
        """Starts the playback of the <item> with the specific <bitrate> in the selected <player>.

        Arguments:
        item    : MediaItem - The item to start playing

        Keyword Arguments:
        player  : [opt] string - The requested player ('dvdplayer', 'mplayer' or '' for the default one)
        bitrate : [opt] integer - The requested bitrate in Kbps or None.
        plugin  : [opt] boolean - Indication whether we are in plugin mode. If True, there
                                  will not actually be playback, rather a tuple with info.

        Returns:
        The updated <item>.

        Starts the playback of the selected MediaItem <item>. Before playback is started
        the item is check for completion (item.complete), if not completed, the self.UpdateVideoItem
        method is called to update the item.

        After updating the requested bitrate playlist is selected, if bitrate was set to None
        the bitrate is retrieved from the addon settings. The playlist is then played using the
        requested player.

        """

        try:
            if player == "":
                player = self.defaultPlayer

            if bitrate == None:
                # use the bitrate from the xbmc settings if bitrate was not specified and the item is MultiBitrate
                bitrate = self.GetSettingsQuality()

            # should we download items?
            Logger.Debug("Checking for not streamable parts")
            # We need to substract the download time from processing time
            downloadStart = datetime.now()
            for part in item.MediaItemParts:
                if not part.CanStream:
                    stream = part.GetMediaStreamForBitrate(bitrate)
                    if not stream.Downloaded:
                        Logger.Debug("Downloading not streamable part: %s\nDownloading Stream: %s", part, stream)

                        # we need a unique filename
                        fileName = encodinghelper.EncodingHelper.EncodeMD5(stream.Url)
                        extension = UriHandler.GetExtensionFromUrl(stream.Url)

                        # now we force the busy dialog to close, else we cannot cancel the download
                        # setResolved will not work.
                        xbmc.executebuiltin("Dialog.Close(busydialog)")

                        cacheFile = UriHandler.Download(stream.Url, "xot.%s.%skbps-%s.%s" % (fileName, stream.Bitrate, item.name, extension), self.GetDefaultCachePath(), proxy=self.proxy, userAgent=part.UserAgent)
                        if cacheFile == "":
                            Logger.Error("Cannot download stream %s \nFrom: %s", stream, part)
                            return

                        if cacheFile.startswith("\\\\"):
                            cacheFile = cacheFile.replace("\\", "/")
                            stream.Url = "file:///%s" % (cacheFile)
                        else:
                            stream.Url = "file://%s" % (cacheFile,)
                        # stream.Url = cacheFile
                        stream.Downloaded = True

            # We need to substract the download time from processing time
            downloadTime = datetime.now() - downloadStart
            downloadDuration = 1000 * downloadTime.seconds + downloadTime.microseconds / 1000

            # Set item as downloaded
            item.downloaded = True

            # now we can play
            Logger.Info("Starting Video Playback using the %s", player)

            # get the playlist
            (playList, srt) = item.GetXBMCPlayList(bitrate, updateItemUrls=pluginMode)

            # determine the player
            if player == "dvdplayer":
                Logger.Debug("Playing using DVDPlayer")
                xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_DVDPLAYER)
            elif player == "mplayer":
                Logger.Debug("Playing using Mplayer")
                xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_MPLAYER)
            else:
                if item.type == "audio":
                    Logger.Debug("Playing using default audio player")
                    xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_PAPLAYER)
                else:
                    Logger.Debug("Playing using default video player")
                    xbmcPlayer = xbmc.Player(xbmc.PLAYER_CORE_AUTO)

            if pluginMode:
                # call for statistics with timing
                Statistics.RegisterPlayback(self, Initializer.StartTime, -downloadDuration)

                # if the item urls have been updated, don't start playback, but return
                return (playList, srt, xbmcPlayer)
            # no reporting for script as it's harder to determine the startime as
            # it should also include the update time and that could have already happened
            #else:
            #    # call for statistics
            #    Statistics.RegisterPlayback(self)

            # and play
            xbmcPlayer.play(playList)

            # any subtitles available
            showSubs = addonsettings.AddonSettings().UseSubtitle()
            if srt and (srt != ""):
                Logger.Info("Adding subtitle: %s and setting showSubtitles to %s", srt, showSubs)
                XbmcWrapper.WaitForPlayerToStart(xbmcPlayer, 10, Logger.Instance())
                xbmcPlayer.setSubtitles(srt)
                xbmcPlayer.showSubtitles(showSubs)
        except:
            XbmcWrapper.ShowNotification(LanguageHelper.GetLocalizedString(LanguageHelper.ErrorId), LanguageHelper.GetLocalizedString(LanguageHelper.NoPlaybackId), XbmcWrapper.Error)
            Logger.Critical("Could not playback the url", exc_info=True)

    def GetDefaultCachePath(self):
        """ returns the default cache path for this channel

        Could be overridden by a channel.

        """

        return Config.cacheDir

    #==============================================================================
    def GetVerifiableVideoUrl(self, url):
        """Creates an RTMP(E) url that can be verified using an SWF URL.

        Arguments:
        url : string - the URL that should be made verifiable.

        Returns:
        A new URL that includes the self.swfUrl in the form of "url --swfVfy|-W swfUrl".
        If self.swfUrl == "", the original URL is returned.

        """

        if self.swfUrl == "":
            return url

        # return "%s --swfVfy -W %s" % (url, self.swfUrl)
        # return "%s swfurl=%s swfvfy=true" % (url, self.swfUrl)
        return "%s swfurl=%s swfvfy=1" % (url, self.swfUrl)

    #==============================================================================
    def GetImageLocation(self, image):
        """returns the path for a specific image name.

        Arguments:
        image : string - the filename of the requested argument.

        Returns:
        The full local path to the requested image.

        Calls the guiController.GetImageLocation to get the path.

        """

        return guicontroller.GuiController.GetImageLocation(image, self)

    #==============================================================================
    def GetSettingsQuality(self):
        """Gets the prefered playback quality from the Addon settings.

        Returns:
        Integer indicating the quality of playback that is configured:
        * 0 -- low quality
        * 1 -- medium quality
        * 2 -- high quality

        This could also be done directly using the settings.AddonSettings() but
        it's here for convenience.

        """

        return addonsettings.AddonSettings().GetMaxStreamBitrate()

    #===============================================================================
    def GetBackgroundImage(self, resolution43=True):
        """Returns the background image for this channel for the requested screensize.

        Keyword Arguments:
        resolution43 : boolean - Indicates whether to return the 4x3 background or not (16x9).

        Returns:
        The path to the requested background, or an empty string if the channel does not
        have a background configured.

        The path also takes into consideration that a possible image is available in the
        XBMC sckin folder. Therefore it uses the GetImageLocation methode in the
        chn_class.__init__() methode.

        """

        if resolution43:
            background = self.backgroundImage
        else:
            background = self.backgroundImage16x9

        if (background == ""):
            background = addonsettings.AddonSettings().BackgroundImageProgram()

        return background

    #===============================================================================
    def CacheThumb(self, remoteImage):
        """Caches an image to disk.

        Arguments:
        remoteImage : string - the URL of the remote thumb.

        Returns:
        The local path of the cached image. If not remote image was specified
        it will return the path of the self.noImage image file. Therefore
        it uses the GetImageLocation methode in the chn_class.__init__() methode.

        In order to make everything appear OK while loading. Set the default thumb
        in the MediaItems to self.noImage file.

        """

        Logger.Trace("Going to cache %s", remoteImage)

        if self.pluginMode:
            Logger.Debug("For plugin-mode we do not cache thumbs, that's XBMC's work.")
            return remoteImage

        if remoteImage == "":
            return self.noImage

        if remoteImage.find(":") < 2:
            return remoteImage

        Logger.Debug("Caching url=%s", remoteImage)
        thumb = ""

        # get image
        localImageName = encodinghelper.EncodingHelper.EncodeMD5(remoteImage)
        # localImageName = Regexer.DoRegex('/([^/]*)$', remoteImage)[-1]
        # correct for fatx
        localImageName = UriHandler.CorrectFileName(localImageName)

        localCompletePath = os.path.join(Config.cacheDir, localImageName)
        try:
            if os.path.exists(localCompletePath):  # check cache
                    thumb = localCompletePath
            else:  # save them in cache folder
                    Logger.Debug("Downloading thumb. Filename=%s", localImageName)
                    thumb = UriHandler.Download(remoteImage, localImageName, folder=Config.cacheDir, pb=False)
                    if thumb == "":
                        return self.noImage
        except:
            Logger.Error("Error opening thumbfile!", exc_info=True)
            return self.noImage

        return thumb

    #===============================================================================
    # Default methods
    #===============================================================================
    def __str__(self):
        """Returns a string representation of the current channel."""

        if self.channelCode is None:
            return "%s [%s, %s] (Order: %s)" % (self.channelName, self.language, self.guid, self.sortOrder)
        else:
            return "%s (%s) [%s, %s] (Order: %s)" % (self.channelName, self.channelCode, self.language, self.guid, self.sortOrder)

    #==============================================================================
    def __eq__(self, other):
        """Compares to channel objects for equality

        Arguments:
        other : Channel - the other channel to compare to

        The comparison is based only on the self.guid of the channels.

        """

        if other == None:
            return False

        return self.guid == other.guid

    def __cmp__(self, other):
        """Compares to channels

        Arguments:
        other : Channel - the other channel to compare to

        Returns:
        The return value is negative if self < other, zero if self == other and strictly positive if self > other

        """

        if other == None:
            return 1

        compVal = cmp(self.sortOrder, other.sortOrder)
        if compVal == 0:
            compVal = cmp(self.channelName, self.channelName)

        return compVal

    #==============================================================================
    # Default ContextMenu functions
    #==============================================================================
    def CtMnPlayMplayer(self, item):
        """Default ContextMenuHandling for playback of an MediaItem via "mplayer".

        Arguments:
        item : MediaItem - the MediaItem to playback.

        Returns the updated MediaItem after calling self.PlayVideoItem. The player
        it defaults to is "mplayer".

        """

        return self.PlayVideoItem(item, "mplayer")

    def CtMnPlayDVDPlayer(self, item):
        """Default ContextMenuHandling for playback of an MediaItem via "dvdplayer".

        Arguments:
        item : MediaItem - the MediaItem to playback.

        Returns the updated MediaItem after calling self.PlayVideoItem. The player
        it defaults to is "dvdplayer".

        """

        return self.PlayVideoItem(item, "dvdplayer")
