import mediaitem
import chn_class

from regexer import Regexer
from helpers.datehelper import DateHelper

from logger import Logger
from urihandler import UriHandler


class Channel(chn_class.Channel):
    #===============================================================================
    # define class variables
    #===============================================================================
    def InitialiseVariables(self, channelInfo):
        """
        Used for the initialisation of user defined parameters. All should be
        present, but can be adjusted
        """
        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self, channelInfo)

        self.mainListUri = "http://twit.tv/shows"
        self.baseUrl = "http://twit.tv"

        self.episodeItemRegex = '<img src="([^"]+)"[^>]*></a>\W*</span>\W*</span>\W*<span[^<]+<span[^<]+<a href="/(show/\d+/latest)">([^<]+)'
        self.videoItemRegex = '<div class="date">(\w+) (\d+)\w+, (\d+)</div>\W+<div[^>]*><a href="([^"]+)"[^>]*>([^<]+)</a></div>\W+<div[^>]*><p>([^<]+)'
        self.mediaUrlRegex = '<a class="[^"]+ download" href="(http://[^"]+_(\d+).mp4)"'

        # self.pageNavigationRegexBase = '<a href="([^"]+%s&amp;sida=)\d+"\W+data[\W\w]{0,100}lastpage="(\d+)"'
        # self.pageNavigationRegex = self.pageNavigationRegexBase % "episodes"
        # self.pageNavigationRegexIndex = 1

        """
            Testcases:

        """

        self.noImage = "twitimage.png"
        self.requiresLogon = False

        return True

    def ParseMainList(self, returnData=False):
        items = chn_class.Channel.ParseMainList(self, returnData=returnData)

        item = mediaitem.MediaItem(".: TWiT.TV Live :.", "http://live.twit.tv/")
        item.thumb = self.noImage
        item.icon = self.icon
        item.complete = True

        playbackItem = mediaitem.MediaItem("Play Live", "http://live.twit.tv/")
        playbackItem.type = "playlist"
        playbackItem.thumb = self.noImage
        playbackItem.icon = self.icon
        playbackPart = playbackItem.CreateNewEmptyMediaPart()

        """
        BitGravity
        There are two streams available from BitGravity; a 512 kbps low-bandwidth stream
        and a 1 Mbps high-bandwidth stream.

        UStream
        This is the default stream. The UStream stream is a variable stream that maxes at
        2.2 Mbps and adjusts down based on your bandwidth.
        Justin.tv

        The Justin.tv stream is a 2.2 mbps high-bandwidth stream that will adjust to lower
        bandwidth and resolutions.

        Flosoft.biz
        The Flosoft.biz stream is a 5 resolution/bitrate HLS stream, intended for our app developers.
        Please see Flosoft Developer Section. This stream is hosted by TWiT through Flosoft.biz
        """

        # http://wiki.twit.tv/wiki/TWiT_Live#Direct_links_to_TWiT_Live_Video_Streams
        mediaUrls = {
                    # Justin TV
                    # "2000": "http://usher.justin.tv/stream/multi_playlist/twit.m3u8",

                    # Flosoft (http://wiki.twit.tv/wiki/Developer_Guide#Flosoft.biz)
                    "264": "http://hls.cdn.flosoft.biz/flosoft/mp4:twitStream_240/playlist.m3u8",
                    "512": "http://hls.cdn.flosoft.biz/flosoft/mp4:twitStream_360/playlist.m3u8",
                    "1024": "http://hls.cdn.flosoft.biz/flosoft/mp4:twitStream_480/playlist.m3u8",
                    "1475": "http://hls.cdn.flosoft.biz/flosoft/mp4:twitStream_540/playlist.m3u8",
                    "1778": "http://hls.cdn.flosoft.biz/flosoft/mp4:twitStream_720/playlist.m3u8",

                    # UStream
                    "1524": "http://iphone-streaming.ustream.tv/ustreamVideo/1524/streams/live/playlist.m3u8",

                    # BitGravity
                    # "512": "http://209.131.99.99/twit/live/low",
                    # "1024": "http://209.131.99.99/twit/live/high",
                    #"512": "http://64.185.191.180/cdn-live-s1/_definst_/twit/live/low/playlist.m3u8",
                    #"1024": "http://64.185.191.180/cdn-live-s1/_definst_/twit/live/high/playlist.m3u8",
                    }

        for bitrate in mediaUrls:
            playbackPart.AppendMediaStream(mediaUrls[bitrate], bitrate)

        Logger.Debug("Streams: %s", playbackPart)
        playbackItem.complete = True
        item.items.append(playbackItem)
        Logger.Debug("Appended: %s", playbackItem)

        items.append(item)
        return items

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

        url = "%s/%s" % (self.baseUrl, resultSet[1])
        item = mediaitem.MediaItem(resultSet[2], url)

        item.thumb = self.noImage
        item.thumbUrl = resultSet[0]
        if not item.thumbUrl.startswith("http"):
            item.thumbUrl = "%s%s" % (self.baseUrl, item.thumbUrl)
        item.thumbUrl = item.thumbUrl.replace("coverart-small", "coverart")

        item.icon = self.icon
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

        url = resultSet[3]
        if not url.startswith("http"):
            url = "%s%s" % (self.baseUrl, url)
        name = resultSet[4]
        description = resultSet[5]

        item = mediaitem.MediaItem(name, url)
        item.description = description
        item.type = 'video'
        item.icon = self.icon
        item.thumb = self.noImage

        month = resultSet[0]
        month = DateHelper.GetMonthFromName(month, "en", False)
        day = resultSet[1]
        year = resultSet[2]
        item.SetDate(year, month, day)

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

        data = UriHandler.Open(item.url, pb=False, proxy=self.proxy)
        streams = Regexer.DoRegex(self.mediaUrlRegex, data)

        item.MediaItemParts = []
        part = item.CreateNewEmptyMediaPart()
        for stream in streams:
            Logger.Trace(stream)
            part.AppendMediaStream(stream[0], stream[1])

        item.thumb = self.CacheThumb(item.thumbUrl)
        item.complete = True
        return item
