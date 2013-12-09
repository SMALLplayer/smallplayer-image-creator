# coding:Cp1252

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
        """
        Used for the initialisation of user defined parameters. All should be
        present, but can be adjusted
        """
        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self, channelInfo)

        if self.channelCode == "redactie":
            self.noImage = "redactieimage.png"
            self.mainListUri = "http://www.deredactie.be/cm/vrtnieuws/videozone"
            self.baseUrl = "http://www.deredactie.be"

        elif self.channelCode == "sporza":
            self.noImage = "sporzaimage.png"
            self.mainListUri = "http://www.sporza.be/cm/sporza/videozone"
            self.baseUrl = "http://www.sporza.be"

        elif self.channelCode == "ketnet":
            self.noImage = "ketnetimage.png"
            self.mainListUri = "http://video.ketnet.be/cm/ketnet/ketnet-mediaplayer"
            self.baseUrl = "http://video.ketnet.be"

        elif self.channelCode == "cobra":
            self.noImage = "cobraimage.png"
            self.mainListUri = "http://www.cobra.be/cm/cobra/cobra-mediaplayer"
            self.baseUrl = "http://www.cobra.be"

        self.swfUrl = "%s/html/flash/common/player.5.10.swf" % (self.baseUrl,)
        # self.episodeItemRegex = '<li[^>]*>\W*<a href="(/cm/[^"]+/videozone/[^"]+/[^"]+)" title="([^"]+)"\W*>'  # used for the ParseMainList
        self.episodeItemRegex = '<li[^>]*>\W*<a href="(/cm/[^"]+/videozone/programmas/[^"]+)" title="([^"]+)"\W*>'  # used for the ParseMainList
        # self.videoItemRegex = '<a href="(/cm/[^/]+/videozone/programmas/[^?"]+)" rel="videoplayer">\W*<span[^>]+>([^<]+)</span>\W*<span class="video">\W*<img src="([^"]+)"'
        self.videoItemRegex = ('<a href="(/cm/[^/]+/videozone/programmas/[^?"]+)" rel="videoplayer">\W*<span[^>]+>([^<]+)</span>\W*(?:<span[^<]+</span>\W*){0,2}<span class="video">\W*<img src="([^"]+)"', '<a href="(/cm/[^/]+/videozone/[^?"]+)" >([^<]+)</a>')
        #self.videoItemRegex = ('<a href="(/cm/[^/]+/videozone/[^?"]+)" rel="videoplayer">\W*<span[^>]+>([^<]+)</span>\W*<span[^>]+>\W*<img src="([^"]+)"', '<a href="(/cm/[^/]+/videozone/[^?"]+)" >([^<]+)</a>')
        self.mediaUrlRegex = 'data-video-((?:src|rtmp|iphone|mobile)[^=]*)="([^"]+)"\W+(?:data-video-[^"]+path="([^"]+)){0,1}'
        self.pageNavigationRegex = '<a href="([^"]+\?page=\d+)"[^>]+>(\d+)'
        self.pageNavigationRegexIndex = 1

        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
        return True

    def PreProcessFolderList(self, data):

        # Only get the first bit
        seperatorIndex = data.find('<div class="splitter split24">')
        data = data[:seperatorIndex]

        return chn_class.Channel.PreProcessFolderList(self, data)

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

        url = "%s%s" % (self.baseUrl, resultSet[0])
        name = resultSet[1]

        item = mediaitem.MediaItem(name.capitalize(), url)
        item.icon = self.icon
        item.type = "folder"
        item.complete = True
        return item

    def CreateFolderItem(self, resultSet):
        """Creates a MediaItem of type 'folder' using the resultSet from the regex.

        Arguments:
        resultSet : tuple(strig) - the resultSet of the self.folderItemRegex

        Returns:
        A new MediaItem of type 'folder'

        This method creates a new MediaItem from the Regular Expression
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        """

        Logger.Trace(resultSet)
        item = None
        # not implemented yet
        return item

    def CreateVideoItem(self, resultSet):
        """Creates a MediaItem of type 'video' using the resultSet from the regex.

        Arguments:
        resultSet : tuple (string) - the resultSet of the self.videoItemRegex

        Returns:
        A new MediaItem of type 'video' or 'audio' (despite the method's name)

        This method creates a new MediaItem from the Regular Expression
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        If the item is completely processed an no further data needs to be fetched
        the self.complete property should be set to True. If not set to True, the
        self.UpdateVideoItem method is called if the item is focused or selected
        for playback.

        """

        Logger.Trace(resultSet)

        if resultSet[0] == 0:
            name = resultSet[2]
            url = "%s%s" % (self.baseUrl, resultSet[1])
            thumb = resultSet[3]
        else:
            name = resultSet[2]
            url = "%s%s" % (self.baseUrl, resultSet[1])
            thumb = ""

        if thumb and not thumb.startswith("http://"):
            thumb = "%s%s" % (self.baseUrl, thumb)

        item = mediaitem.MediaItem(name, url)
        item.thumb = self.noImage
        item.thumbUrl = thumb
        item.description = name
        item.icon = self.icon
        item.type = 'video'
        item.complete = False

        if name[-3] == name[-6] == "/":
            Logger.Debug("Found possible date in name")
            year = int(name[-2:]) + 2000
            month = name[-5:-3]
            day = name[-8:-6]
            Logger.Trace("%s - %s - %s", year, month, day)
            item.SetDate(year, month, day)

        return item

    #=============================================================================
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. Usually retrieves the MediaURL
        and the Thumb! It should return a completed item.
        """
        Logger.Debug('Starting UpdateVideoItem for %s (%s)', item.name, self.channelName)

        item.thumb = self.CacheThumb(item.thumbUrl)

        """
        data-video-id="1613274"
        data-video-type="video"
        data-video-src="http://media.vrtnieuws.net/2013/04/135132051ONL1304255866693.urlFLVLong.flv"
        data-video-title="Het journaal 1 - 25/04/13"
        data-video-rtmp-server="rtmp://vrt.flash.streampower.be/vrtnieuws"
        data-video-rtmp-path="2013/04/135132051ONL1304255866693.urlFLVLong.flv"
        data-video-rtmpt-server="rtmpt://vrt.flash.streampower.be/vrtnieuws"
        data-video-rtmpt-path="2013/04/135132051ONL1304255866693.urlFLVLong.flv"
        data-video-iphone-server="http://iphone.streampower.be/vrtnieuws_nogeo/_definst_"
        data-video-iphone-path="2013/04/135132051ONL1304255866693.urlMP4_H.264.m4v"
        data-video-mobile-server="rtsp://mp4.streampower.be/vrt/vrt_mobile/vrtnieuws_nogeo"
        data-video-mobile-path="2013/04/135132051ONL1304255866693.url3GP_MPEG4.3gp"
        data-video-sitestat-program="het_journaal_1_-_250413_id_1-1613274"
        """

        # now the mediaurl is derived. First we try WMV
        data = UriHandler.Open(item.url, pb=False)

        descriptions = Regexer.DoRegex('<div class="longdesc"><p>([^<]+)</', data)
        Logger.Trace(descriptions)
        for desc in descriptions:
            item.description = desc

        data = data.replace("\\/", "/")
        urls = Regexer.DoRegex(self.mediaUrlRegex, data)
        part = item.CreateNewEmptyMediaPart()
        for url in urls:
            Logger.Trace(url)
            if url[0] == "src":
                flv = url[1]
                bitrate = 800
            else:
                flvServer = url[1]
                flvPath = url[2]

                if url[0] == "rtmp-server":
                    flv = "%s//%s" % (flvServer, flvPath)
                    bitrate = 750

                elif url[0] == "rtmpt-server":
                    continue
                    flv = "%s//%s" % (flvServer, flvPath)
                    flv = self.GetVerifiableVideoUrl(flv)
                    bitrate = 1500

                elif url[0] == "iphone-server":
                    flv = "%s/%s" % (flvServer, flvPath)
                    iData = UriHandler.Open("%s/playlist.m3u8" % (flv,), proxy=self.proxy)
                    Logger.Trace(iData)
                    iphoneUrls = Regexer.DoRegex('BANDWIDTH=(\d+)\d{3}[^\n]+\W+([^\n]+.m3u8\?wowzasessionid=\d+)', iData)
                    for iphoneUrl in iphoneUrls:
                        m3u8 = iphoneUrl[1]
                        bitrate = iphoneUrl[0]
                        part.AppendMediaStream("%s/%s" % (flv, m3u8), bitrate)
                    # no need to continue adding the streams
                    continue

                elif url[0] == "mobile-server":
                    flv = "%s/%s" % (flvServer, flvPath)
                    bitrate = 250

                else:
                    flv = "%s/%s" % (flvServer, flvPath)
                    bitrate = 0

            part.AppendMediaStream(flv, bitrate)

        item.complete = True
#             server = url[0]
#             path = url[1]
#
#             if server != "":
#                 if server.startswith("rtmp:") or server.startswith("rtmpt:"):
#                     mediaUrl = "%s//%s" % (server, path)
#                     mediaUrl = self.GetVerifiableVideoUrl(mediaUrl)
#                     part.AppendMediaStream(mediaUrl, 800)
#                 elif "_definst_" in server:
#                     continue
# #                    #http://iphone.streampower.be/vrtnieuws_nogeo/_definst_/2011/07/151204967HOORENSVL2123520.urlMP4_H.264.m4v/playlist.m3u8
# #                    bitrate = 1200
# #                    mediaurl = mediaurl.replace("definst_//", "definst_/")+"/playlist.m3u8"
# #                    mobileData = UriHandler.Open(mediaurl, pb=False)
# #                    mobileUrls = Regexer.DoRegex("BANDWIDTH=(\d+)\d{3}\W+(http://[^\n]+)", mobileData)
# #                    for mobileUrl in mobileUrls:
# #                        part.AppendMediaStream(mobileUrl[1], mobileUrl[0])
#                 else:
#                     mediaUrl = "%s/%s" % (server, path)
#                     part.AppendMediaStream(mediaUrl, 100)
#                 item.complete = True
#        else:
#            Logger.Debug("Media url was not found.")

        return item
