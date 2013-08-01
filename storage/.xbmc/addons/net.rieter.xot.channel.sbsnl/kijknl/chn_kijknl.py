#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import contextmenu
import chn_class

from regexer import Regexer
from helpers import brightcovehelper
from helpers.htmlhelper import HtmlHelper
from proxyinfo import ProxyInfo

from logger import Logger
from urihandler import UriHandler


#===============================================================================
# main Channel Class
#===============================================================================
class Channel(chn_class.Channel):
    """
    main class from which all channels inherit
    """

    #===============================================================================
    def InitialiseVariables(self, channelInfo):
        """
        Used for the initialisation of user defined parameters. All should be
        present, but can be adjusted
        """
        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self, channelInfo)

        self.baseUrl = "http://www.kijk.nl"
        if self.channelCode == 'veronica':
            self.noImage = "veronicaimage.png"
            self.mainListUri = "http://www.kijk.nl/veronicatv/zender"

        elif self.channelCode == 'sbs':
            self.noImage = "sbs6image.png"
            self.mainListUri = "http://www.kijk.nl/sbs6/zender"

        elif self.channelCode == 'net5':
            self.noImage = "net5image.png"
            self.mainListUri = "http://www.kijk.nl/net5/zender"

        self.episodeItemRegex = ('<li><a class="[^>]*" href="([^"]+video/[^"]+)">([^<]+)</a></li>', '<a href="(/video/[^"]+)">[\w\W]{0,300}?<span class="title">([^<]+)<')
        self.videoItemRegex = '<article class="([^"]+)">([\w\W]{0,1000}?)</article>'

        # self.folderItemRegex = '<li><a  href="(?P<url>[^"]+)">(?P<name>[^<]+)</a></li>'
        self.mediaUrlRegex = '<object id=@"myExperience[\w\W]+?playerKey@" value=@"([^@]+)[\w\W]{0,1000}?videoPlayer@" value=@"(\d+)@"'.replace("@", "\\\\")

        # self.pageNavigationRegex = '<li class=""><a href="(/ajax/VideoClips/[^"]+/page/)(\d+)"' #self.pageNavigationIndicationRegex
        # self.pageNavigationRegexIndex = 1

        self.onUpDownUpdateEnabled = True
        self.requiresLogon = False

        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))

        self.__parsedEpisodes = []
        return True

    def CreateEpisodeItem(self, resultSet):
        """Creates a new MediaItem for an episode

        Arguments:
        resultSet : list[string] - the resultSet of the self.episodeItemRegex

        Returns:
        A new MediaItem of type 'folder'

        This method creates a new MediaItem from the Regular Expression
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        """

        # due to incomplete "all programs" list we also parse videos in the
        # main page, that could result in duplicate names.
        if resultSet[2] in self.__parsedEpisodes:
            return None
        else:
            self.__parsedEpisodes.append(resultSet[2])

        if not "http://" in resultSet[1]:
            url = "%s/%s" % (self.baseUrl, resultSet[1])
        else:
            url = resultSet[1]
        item = mediaitem.MediaItem(resultSet[2], url)
        item.icon = self.iconLarge
        # item.thumbUrl = urlparse.urljoin(self.baseUrl, resultSet['thumb'])
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

        # Logger.Trace(resultSet)

        itemType = resultSet[0]
        Logger.Trace(itemType)

        html = HtmlHelper(resultSet[1])
        image = html.GetTagAttribute("img", {"alt": None}, {"src": None}, firstOnly=False)[0]

        series = image[0]
        Logger.Trace(series)

        image = image[1]
        if not "http://" in image:
            image = "%s%s" % (self.baseUrl, image)
        Logger.Trace(image)

        title = html.GetTagContent("h1", firstOnly=True)
        Logger.Trace(title)

        url = html.GetTagAttribute("a", {"class": "wrap"}, {"href": None})
        if not "http://" in url:
            url = "%s%s" % (self.baseUrl, url)
        Logger.Trace(url)

        item = mediaitem.MediaItem("%s - %s" % (series, title), url)
        item.type = 'video'

        item.thumb = self.noImage
        item.icon = self.icon
        item.thumbUrl = image

        if not '<time datetime="">' in resultSet[1]:
            dt = html.GetTagAttribute("time", {"datetime": None})
            Logger.Trace(dt)
            year = dt[0:4]
            month = dt[5:7]
            day = dt[8:10]
            hour = dt[11:13]
            minute = dt[14:16]
            seconds = dt[17:19]
            Logger.Trace((dt, year, month, day, hour, minute, seconds))
            item.SetDate(year, month, day, hour, minute, seconds)

        item.complete = False
        return item

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

        videoId = item.url[item.url.rfind("/") + 1:]

        url = "http://embed.kijk.nl/?width=868&height=491&video=%s" % (videoId,)
        referer = "http://www.kijk.nl/video/%s" % (videoId,)

        # now the mediaurl is derived. First we try WMV
        data = UriHandler.Open(url, pb=False, referer=referer)
        Logger.Trace(self.mediaUrlRegex)
        objectData = Regexer.DoRegex(self.mediaUrlRegex, data)[0]
        Logger.Trace(objectData)

        # seed = "61773bc7479ab4e69a5214f17fd4afd21fe1987a"
        # seed = "0a2b91ec0fdb48c5dd5239d3e796d6f543974c33"
        seed = "0b0234fa8e2435244cdb1603d224bb8a129de5c1"
        amfHelper = brightcovehelper.BrightCoveHelper(Logger.Instance(), objectData[0], objectData[1], url, seed)  # , proxy=ProxyInfo("localhost", 8888)
        item.description = amfHelper.GetDescription()

        part = item.CreateNewEmptyMediaPart()
        for stream, bitrate in amfHelper.GetStreamInfo():
            part.AppendMediaStream(stream.replace("&mp4:", ""), bitrate)

        item.complete = True
        return item
