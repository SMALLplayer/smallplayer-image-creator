import xml.dom.minidom
import time
import cookielib

#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import chn_class

from regexer import Regexer
from logger import Logger
from urihandler import UriHandler
from addonsettings import AddonSettings


class Channel(chn_class.Channel):
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

        self.mainListUri = "http://www.rtl.nl/system/xl/feed/a-z.xml"
        self.mainListUri = "http://www.rtl.nl/system/xl/feed/a-z_SMOOTH.xml"
        self.baseUrl = "http://www.rtl.nl"
        self.noImage = "rtlimage.png"

        # self.backgroundImage = "background-rtl.png"
        # self.backgroundImage16x9 = "background-rtl-16x9.png"
        self.requiresLogon = False

        self.episodeItemRegex = "<abstract key='([^']+)'>\W*<station>([^<]+)</station>\W*(?:<[^>]+>[^>]+>\W*){2}<name>([^<]+)</name>\W*(?:<[^>]+>[^>]+>\W+){1,3}<logo-url>([^<]*)"
        self.videoItemRegex = ''
        self.folderItemRegex = ''
        # self.mediaUrlRegex = '<ref href="([^"]+_)(\d+)(K[^"]+.wmv)"[^>]*>'
        self.mediaUrlRegex = "BANDWIDTH=(\d+)\d{3}[^\n]+\W+([^\n]+.m3u8)"

        self.contextMenuItems = []
        # self.contextMenuItems.append(contextmenu.ContextMenuItem("Play lowest bitrate stream", "CtMnPlayLow", itemTypes="video", completeStatus=True))
        # self.contextMenuItems.append(contextmenu.ContextMenuItem("Play default bitrate stream", "CtMnPlayHigh", itemTypes="video", completeStatus=True))

        #==============================================================================
        # non standard items
        self.PreProcessRegex = '<ul title="([^"]*)" rel="([^"]*)videomenu.xml"'
        self.progTitle = ""
        self.videoMenu = ""

        self.seasons = dict()
        self.episodes = dict()
        self.materials = dict()
        # self.parseWvx = True

        self.iconSet = dict()
        self.largeIconSet = dict()

        for channel in ["rtl4", "rtl5", "rtl7", "rtl8"]:
            self.iconSet[channel] = self.GetImageLocation("%sicon.png" % (channel,))
            self.largeIconSet[channel] = self.GetImageLocation("%slarge.png" % (channel,))

        self.__IgnoreCookieLaw()
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

        items = chn_class.Channel.ParseMainList(self, returnData=returnData)

        # let's add the RTL-Z live stream
        rtlzLive = mediaitem.MediaItem("RTL Z Live Stream", "")
        rtlzLive.icon = self.icon
        rtlzLive.thumb = self.noImage
        rtlzLive.complete = True

        streamItem = mediaitem.MediaItem("RTL Z: Live Stream", "http://www.rtl.nl/(config=RTLXLV2,channel=rtlxl,progid=rtlz,zone=inlineplayer.rtl.nl/rtlz,ord=0)/system/video/wvx/components/financien/rtlz/miMedia/livestream/rtlz_livestream.xml/1500.wvx")
        streamItem.icon = self.icon
        streamItem.thumb = self.noImage
        streamItem.complete = True
        streamItem.type = "video"
        streamItem.AppendSingleStream("http://mss6.rtl7.nl/rtlzbroad", 1200)
        streamItem.AppendSingleStream("http://mss26.rtl7.nl/rtlzbroad", 1200)
        streamItem.AppendSingleStream("http://mss4.rtl7.nl/rtlzbroad", 1200)
        streamItem.AppendSingleStream("http://mss5.rtl7.nl/rtlzbroad", 1200)
        streamItem.AppendSingleStream("http://mss3.rtl7.nl/rtlzbroad", 1200)
        rtlzLive.items.append(streamItem)
        items.append(rtlzLive)

        return items

    def CreateEpisodeItem(self, resultSet):
        """Creates a new MediaItem for an episode

        Arguments:
        resultSet : list[string] - the resultSet of the self.episodeItemRegex

        Returns:
        A new MediaItem of type 'folder'

        This method creates a new MediaItem from the Regular Expression or Json
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        """

        item = mediaitem.MediaItem(resultSet[2], "http://www.rtl.nl/system/s4m/xldata/abstract/%s.xml?version=2.0" % (resultSet[0]))

        channel = resultSet[1].lower()

        if channel in self.largeIconSet:
            item.icon = self.iconSet[channel]
            item.thumb = self.largeIconSet[channel]
        else:
            item.icon = self.folderIcon

        if resultSet[3]:
            item.thumbUrl = "http://data.rtl.nl/service/programma_logos/%s" % (resultSet[3],)

        return item

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
        if not data:
            return (data, items)

        settings = AddonSettings()

        # process the XML file in items and return an empty data string
        dom = xml.dom.minidom.parseString(data)
        for abstract in dom.getElementsByTagName("abstract"):
            programName = self.GetXmlTextForNode(abstract, "name")
        Logger.Trace("Processing: %s", programName)

        # Do not just set the name, add the items, basically we already determine al the items
        # that are available and already parse them here.

        for season in dom.getElementsByTagName("season"):
            name = self.GetXmlTextForNode(season, "name")
            key = season.getAttribute('key')

            folderItem = mediaitem.MediaItem(name, "", parent=self)
            folderItem.complete = True
            folderItem.thumb = self.noImage
            folderItem.icon = self.folderIcon

            self.seasons[key] = folderItem
            items.append(folderItem)
            Logger.Trace("Adding Season: %s", folderItem)

        for episode in dom.getElementsByTagName("episode"):
            number = self.GetXmlTextForNode(episode, "item_number")
            name = self.GetXmlTextForNode(episode, "name")
            synopsis = self.GetXmlTextForNode(episode, "synopsis")
            seasonKey = episode.getAttribute('season_key')
            key = episode.getAttribute('key')
            season = episode.getAttribute('season_key')

            if name == None:
                name = "Aflevering #%s" % (number,)

            # create the episode
            seasonItem = self.seasons[season]
            episodeItem = mediaitem.MediaItem(name, "", parent=seasonItem)
            episodeItem.description = synopsis
            episodeItem.complete = True
            episodeItem.thumb = self.noImage
            episodeItem.icon = self.folderIcon

            # now add them
            Logger.Trace("Adding Episode %s to Season %s", episodeItem, seasonItem)
            seasonItem.items.append(episodeItem)
            self.episodes[key] = episodeItem

        for material in dom.getElementsByTagName("material"):
            date = self.GetXmlTextForNode(material, "broadcast_date_display")
            url = self.GetXmlTextForNode(material, "component_uri")
            title = self.GetXmlTextForNode(material, "title")
            if title is None or title == "":
                continue

            thumbId = self.GetXmlTextForNode(material, "thumbnail_id")
            thumbUrl = "http://data.rtl.nl/system/img/71v0o4xqq2yihq1tc3gc23c2w/%s" % (thumbId,)
            # seasonKey = material.getAttribute('season_key')
            key = material.getAttribute('key')
            episodeKey = material.getAttribute('episode_key')

            if episodeKey == "" or episodeKey == u'':
                Logger.Error("Error matching RTL video: %s, %s", url, seasonKey)
                continue

            episodeItem = self.episodes[episodeKey]

            drm = self.GetXmlTextForNode(material, "audience")
            if drm.lower() == "drm":
                if settings.HideGeoLocked():
                    Logger.Debug("Found DRM Item: %s", title)
                    continue
                title = "[DRM] " + title

            tarief = self.GetXmlTextForNode(material, "tariff")
            if tarief:
                if settings.HideGeoLocked():
                    Logger.Debug("Found Paid Item: %s", title)
                    continue
                title = "[Paid] " + title

            # url = "http://www.rtl.nl/system/video/wvx" + url + "/1500.wvx?utf8=ok"  # or 600.wvx?utf8=ok
            url = "http://www.rtl.nl/system/s4m/xldata/ux/%s?context=rtlxl&d=pc&fmt=adaptive&version=3" % (key,)
            item = mediaitem.MediaItem(title, url, parent=episodeItem)
            # description = episodeItem.description
            item.thumbUrl = thumbUrl
            item.thumb = self.noImage
            item.type = "video"
            item.icon = self.icon

            dates = None
            if not date == "":
                dates = time.localtime(float(date))
                item.SetDate(dates[0], dates[1], dates[2])
            episodeItem.items.append(item)
            Logger.Trace("Adding Clip %s to Episode %s", item, episodeItem)

            # now we set the dates for the parents
            if dates:
                episodeItem.SetDate(dates[0], dates[1], dates[2], onlyIfNewer=True)
                episodeItem.parent.SetDate(dates[0], dates[1], dates[2], onlyIfNewer=True)

        # now sort them
        items.sort()
        for item in items:
            item.items.sort()
            for subitem in item.items:
                subitem.items.sort()
        return (data, items)

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

        item.thumb = self.CacheThumb(item.thumbUrl)

        xmlData = UriHandler.Open(item.url, pb=False, proxy=self.proxy)
        # <ref type='adaptive' device='pc' host='http://manifest.us.rtl.nl' href='/rtlxl/network/pc/adaptive/components/videorecorder/27/278629/278630/d009c025-6e8c-3d11-8aba-dc8579373134.ssm/d009c025-6e8c-3d11-8aba-dc8579373134.m3u8' />
        m3u8Urls = Regexer.DoRegex("<ref type='adaptive' device='pc' host='([^']+)' href='/([^']+)' />", xmlData)
        if not m3u8Urls:
            Logger.Warning("No m3u8 data found for: %s", item)
            return item
        m3u8Url = "%s/%s" % (m3u8Urls[0])

        m3u8Data = UriHandler.Open(m3u8Url, pb=False, proxy=self.proxy)
        # serverPart = m3u8Url[:m3u8Url.rindex("/")]
        part = item.CreateNewEmptyMediaPart()
        for m3u8 in Regexer.DoRegex(self.mediaUrlRegex, m3u8Data):
            item.complete = True
            # streamUrl = "%s/%s" % (serverPart, )
            part.AppendMediaStream(m3u8[1], m3u8[0])

        return item

    def GetXmlTextForNode(self, node, nodeName):
        elements = node.getElementsByTagName(nodeName)
        if len(elements) == 0:
            return ""

        element = elements[0]
        for childNode in element.childNodes:
                if childNode.nodeType == childNode.TEXT_NODE:
                    return childNode.data

    def __IgnoreCookieLaw(self):
        """ Accepts the cookies from RTL channel in order to have the site available """

        Logger.Info("Setting the Cookie-Consent cookie for www.uitzendinggemist.nl")

        # the rfc2109 parameters is not valid in Python 2.4 (Xbox), so we ommit it.
        c = cookielib.Cookie(version=0, name='rtlcookieconsent', value='yes', port=None, port_specified=False, domain='.www.rtl.nl', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=2327431273, discard=False, comment=None, comment_url=None, rest={'HttpOnly': None})  # , rfc2109=False)
        UriHandler.Instance().cookieJar.set_cookie(c)
        return
