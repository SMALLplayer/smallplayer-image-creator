import datetime

import mediaitem
import chn_class

from regexer import Regexer
from logger import Logger
from urihandler import UriHandler


class Channel(chn_class.Channel):
    """
    main class from which all channels inherit
    """

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

        if self.channelCode == '538':
            self.noImage = "radio538image.png"
            self.mainListUri = "http://www.538gemist.nl/"
            self.baseUrl = "http://www.538gemist.nl"

        self.onUpDownUpdateEnabled = True
        self.requiresLogon = False
        self.swfUrl = "http://www.538.nl/jwplayer/player.swf"

        # self.episodeItemRegex = ''
        # self.folderItemRegex = '<li><a href="([^"]+)" ><span>([^<]+)</span></a></li>'
        # self.videoItemRegex = '(?:<img src="([^"]+)"([\w\W]{0,500}?)<p><a href="([^"]+)">([^<]+)</a>|<a href="#([^"]+)" onclick="window.open\(.player.php\?(id=\d+&starttijd=\d+)[^>]+>(\w+) (\d+)-(\d+)-(\d+) \((\d+):(\d+)-(\d+):(\d+)\)<)'
        self.videoItemJson = ('content',)
        self.mediaUrlRegex = '<media:content url="([^"]+)"'

        self.pageNavigationRegex = '<li><a href="([^"]+?)(\d+)" >\d+</a></li>'  # self.pageNavigationIndicationRegex
        self.pageNavigationRegexIndex = 1

        self.contextMenuItems = []
        # self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        # self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
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

        # add live stuff
        live = mediaitem.MediaItem("Live streams", "")
        live.icon = self.icon
        live.thumb = self.noImage
        live.complete = True
        #live.SetDate(2050, 1, 1)

        tv538 = mediaitem.MediaItem("TV 538", "")
        tv538.icon = self.icon
        tv538.thumb = self.noImage
        tv538.AppendSingleStream("rtmp://82.201.53.52:80/livestream/tv538 live=1", 800)
        tv538.type = "video"
        tv538.complete = True
        live.items.append(tv538)

        cam538 = mediaitem.MediaItem("538 Webcam", "")
        cam538.icon = self.icon
        cam538.thumb = self.noImage
        cam538.AppendSingleStream("rtmp://82.201.53.52:80/livestream/live live=1", 800)
        cam538.type = "video"
        cam538.complete = True
        live.items.append(cam538)

        slam = mediaitem.MediaItem("Slam TV", "")
        slam.icon = self.icon
        slam.thumb = self.noImage
        slam.AppendSingleStream("rtmp://video.true.nl/slamtv/slamtv live=1", 800)
        slam.type = "video"
        slam.complete = True
        live.items.append(slam)

        items = []
        data = ""
        items.append(live)

        now = datetime.datetime.now()
        fromDate = now - datetime.timedelta(365)
        Logger.Debug("Showing dates starting from %02d%02d%02d to %02d%02d%02d", fromDate.year, fromDate.month, fromDate.day, now.year, now.month, now.day)
        current = fromDate
        while current <= now:
            url = "http://www.538.nl/ajax/VdaGemistBundle/Gemist/ajaxGemistFilter/date/%02d%02d%02d" % (current.year, current.month, current.day)
            title = "Afleveringen van %02d-%02d-%02d" % (current.year, current.month, current.day)
            dateItem = mediaitem.MediaItem(title, url)
            dateItem.icon = self.icon
            dateItem.thumb = self.noImage
            dateItem.complete = True
            dateItem.httpHeaders = {"X-Requested-With": "XMLHttpRequest"}
            items.append(dateItem)
            current = current + datetime.timedelta(1)

        if returnData:
            # (items, data) = chn_class.Channel.ParseMainList(self, returnData=returnData)
            # items.append(live)
            return (items, data)
        else:
            return items
        return

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

#         if (resultSet[4] == ""):
#             Logger.Trace("Simple audio")
#
#             if not ("vote" in resultSet[1]):
#                 return None
#
#             url = "%s/%s" % (self.baseUrl, resultSet[2])
#             title = resultSet[3]
#             item = mediaitem.MediaItem(title, url)
#             item.type = 'video'
#             item.thumbUrl = resultSet[0]
#         else:
#             Logger.Trace("Playlist audio")
#             # http://www.radio538.nl/gemist/xml2.php?id=1&starttijd=1334808000
#             url = "http://www.radio538.nl/gemist/xml2.php?%s" % (resultSet[5])
#             title = "%s (%s)" % (resultSet[4], resultSet[6])

        title = resultSet.get("title", "Unknown title")
        subTitle = resultSet.get("subtitle_list", "")
        if subTitle:
            title = "%s - %s" % (title, subTitle)

        url = "http://www.538.nl/static/VdaGemistBundle/Feed/xml/idGemist/%s" % (resultSet["id"],)

        item = mediaitem.MediaItem(title, url)
        item.type = 'video'

        dateTime = resultSet.get("time", None)
        if dateTime:
            day = dateTime[0:2]
            month = dateTime[3:5]
            year = dateTime[6:10]
            item.SetDate(year, month, day)

        item.description = resultSet.get("description", "")
        item.thumb = self.noImage
        item.thumbUrl = resultSet.get("image", None)
        item.icon = self.icon
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

        # now the mediaurl is derived. First we try WMV
        data = UriHandler.Open(item.url, pb=False)
        item.MediaItemParts = []
        i = 1
        for part in Regexer.DoRegex(self.mediaUrlRegex, data):
            name = "%s - Deel %s" % (item.name, i)
            mediaPart = mediaitem.MediaItemPart(name, part, 128)
            item.MediaItemParts.append(mediaPart)
            i += 1

        item.complete = True
        return item
