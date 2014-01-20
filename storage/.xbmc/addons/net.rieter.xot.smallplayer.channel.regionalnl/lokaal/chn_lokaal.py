import urlparse
import datetime

import contextmenu
import mediaitem
import chn_class
from logger import Logger
from helpers.jsonhelper import JsonHelper


class Channel(chn_class.Channel):
    """

    THIS CHANNEL IS BASED ON THE PEPERZAKEN APPS FOR ANDROID

    """

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

        self.channelBitrate = 850  # : the default bitrate
        self.liveUrl = None        # : the live url if present

        # now call the override
        chn_class.Channel.__init__(self, channelInfo)

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

        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self, channelInfo)

        if self.channelCode == "rtvutrecht":
            self.noImage = "rtvutrechtimage.png"
            self.mainListUri = "http://app.rtvutrecht.nl/feeds/v400/gemist_ipad_programmas.json"
            self.baseUrl = "http://app.rtvutrecht.nl"
            self.liveUrl = "http://app.rtvutrecht.nl/feeds/v400/live_televisie.json"
            self.channelBitrate = 780

        elif self.channelCode == "rtvrijnmond":
            self.noImage = "rtvrijnmondimage.png"
            self.mainListUri = "http://www.rijnmond.nl/feeds/v400/programmas.php"
            self.baseUrl = "http://www.rijnmond.nl"
            self.liveUrl = "http://www.rijnmond.nl/feeds/v400/tv.php"
            self.channelBitrate = 900

        elif self.channelCode == "rtvdrenthe":
            self.noImage = "rtvdrentheimage.png"
            self.mainListUri = "http://m.rtvdrenthe.nl/feeds/v400/programmas.php"
            self.baseUrl = "http://www.rtvdrenthe.nl"
            self.liveUrl = "http://m.rtvdrenthe.nl/feeds/v400/tv.php"
            self.channelBitrate = 1350

        elif self.channelCode == "rtvnoord":
            self.noImage = "rtvnoordimage.png"
            self.mainListUri = "http://www.rtvnoord.nl/feeds/v400/ug_programmas.json"
            self.baseUrl = "http://www.rtvnoord.nl"
            #self.liveUrl = "http://www.rtvnoord.nl/feeds/v400/tv-live-kiezer.json"
            self.channelBitrate = 1350

        elif self.channelCode == "rtvoost":
            self.noImage = "rtvoostimage.png"
            self.mainListUri = "http://mobileapp.rtvoost.nl/v400/feeds/programmas.aspx"
            self.baseUrl = "http://mobileapp.rtvoost.nl"
            self.liveUrl = "http://mobileapp.rtvoost.nl/v400/feeds/tv.aspx"
            self.channelBitrate = 1350

        elif self.channelCode == "rtvnh":
            self.noImage = "rtvnhimage.png"
            self.mainListUri = "http://www.rtvnh.nl/iphone-app/v400/programmas"
            self.baseUrl = "http://www.rtvnh.nl"
            self.liveUrl = "http://www.rtvnh.nl/iphone-app/v400/tvnh"
            self.channelBitrate = 1200

        elif self.channelCode == "omroepwest":
            self.noImage = "omroepwestimage.png"
            self.mainListUri = "http://www.omroepwest.nl/feeds/v400/programmas.php"
            self.baseUrl = "http://www.omroepwest.nl"
            # self.liveUrl = "http://www.omroepwest.nl/feeds/v400/tv.php"  -> 404 http error on streams
            self.channelBitrate = 1500

        elif self.channelCode == "omroepgelderland":
            self.noImage = "omroepgelderlandimage.png"
            self.mainListUri = "http://web.omroepgelderland.nl/json/v400/programmas.json"
            self.baseUrl = "http://web.omroepgelderland.nl"
            self.liveUrl = "http://web.omroepgelderland.nl/json/v400/tv_live.json"
            self.channelBitrate = 1500

        elif self.channelCode == "omroepzeeland":
            self.noImage = "omroepzeelandimage.png"
            self.mainListUri = "http://www.omroepzeeland.nl/apps/middleware/shows.php"
            self.baseUrl = "http://www.omroepzeeland.nl"
            self.liveUrl = "http://www.omroepzeeland.nl/apps/middleware/streams.php?t=tv&v=4"
            self.channelBitrate = 1500

        elif self.channelCode == "omroepbrabant":
            self.noImage = "omroepbrabantimage.png"
            self.mainListUri = "http://dr.omroepbrabant.nl/v400/UGSeries.json"
            self.baseUrl = "http://www.omroepbrabant.nl"
            self.liveUrl = "http://dr.omroepbrabant.nl/v400/tv.json"
            self.channelBitrate = 1500

        elif self.channelCode == "omropfryslan":
            self.noImage = "omropfryslanimage.png"
            self.mainListUri = ""
            self.baseUrl = "http://www.omropfryslan.nl"
            self.liveUrl = "http://www.omropfryslan.nl/feeds/v300/tv.php"
            self.channelBitrate = 1500

        else:
            raise NotImplementedError("Channelcode '%s' not implemented" % (self.channelCode, ))

        self.onUpDownUpdateEnabled = True
        self.contextMenuItems = []
        self.contextMenuItems.append(
            contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True,
                                        plugin=True))

        self.episodeItemJson = ()
        self.videoItemJson = ("items", )

        return True

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

        Logger.Trace("Overriding ParseMainList")

        if self.mainListUri:
            if returnData:
                (items, data) = chn_class.Channel.ParseMainList(self, returnData)
            else:
                items = chn_class.Channel.ParseMainList(self, returnData)
        else:
            items = []
            data = ""
            Logger.Info("No mainlist URL for %s", self.channelName)

        Logger.Trace(self.liveUrl)
        if self.liveUrl:
            Logger.Debug("Adding live item")
            liveItem = mediaitem.MediaItem("\aLive TV", self.liveUrl)
            liveItem.icon = self.icon
            liveItem.thumb = self.noImage
            items.append(liveItem)

        if returnData:
            #noinspection PyUnboundLocalVariable
            return items, data
        else:
            return items

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

        items = []

        Logger.Info("Performing Pre-Processing")

        # we basically will check for live channels
        jsonData = JsonHelper(data)
        liveStreams = jsonData.GetValue()

        Logger.Trace(liveStreams)
        if "videos" in liveStreams:
            Logger.Debug("Multiple streams found")
            liveStreams = liveStreams["videos"]
        else:
            Logger.Debug("Single streams found")
            liveStreams = (liveStreams, )

        for streams in liveStreams:
            Logger.Debug("Adding live stream")
            title = streams.get('name') or "%s - Live TV" % (self.channelName, )
            liveItem = mediaitem.MediaItem(title, self.liveUrl)
            liveItem.type = 'video'
            liveItem.complete = True
            liveItem.icon = self.icon
            liveItem.thumb = self.noImage
            part = liveItem.CreateNewEmptyMediaPart()
            for stream in streams:
                bitrate = None
                if stream == "androidLink":
                    bitrate = 250
                elif stream == "ipadLink":
                    bitrate = 1000
                elif stream == "iphoneLink":
                    bitrate = 250
                elif stream == "tabletLink":
                    bitrate = 300
                #elif stream == "windowsLink":
                #    bitrate = 1200
                elif stream == "name":
                    pass
                else:
                    Logger.Warning("No url found for type '%s'", stream)

                if bitrate:
                    url = streams[stream]
                    part.AppendMediaStream(url, bitrate)
            items.append(liveItem)

        Logger.Debug("Pre-Processing finished")
        return data, items

    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item.
        """
        Logger.Trace(resultSet)
        title = resultSet.get("title")

        if not title:
            return None

        if title.islower():
            title = "%s%s" % (title[0].upper(), title[1:])

        link = resultSet.get("feedLink")
        if not link.startswith("http"):
            link = urlparse.urljoin(self.baseUrl, link)

        item = mediaitem.MediaItem(title, link)
        item.icon = self.icon
        item.thumb = self.noImage
        item.complete = True
        return item

    def CreateVideoItem(self, resultSet):
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

        Logger.Trace(resultSet)

        mediaLink = resultSet.get("ipadLink")
        title = resultSet.get("title")

        # it seems overkill, but not all items have a contentLink and of we set
        # the url to self.baseUrl it will be a duplicate item if the titles are
        # equal
        url = resultSet.get("contentLink") or mediaLink or self.baseUrl
        if not url.startswith("http"):
            url = urlparse.urljoin(self.baseUrl, url)

        item = mediaitem.MediaItem(title, url)
        item.thumb = self.noImage

        if mediaLink:
            item.AppendSingleStream(mediaLink, self.channelBitrate)

        # get the thumbs from multiple locations
        thumbUrls = resultSet.get("images", None)
        thumbUrl = None
        if thumbUrls:
            thumbUrl = \
                thumbUrls[0].get("fullScreenLink", None) or \
                thumbUrls[0].get("previewLink", None) or \
                resultSet.get("imageLink", None)

        if thumbUrl and not thumbUrl.startswith("http"):
            thumbUrl = urlparse.urljoin(self.baseUrl, thumbUrl)

        if thumbUrl:
            item.thumbUrl = thumbUrl

        item.icon = self.icon
        item.type = 'video'

        item.description = resultSet.get("text")
        #if item.description:
        #    item.description = item.description.replace("<br />", "\n")

        posix = resultSet.get("timestamp", None)
        if posix:
            broadcastDate = datetime.datetime.fromtimestamp(int(posix))
            item.SetDate(broadcastDate.year,
                         broadcastDate.month,
                         broadcastDate.day,
                         broadcastDate.hour,
                         broadcastDate.minute,
                         broadcastDate.second)

        item.complete = True
        return item

    def CtMnDownloadItem(self, item):
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

        item = self.DownloadVideoItem(item)
        return item
