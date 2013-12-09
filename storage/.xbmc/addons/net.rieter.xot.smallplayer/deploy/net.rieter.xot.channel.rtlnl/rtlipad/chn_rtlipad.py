#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import contextmenu
import chn_class

from regexer import Regexer
from helpers import xmlhelper
from logger import Logger
from urihandler import UriHandler


#===============================================================================
# main Channel Class
#===============================================================================
class Channel(chn_class.Channel):
    #===============================================================================
    # define class variables
    #===============================================================================
    def InitialiseVariables(self, channelInfo):
        """Used for the initialisation of user defined parameters.

        All should be present, but can be adjusted. If overridden by derived class
        first call chn_class.Channel.InitialiseVariables(self, channelInfo) to make sure all
        variables are initialised.

        Returns:
        True if OK

        """

        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self, channelInfo)

        self.mainListUri = "http://www.rtl.nl/system/s4m/ipadfd/d=ipad/fmt=adaptive/"
        # there also is a nettv stream: http://iptv.rtl.nl/nettv/feed.xml

        self.baseUrl = "http://www.rtl.nl/service/gemist/device/ipad/feed/index.xml"
        self.noImage = "rtlimage.png"

        self.requiresLogon = False
        self.episodeSort = True
        self.defaultPlayer = 'dvdplayer'

        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))

        self.episodeItemRegex = '<serieitem><itemsperserie_url>([^<]+)</itemsperserie_url><serienaam>([^<]+)</serienaam><seriescoverurl>([^<]+)</seriescoverurl><serieskey>([^<]+)</serieskey>'
        self.videoItemRegex = '(<item>([\w\W]+?)</item>)'
        self.mediaUrlRegex = 'BANDWIDTH=(\d+)\d{3}[^\n]+\W+([^\n]+.m3u8)'

        #==============================================================================
        # non standard items

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
        # Logger.Trace("iRTL :: %s", resultSet)

        item = mediaitem.MediaItem(resultSet[1], resultSet[0])
        item.thumbUrl = resultSet[2]
        item.icon = self.folderIcon
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

        xml = resultSet[0]
        xmlData = xmlhelper.XmlHelper(xml)

        name = "%s - %s" % (xmlData.GetSingleNodeContent("episodetitel"), xmlData.GetSingleNodeContent("title"))
        thumb = xmlData.GetSingleNodeContent("thumbnail")
        url = xmlData.GetSingleNodeContent("movie")
        date = xmlData.GetSingleNodeContent("broadcastdatetime")

        item = mediaitem.MediaItem(name, url)
        item.description = name
        item.icon = self.icon
        item.thumb = self.noImage
        item.thumbUrl = thumb
        item.type = 'video'

        item.SetDate(date[0:4], date[5:7], date[8:10], date[11:13], date[14:16], date[17:20])
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

        # load the details.
        playlistdata = UriHandler.Open(item.url, proxy=self.proxy)
        urls = Regexer.DoRegex(self.mediaUrlRegex, playlistdata)

        # baseUrl from: http://us.rtl.nl/Thu14.RTL_D_110818_143155_190_Britt_Ymke_op_d.MiMe.ssm/Thu14.RTL_D_110818_143155_190_Britt_Ymke_op_d.MiMe.m3u8
        baseUrl = item.url[0:item.url.rfind("/")]
        Logger.Debug("Using baseUrl: %s", baseUrl)

        part = item.CreateNewEmptyMediaPart()
        for url in urls:
            # Logger.Trace(url)
            if "http" in url[1]:
                mediaUrl = url[1]
            else:
                mediaUrl = "%s/%s" % (baseUrl, url[1])
            part.AppendMediaStream(mediaUrl, url[0])

        item.complete = True
        return item
