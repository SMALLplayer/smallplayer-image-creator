# coding:UTF-8

#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import contextmenu
import chn_class

from regexer import Regexer
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
        """Used for the initialisation of user defined parameters.

        All should be present, but can be adjusted. If overridden by derived class
        first call chn_class.Channel.InitialiseVariables(self, channelInfo) to make sure all
        variables are initialised.

        Returns:
        True if OK

        """

        # call base function first to ensure all variables are there

        chn_class.Channel.InitialiseVariables(self, channelInfo)
        if self.channelCode == 'nickelodeon':
            self.noImage = "nickelodeonimage.png"
            self.mainListUri = "http://www.nickelodeon.nl/shows"
            self.baseUrl = "http://www.nickelodeon.nl"

        elif self.channelCode == "nickjr":
            self.noImage = "nickjrimage.png"
            self.mainListUri = "http://www.nickelodeon.nl/kanalen/18"
            self.baseUrl = "http://www.nickelodeon.nl"

        elif self.channelCode == "nickno":
            self.noImage = "nickelodeonimage.png"
            self.mainListUri = "http://www.nickelodeon.no/kanalen/29"
            self.baseUrl = "http://www.nickelodeon.no"

# The junior channels do not seem to be OK as they are the same for NO and SE
#        elif self.channelCode == "nickjrno":
#            self.noImage = "nickjrimage.png"
#            self.mainListUri = "http://www.nickelodeon.no/kanalen/20"
#            self.baseUrl = "http://www.nickelodeon.no"

        elif self.channelCode == "nickse":
            self.noImage = "nickelodeonimage.png"
            self.mainListUri = "http://www.nickelodeon.se/kanaler/30"
            self.baseUrl = "http://www.nickelodeon.se"

# The junior channels do not seem to be OK as they are the same for NO and SE
#        elif self.channelCode == "nickjrse":
#            self.noImage = "nickjrimage.png"
#            self.mainListUri = "http://www.nickelodeon.se/kanaler/20"
#            self.baseUrl = "http://www.nickelodeon.se"
        else:
            raise NotImplementedError("Unknown channel code")

        self.onUpDownUpdateEnabled = True

        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))

        self.requiresLogon = False
        self.swfUrl = "http://media.mtvnservices.com/player/prime/mediaplayerprime.1.9.1.swf"

        self.episodeItemRegex = ('<h3>([^<]+)</h3>\W+<a[\W\w]+?<a href="(/videos[^"]+|/video[^"]+)"', '<a href="/program/([^"]+)"[^>]+title="([^"]+)')
        self.videoItemRegex = """<a href="(/videos/[^"]+|/video/\d+-)([^/]+)[^"]* class="preview">(?:<span[^>]+>[^>]+>\W+){0,1}<img (?:alt="([^"]+)")?[^>]+src="([^"]+/)([0-9a-f]+)([0-9a-f]/[^"]+)"[^>]+/>\W+</a><div class='description'>"""
        self.pageNavigationRegex = 'href="(/video[^?"]+\?page_\d*=)(\d+)"'
        self.pageNavigationRegexIndex = 1
        # <a href="(/videos/[^"]+)" class="preview"><img alt="([^"]+)"[^>]+src="([^"]+/)([0-9a-f])(/[^"]+)"[^>]+/>
        # self.folderItemRegex = '<a href="\.([^"]*/)(cat/)(\d+)"( style="color:\s*white;"\s*)*>([^>]+)</a><br'  # used for the CreateFolderItem

        # Test cases:
        # SE: Huset Anubis: paging

        self.mediaUrlRegex = '<param name="src" value="([^"]+)" />'    # used for the UpdateVideoItem
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

        if resultSet[0] == 0:
            title = resultSet[1]
            url = "%s%s" % (self.baseUrl, resultSet[2])
        else:
            title = resultSet[2]
            url = "%s/video/show/%s" % (self.baseUrl, resultSet[1])

        if (title.isupper()):
            title = title.title()

        title = title.strip("!")
        item = mediaitem.MediaItem(title, url)
        item.thumb = self.noImage
        item.icon = self.icon
        item.complete = True

        Logger.Trace(item)
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

        # url = "http://riptide.mtvnn.com/mediagen/%s" % (resultSet[3])
        Logger.Trace(resultSet)
        url = "%s%s%s" % (self.baseUrl, resultSet[0], resultSet[1])
        if resultSet[2]:
            title = resultSet[2]
        else:
            title = resultSet[1].replace("-", " ").title()

        item = mediaitem.MediaItem(title, url)
        item.thumbUrl = "%s%s%s" % (resultSet[3], resultSet[4], resultSet[5])
        item.thumb = self.noImage
        item.icon = self.icon
        item.type = 'video'
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
        data = UriHandler.Open(item.url, pb=False, proxy=self.proxy)

        # get the playlist GUID
        playlistGuid = Regexer.DoRegex("<div[^>]+data-playlist-id='([^']+)'[^>]+></div>", data)[0]
        # Logger.Trace(playlistGuid)

        # now we can get the playlist meta data
        # http://api.mtvnn.com/v2/mrss.xml?uri=mgid%3Asensei%3Avideo%3Amtvnn.com%3Alocal_playlist-39ce0652b0b3c09258d9-SE-uma_site--ad_site-nickelodeon.se-ad_site_referer-video/9764-barjakt&adSite=nickelodeon.se&umaSite={umaSite}&show_images=true&url=http%3A//www.nickelodeon.se/video/9764-barjakt
        # but this seems to work.
        # http://api.mtvnn.com/v2/mrss.xml?uri=mgid%3Asensei%3Avideo%3Amtvnn.com%3Alocal_playlist-39ce0652b0b3c09258d9
        playListUrl = "http://api.mtvnn.com/v2/mrss.xml?uri=mgid%3Asensei%3Avideo%3Amtvnn.com%3Alocal_playlist-" + playlistGuid
        playListData = UriHandler.Open(playListUrl, pb=False, proxy=self.proxy)

        # now get the real RTMP data
        rtmpMetaData = Regexer.DoRegex("<media:content [^>]+url='([^']+)'", playListData)[0]
        rtmpData = UriHandler.Open(rtmpMetaData, pb=False, proxy=self.proxy)

        rtmpUrls = Regexer.DoRegex('<rendition[^>]+bitrate="(\d+)"[^>]*>\W+<src>([^<]+ondemand)/([^<]+)</src>', rtmpData)

        part = item.CreateNewEmptyMediaPart()
        for rtmpUrl in rtmpUrls:
            url = "%s/%s" % (rtmpUrl[1], rtmpUrl[2])
            bitrate = rtmpUrl[0]
            # convertedUrl = url.replace("ondemand/","ondemand?slist=")
            convertedUrl = self.GetVerifiableVideoUrl(url)
            part.AppendMediaStream(convertedUrl, bitrate)

        item.complete = True
        Logger.Trace("Media url: %s", item)
        return item
