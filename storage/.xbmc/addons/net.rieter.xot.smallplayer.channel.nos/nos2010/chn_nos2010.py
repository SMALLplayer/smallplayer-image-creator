import time
import datetime
import cookielib
import os

import mediaitem
import contextmenu
import chn_class
import envcontroller

from config import Config
from regexer import Regexer
from helpers import encodinghelper
from helpers import subtitlehelper
from helpers import datehelper
from helpers.jsonhelper import JsonHelper

from logger import Logger
from urihandler import UriHandler
from addonsettings import AddonSettings


class Channel(chn_class.Channel):
    """
    main class from which all channels inherit
    """

    def InitialiseVariables(self, channelInfo):
        """
        Used for the initialisation of user defined parameters. All should be
        present, but can be adjusted
        """

        try:
            # call base function first to ensure all variables are there
            chn_class.Channel.InitialiseVariables(self, channelInfo)

            self.noImage = "nosimage.png"
            self.baseUrl = "http://www.uitzendinggemist.nl"
            self.requiresLogon = False

            if self.channelCode == "uzg":
                self.mainListUri = "%s/programmas" % (self.baseUrl,)
                self.noImage = "nosimage.png"

            elif self.channelCode == "uzgjson":
                self.baseUrl = "http://apps-api.uitzendinggemist.nl"
                self.mainListUri = "%s/series.json" % (self.baseUrl,)
                self.noImage = "nosimage.png"

                self.CreateEpisodeItem = self.CreateEpisodeItemJson
                self.CreateVideoItem = self.CreateVideoItemJson
                self.UpdateVideoItem = self.UpdateVideoItemJson
                self.SearchSite = self.SearchSiteJson
                self.ParseMainList = self.ParseMainListJson

            elif self.channelCode == "zapp":
                self.mainListUri = "%s/zapp" % (self.baseUrl,)
                self.noImage = "zapimage.png"

            elif self.channelCode == "zappelin":
                self.mainListUri = "%s/zappelin" % (self.baseUrl,)
                self.noImage = "zappelinimage.png"

            self.contextMenuItems = []
            if envcontroller.EnvController.IsPlatform(envcontroller.Environments.Xbox):
                self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
                self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))

            # if not self.channelCode == "uzgjson":
            self.contextMenuItems.append(contextmenu.ContextMenuItem("Download item", "CtMnDownload", itemTypes='video', completeStatus=True, plugin=True))

            self.contextMenuItems.append(contextmenu.ContextMenuItem("Refresh item", "CtMnRefresh", itemTypes="video", completeStatus=True))

            # these REGEXES are a mess, but we just need more to make shure all works.

            # used to catch the A-Z urls and latetly URLs
            episodeItemRegex1 = '<li><a href="/((?:programmas|zapp|zappelin)/[^"]+)"[^>]*title="Toon [^"]+">([^<])</a></li>'
            if self.channelCode == "uzg":
                episodeItemRegex2 = '<li><a href="/(weekarchief)/((\d+)-(\d+)-(\d+)|(\w+))">([^<]+)</a></li>'
            else:
                # no exta stuff needed for Z@pp and Z@ppelin
                episodeItemRegex2 = '(w)(w)(w)(w)(w)(w)(w)'
            self.episodeItemRegex = '(?:%s|%s)' % (episodeItemRegex1, episodeItemRegex2)

            # regex for Top 50 and Weekoverview
            videoItemRegex2 = 'class="thumbnail" data-images="\[([^]]*)\]" [^>]+[\w\W]{0,400}?<h2><a[^>]+title="([^"]+)"[^\n]+\W{0,100}<h3><a href="/([^"]+)"[^>]+title="((?:[^"]+\(){0,1}(\w+ +\d+ \w+ \d+, \d+:\d+)\W*\){0,1})"'
            # regex for episodes details
            videoItemRegex3 = 'class="thumbnail" data-images="\[([^]]*)\]" [^>]+></a>\W+[\w\W]{0,800}?(?:<h2>\W*<a href="/afleveringen/\d+"[^>]+title="([^"]+)">[\w\W]{0,500}?){0,1}<h3[^>]*>\W*<a href="/([^"]+)" class="episode[^>]+title="((?:[^"]+\(){0,1}(\w+ +\d+ \w+ \d+, \d+:\d+)\W*\){0,1})">[\w\W]{0,400}</h3>([^<]+)'
            self.videoItemRegex = '(?:%s|%s)' % (videoItemRegex2, videoItemRegex3)

            # used for the A-Z indexes to parse the programms
            folderItemRegex1 = '<h2>\W*<a href="/programmas/(\d+)([^"]+)"[^>]*>([^<]+)</a>[\w\W]{0,400}?</h2>\W+<div[^>]+>\W+<a href="[^"]+">Bekijk laatste</a> \((?:(Geen)|\w+\W+(\d+) (\w+) (\d+), (\d+):(\d+))\)'
            # used for search results
            folderItemRegex2 = '<div class="wrapper">\W*<div class="img">\W*<a href="/(programma[^"]+)"[^<]+<img alt="([^"]+)" class="thumbnail" data-images="\[([^]]*)\]"[\w\W]{0,1000}?<div class="date">\w+ +(\d+) (\w+) (\d+), (\d+):(\d+)'
            self.folderItemRegex = "(?:%s|%s)" % (folderItemRegex1, folderItemRegex2)

            """
                The ProcessPageNavigation method will parse the current data using the pageNavigationRegex. It will
                create a pageItem using the CreatePageItem method. If no CreatePageItem method is in the channel,
                a default one will be created with the number present in the resultset location specified in the
                pageNavigationRegexIndex and the url from the combined resultset. If that url does not contain http://
                the self.baseUrl will be added.
            """

            self.pageNavigationRegex = '<a[^>]+href="([^"]+(?:afleveringen|weekarchief|programmas)[^"]+page=)(\d+)">\d+'
            self.pageNavigationRegexIndex = 1

            if self.channelCode == "uzgjson":
                self.episodeItemRegex = None
                self.episodeItemJson = ()
                self.videoItemRegex = None
                # we need 2 regexes, one for search results and one for normal results
                self.videoItemJsonNormal = ("episodes",)
                self.videoItemJsonSearch = ()
                self.videoItemJson = self.videoItemJsonNormal
                self.folderItemRegex = None
                self.pageNavigationRegex = None

            # needs to be here because it will be too late in the script version
            self.__IgnoreCookieLaw()
        except:
            Logger.Error("Error Initializing Variables for NOS", exc_info=True)
        #==============================================================================
        # non standard items
        self.sortAlphabetically = True
        self.maxNumberOfFrontPages = 0
        self.md5Encoder = encodinghelper.EncodingHelper()
        self.environmentController = envcontroller.EnvController()
        # self.securityCodes = None
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
        # first do the basic stuff
        items = chn_class.Channel.ParseMainList(self, returnData=returnData)

        if self.channelCode == "uzg":
            # we need to append some stuff
            top50 = mediaitem.MediaItem("Top 50 bekeken", "%s/top50" % (self.baseUrl,))
            top50.complete = True
            top50.icon = self.icon
            top50.thumb = self.noImage
            items.append(top50)

            search = mediaitem.MediaItem("Zoeken", "searchSite")
            search.complete = True
            search.icon = self.icon
            search.thumb = self.noImage
            items.append(search)

        return items

    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item.

        http://www.uitzendinggemist.nl/programmas/2.rss (programmaID)
        """
        # Logger.Trace(resultSet)

        if resultSet[0] != '':
            name = "Alfabetisch's: %s" % (resultSet[1],)
            url = "%s/%s?order=latest_broadcast_date_desc&page=1" % (self.baseUrl, resultSet[0])
        elif resultSet[2] != '':
            # specific stuff
            name = resultSet[8].capitalize()
            url = "%s/%s/%s?display_mode=list&herhaling=ja" % (self.baseUrl, resultSet[2], resultSet[3])
        else:
            return None
        # url = "http://www.uitzendinggemist.nl/programmas/%s%s.rss" % (resultSet[0], resultSet[1])

        item = mediaitem.MediaItem(name, url)
        item.type = 'folder'
        item.icon = self.icon
        item.complete = True
        item.thumb = self.noImage

        if resultSet[4] != '':
            # date specified
            item.SetDate(resultSet[4], resultSet[5], resultSet[6])
            pass
        elif resultSet[7] == 'vandaag':
            now = datetime.date.today()
            item.SetDate(now.year, now.month, now.day)
        elif resultSet[7] == 'gisteren':
            now = datetime.date.today()
            now = now - datetime.timedelta(1)
            item.SetDate(now.year, now.month, now.day)

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

        Logger.Info("Performing Pre-Processing")
        items = []

        if '<ul class="episodes" id="episode-results">' in data:
            # we need to strip the search results
            startIndex = data.index('<div id="series-slider">')
            data = data[startIndex + 20:]
            endIndex = data.index('<div class="tabs_wrapper">')
            data = data[:endIndex]

        if self.channelCode == "uzgjson":
            if "active_episodes_count" in data:
                self.videoItemJson = self.videoItemJsonNormal
            else:
                self.videoItemJson = self.videoItemJsonSearch

        Logger.Debug("Pre-Processing finished")
        return data, items

    def CreateFolderItem(self, resultSet):
        """Creates a MediaItem of type 'folder' using the resultSet from the regex.

        Arguments:
        resultSet : tuple(strig) - the resultSet of the self.folderItemRegex

        Returns:
        A new MediaItem of type 'folder'

        This method creates a new MediaItem from the Regular Expression or Json
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        """

        if resultSet[0] == "":
            # search results
            name = resultSet[10]
            url = "%s/%s" % (self.baseUrl, resultSet[9],)
            item = mediaitem.MediaItem(name, url)
            item.type = 'folder'
            item.icon = self.icon

            year = resultSet[14]
            month = resultSet[13]
            month = datehelper.DateHelper.GetMonthFromName(month, "nl")
            day = resultSet[12]
            hour = resultSet[15]
            minute = resultSet[16]
            item.SetDate(year, month, day, hour, minute, 0)

            thumbnails = resultSet[11]
            thumbUrl = self.__GetThumbUrl(thumbnails)
            if thumbUrl != "":
                item.thumbUrl = thumbUrl

            item.thumb = self.noImage
            item.complete = True
            return item

        name = resultSet[2]
        # url = "http://www.uitzendinggemist.nl/programmas/%s%s.rss" % (resultSet[0], resultSet[1])
        # Let's not use RSS for now.
        url = "%s/programmas/%s%s" % (self.baseUrl, resultSet[0], resultSet[1])

        item = mediaitem.MediaItem(name, url)
        item.type = 'folder'
        item.icon = self.icon
        item.thumb = self.noImage
        item.complete = True

        # get the date
        try:
            month = datehelper.DateHelper.GetMonthFromName(resultSet[5], "nl")

            day = resultSet[4]
            year = resultSet[6]
            # hour = resultSet[7]
            # min = resultSet[8]
            item.SetDate(year, month, day)
        except:
            Logger.Error("Error resolving Month: %s", resultSet[4])

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

        #noinspection PyStatementEffect
        """
                http://player.omroep.nl/info/security/ geeft volgende item
                MTI4NTAwODUzMHxOUE9VR1NMIDEuMHxoNnJjbXNJZnxnb25laTFBaQ== -> SessionKey (via Convert.FromBase64String & Encoding.UTF8.GetString ) = 1285008530|NPOUGSL 1.0|h6rcmsIf|gonei1Ai -> split on "|"
                                                                                                                                                   1285413107|NPOUGSL 1.0|h6rcmsIf|gonei1Ai
                aflid: 11420664
                AEAE45803625654A216FB8DF43BD9ACD = MD5 van aflid|sessionKey[1]
                Denk niet dat SessionKey[1] ooit veranderd? -> lijkt van niet

                http://player.omroep.nl/info/metadata/aflevering/11447726/5CE0A8F6DEAA0106C85C5286EA4F89E4
                http://player.omroep.nl/info/stream/aflevering/11447726/5CE0A8F6DEAA0106C85C5286EA4F89E4
                """

        if resultSet[2] != "#" and resultSet[2] != "":
            # regex for Top 50 and Weekoverview
            Logger.Debug("regex for Top 50 and Weekoverview")
            return self.__CreateVideoItem(resultSet[0], resultSet[1], resultSet[2], resultSet[3], resultSet[4], "")

        elif resultSet[7] != "#" and resultSet[7] != "":
            # regex for Searchresults and episodes
            Logger.Debug("regex for Searchresults and episodes")
            return self.__CreateVideoItem(resultSet[5], resultSet[6], resultSet[7], resultSet[8], resultSet[9], resultSet[10])
        else:
            return None

    def UpdateVideoItem(self, item):
        """
        Accepts an arraylist of results. It returns an item.
        """

        if "gemi.st" in item.url:
            episodeId = Regexer.DoRegex('http://gemi.st/(\d+)', item.url)[0]
        else:
            data = UriHandler.Open(item.url, proxy=self.proxy)
            episodeId = Regexer.DoRegex('data-player-id="([^"]+)"', data)[0]
        Logger.Debug("EpisodeId for %s: %s", item, episodeId)

        return self.__UpdateVideoItem(item, episodeId)

    def SearchSite(self, url=None):  # @UnusedVariable
        """Creates an list of items by searching the site

        Returns:
        A list of MediaItems that should be displayed.

        This method is called when the URL of an item is "searchSite". The channel
        calling this should implement the search functionality. This could also include
        showing of an input keyboard and following actions.

        """

        url = "%s/zoek/programmas?id=%s&series_page=1" % (self.baseUrl, "%s")
        return chn_class.Channel.SearchSite(self, url)

    def ParseMainListJson(self, returnData=False):
        """Parses the mainlist of the channel and returns a list of MediaItems

        This method creates a list of MediaItems that represent all the different
        programs that are available in the online source. The list is used to fill
        the ProgWindow.

        Keyword parameters:
        returnData : [opt] boolean - If set to true, it will return the retrieved
                                     data as well

        Returns a list of MediaItems that were retrieved.

        """

        # first do the basic stuff
        items = chn_class.Channel.ParseMainList(self, returnData=returnData)

        search = mediaitem.MediaItem("\a.: Zoeken :.", "searchSite")
        search.complete = True
        search.icon = self.icon
        search.thumb = self.noImage
        search.SetDate(2200, 1, 1, text="")
        items.append(search)

        extra = mediaitem.MediaItem("\a.: Populair :.", "%s/episodes/popular.json" % (self.baseUrl,))
        extra.complete = True
        extra.icon = self.icon
        extra.thumb = self.noImage
        extra.SetDate(2200, 1, 1, text="")
        items.append(extra)

        extra = mediaitem.MediaItem("\a.: Tips :.", "%s/tips.json" % (self.baseUrl,))
        extra.complete = True
        extra.icon = self.icon
        extra.thumb = self.noImage
        extra.SetDate(2200, 1, 1, text="")
        items.append(extra)

        extra = mediaitem.MediaItem("\a.: Recent :.", "%s/broadcasts/recent.json" % (self.baseUrl,))
        extra.complete = True
        extra.icon = self.icon
        extra.thumb = self.noImage
        extra.SetDate(2200, 1, 1, text="")
        items.append(extra)

        return items

    def CreateEpisodeItemJson(self, resultSet):
        """Creates a new MediaItem for an episode

        Arguments:
        resultSet : list[string] - the resultSet of the self.episodeItemRegex

        Returns:
        A new MediaItem of type 'folder'

        This method creates a new MediaItem from the Regular Expression or Json
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        """

        episodeId = resultSet['nebo_id']
        url = "%s/series/%s.json" % (self.baseUrl, episodeId)
        name = resultSet['name']
        description = resultSet.get('description', '')
        thumbUrl = resultSet['image']

#        date = resultSet['date']
#        date = date[0:date.find("T")]
#        date = date.split("-")
#        time = resultSet['date']
#        time = time[time.find("T") + 1:]
#        time = time.split(":")

        item = mediaitem.MediaItem(name, url)
        item.type = 'folder'
        item.icon = self.icon
        item.complete = True
        item.description = description
#        item.SetDate(date[0], date[1], date[2], time[0], time[1], 0)
        item.thumb = self.noImage
        if thumbUrl:
            item.thumbUrl = thumbUrl

        return item

    def CreateVideoItemJson(self, resultSet):
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

        # in some case some properties are at the root and some at the subnode
        # get the root items here
        posix = resultSet.get('starts_at', None)
        name = resultSet.get('name', None)
        description = resultSet.get('description', '')
        image = resultSet.get('image', None)

        # the tips has an extra 'episodes' key
        if 'episode' in resultSet:
            Logger.Debug("Found subnode: episodes")
            # set to episode node
            data = resultSet['episode']
            Logger.Trace(data)
            titleExtra = resultSet.get('title', '')
        else:
            titleExtra = None
            data = resultSet

        posix = data.get('broadcasted_at', posix)
        broadcasted = datetime.datetime.fromtimestamp(posix)

        if not name:
            Logger.Debug("Trying alternative ways to get the title")
            name = data.get('series', {'name': self.parentItem.name})['name']

        name.strip("")
        if titleExtra:
            name = "%s - %s" % (name, titleExtra)

        # url = data['video']['m3u8']

        videoId = data.get('whatson_id', None)
        item = mediaitem.MediaItem(name, videoId)
        item.icon = self.icon
        item.type = 'video'
        item.complete = False
        item.description = description

        images = data.get('stills', None)
        if images:
            # there were images in the stills
            item.thumbUrl = images[-1]['url']
        elif image:
            # no stills, or empty, check for image
            item.thumbUrl = image

        item.SetDate(broadcasted.year, broadcasted.month, broadcasted.day, broadcasted.hour, broadcasted.minute, broadcasted.second)

        return item

    def UpdateVideoItemJson(self, item):
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

        whatson_id = item.url
        return self.__UpdateVideoItem(item, whatson_id)

    def GetDefaultCachePath(self):
        """ returns the default cache path for this channel"""

        # set the UZG path
        if AddonSettings().GetUzgCacheDuration() > 0:
            cachPath = AddonSettings().GetUzgCachePath()
            if cachPath:
                Logger.Trace("UZG Cache path resolved to: %s", cachPath)
                return cachPath

        cachePath = chn_class.Channel.GetDefaultCachePath(self)
        Logger.Trace("UZG Cache path resolved chn_class default: %s", cachePath)
        return cachePath

    #noinspection PyUnusedLocal
    def SearchSiteJson(self, url=None):  # @UnusedVariable
        """Creates an list of items by searching the site

        Returns:
        A list of MediaItems that should be displayed.

        This method is called when the URL of an item is "searchSite". The channel
        calling this should implement the search functionality. This could also include
        showing of an input keyboard and following actions.

        """
        url = "%s/episodes/search/%s.json" % (self.baseUrl, "%s")
        return chn_class.Channel.SearchSite(self, url)

    def CtMnDownload(self, item):
        """ downloads a video item and returns the updated one
        """
        #noinspection PyUnusedLocal
        item = self.DownloadVideoItem(item)

    def __UpdateVideoItem(self, item, episodeId):
        """Updates an existing MediaItem with more data.

        Arguments:
        item      : MediaItem - the MediaItem that needs to be updated
        episodeId : String    - The episodeId, e.g.: VARA_xxxxxx

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

        # get the subtitle
        subTitleUrl = "http://e.omroep.nl/tt888/%s" % (episodeId,)
        subTitlePath = subtitlehelper.SubtitleHelper.DownloadSubtitle(subTitleUrl, episodeId + ".srt", format='srt', proxy=self.proxy)

        # we need an hash code
        hashCode = self.__GetHashCode(item)

        metaUrl = "http://e.omroep.nl/metadata/aflevering/%s" % (episodeId,)
        metaData = UriHandler.Open(metaUrl, pb=False, proxy=self.proxy)
        metaJson = JsonHelper(metaData)

        item.MediaItemParts = []

        # streamUrl = "http://pi.omroep.nl/info/stream/aflevering/%s/%s" % (episodeId, hashCode)
        streamUrlSource = "http://ida.omroep.nl/odiplus/?prid=%s&puboptions=adaptive,h264_bb,h264_sb,h264_std&adaptive=no&part=1&token=%s" % (episodeId, hashCode,)
        streamUrlData = UriHandler.Open(streamUrlSource, proxy=self.proxy, noCache=True)
        Logger.Trace(streamUrlData)

        streamJson = JsonHelper(streamUrlData)
        part = item.CreateNewEmptyMediaPart()
        part.Subtitle = subTitlePath

        # should we cache before playback
        if AddonSettings().GetUzgCacheDuration() > 0:
            part.CanStream = False

        for url in streamJson.GetValue('streams'):
            if "h264_bb" in url:
                bitrate = 500
            elif "h264_sb" in url:
                bitrate = 220
            elif "h264_std" in url:
                bitrate = 1000
            else:
                bitrate = None

            actualJson = JsonHelper(UriHandler.Open(url, proxy=self.proxy))
            protocol = actualJson.GetValue('protocol')
            if protocol:
                url = "%s://%s%s" % (protocol, actualJson.GetValue('server'), actualJson.GetValue('path'))
                part.AppendMediaStream(url, bitrate=bitrate)
            else:
                Logger.Warning("Found UZG Stream without a protocol. Probably a expired page.")

        # now we need to get extra info from the data
        item.description = metaJson.GetValue("info")
        item.title = metaJson.GetValue('aflevering_titel')
        station = metaJson.GetValue('streamSense', 'station')

        if station.startswith('nederland_1'):
            item.icon = self.GetImageLocation("1icon.png")
        elif station.startswith('nederland_2'):
            item.icon = self.GetImageLocation("2icon.png")
        elif station.startswith('nederland_3'):
            item.icon = self.GetImageLocation("3icon.png")
        Logger.Trace("Icon for station %s = %s", station, item.icon)

        # <image size="380x285" ratio="4:3">http://u.omroep.nl/n/a/2010-12/380x285_boerzoektvrouw_yvon.png</image>
        thumbUrls = metaJson.GetValue('images')  # , {"size": "380x285"}, {"ratio":"4:3"})
        Logger.Trace(thumbUrls)
        if thumbUrls:
            thumbUrl = thumbUrls[-1]['url']
        else:
            thumbUrl = self.noImage

        if not "http" in thumbUrl:
            thumbUrl = "http://u.omroep.nl/n/a/%s" % (thumbUrl,)

        item.thumb = self.CacheThumb(thumbUrl)
        Logger.Trace(thumbUrl)

        item.complete = True
        return item

    def __GetHashCode(self, item):
        tokenUrl = "http://ida.omroep.nl/npoplayer/i.js"
        tokenExpired = True
        tokenFile = "uzg-i.js"
        tokenPath = os.path.join(Config.cacheDir, tokenFile)

        # determine valid token
        if os.path.exists(tokenPath):
            mTime = os.path.getmtime(tokenPath)
            Logger.Debug("Found token '%s' which is %s seconds old", tokenFile, time.time() - mTime)
            if mTime + 30 * 60 < time.time():  # if older than 15 minutes, 30 also seems to work.
                Logger.Debug("Token expired.")
                tokenExpired = True
            else:
                tokenExpired = False
        else:
            Logger.Debug("No Token Found.")

        if tokenExpired:
            Logger.Debug("Fetching a Token.")
            tokenData = UriHandler.Open(tokenUrl, pb=True, proxy=self.proxy, noCache=True)
            tokenHandle = file(tokenPath, 'w')
            tokenHandle.write(tokenData)
            tokenHandle.close()
            Logger.Debug("Token saved for future use.")
        else:
            Logger.Debug("Reusing an existing Token.")
            tokenHandle = file(tokenPath, 'r')
            tokenData = tokenHandle.read()
            tokenHandle.close()

        # perhaps we should random it?
        token = Regexer.DoRegex('npoplayer.token = "([^"]+)', tokenData)[-1]
        Logger.Info("Found NOS token for %s: %s", item, token)
        return token

    def __CreateVideoItem(self, thumbnails, showName, url, episodeName, datestring, description):
        """ Creates a MediaItem for the given values

        Arguments:
        thumbnails  : string - a list of thumbnails in the format:
                               &quot;<URL>&quot;,&quot;<URL>&quote;
        showName    : string - the name of the main show
        episodeName : string - the name of the episode
        datestring  : string - datetime in the format: 'di 20 dec 2011, 12:00'
        description : string - description of the show

        Returns a new MediaItem

        """

        # Logger.Trace("thumbnails: %s\nshowName: %s\nurl: %s\nepisodeName: %s\ndatestring: %s\ndescription: %s", thumbnails, showName, url, episodeName, datestring, description)

        if showName:
            name = "%s - %s" % (showName, episodeName)
        else:
            name = episodeName
        url = "%s/%s" % (self.baseUrl, url)

        item = mediaitem.MediaItem(name, url)
        item.icon = self.icon
        item.type = 'video'
        item.complete = False
        item.description = description.strip()
        item.thumb = self.noImage

        # Date format: 'di 20 dec 2011, 12:00'
        #               012345678901234567890
        year = month = day = hour = minute = 0
        partList = Regexer.DoRegex("\w+ (?P<day>\d+) (?P<month>\w+) (?P<year>\d+).+(?P<hour>\d+):(?P<minute>\d+)", datestring)
        for dateParts in partList:
            year = dateParts['year']
            month = dateParts['month']
            month = datehelper.DateHelper.GetMonthFromName(month, "nl")
            day = dateParts['day']
            hour = dateParts['hour']
            minute = dateParts['minute']
        item.SetDate(year, month, day, hour, minute, 0)

        thumbUrl = self.__GetThumbUrl(thumbnails)
        if thumbUrl != "":
            item.thumbUrl = thumbUrl

        item.complete = False
        return item

    def __GetThumbUrl(self, thumbnails):
        """ fetches the thumburl from an coded string

        Arguments:
        thumbnails  : string - a list of thumbnails in the format:
                               &quot;<URL>&quot;,&quot;<URL>&quote;

        returns the URL of single thumb

        """

        # thumb splitting
        if len(thumbnails) > 0:
            thumbnails = thumbnails.split(';')
            # Logger.Trace(thumbnails)
            thumbUrl = thumbnails[1].replace('140x79', '280x158').replace('60x34', '280x158').replace("&quot", "")
            # Logger.Trace(thumbUrl)
        else:
            thumbUrl = ""

        return thumbUrl

    def __IgnoreCookieLaw(self):
        """ Accepts the cookies from UZG in order to have the site available """

        Logger.Info("Setting the Cookie-Consent cookie for www.uitzendinggemist.nl")

        # the rfc2109 parameters is not valid in Python 2.4 (Xbox), so we ommit it.
        c = cookielib.Cookie(version=0, name='site_cookie_consent', value='yes', port=None, port_specified=False, domain='.www.uitzendinggemist.nl', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=2327431273, discard=False, comment=None, comment_url=None, rest={'HttpOnly': None})  # , rfc2109=False)
        UriHandler.Instance().cookieJar.set_cookie(c)

        # a second cookie seems to be required
        c = cookielib.Cookie(version=0, name='npo_cc', value='tmp', port=None, port_specified=False, domain='.www.uitzendinggemist.nl', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=2327431273, discard=False, comment=None, comment_url=None, rest={'HttpOnly': None})  # , rfc2109=False)
        UriHandler.Instance().cookieJar.set_cookie(c)

        # http://pilot.odcontent.omroep.nl/codem/h264/1/nps/rest/2013/NPS_1220255/NPS_1220255.ism/NPS_1220255.m3u8
        # balancer://sapi2cluster=balancer.sapi2a

        # c = cookielib.Cookie(version=0, name='balancer://sapi2cluster', value='balancer.sapi2a', port=None, port_specified=False, domain='.pilot.odcontent.omroep.nl', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=2327431273, discard=False, comment=None, comment_url=None, rest={'HttpOnly': None})  # , rfc2109=False)
        # UriHandler.Instance().cookieJar.set_cookie(c)
        # c = cookielib.Cookie(version=0, name='balancer://sapi1cluster', value='balancer.sapi1a', port=None, port_specified=False, domain='.pilot.odcontent.omroep.nl', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=2327431273, discard=False, comment=None, comment_url=None, rest={'HttpOnly': None})  # , rfc2109=False)
        # UriHandler.Instance().cookieJar.set_cookie(c)
        return
