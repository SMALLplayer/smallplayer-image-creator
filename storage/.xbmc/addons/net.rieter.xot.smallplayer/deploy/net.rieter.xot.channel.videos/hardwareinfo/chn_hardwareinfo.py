#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
# import contextmenu
import chn_class
import contextmenu
from helpers import xmlhelper
from helpers import stopwatch
from helpers import htmlentityhelper

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

    def InitialiseVariables(self, channelInfo):
        """
        Used for the initialisation of user defined parameters. All should be
        present, but can be adjusted
        """

        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self, channelInfo)

        self.mainListUri = "http://gdata.youtube.com/feeds/api/users/hardwareinfovideo/uploads?max-results=1&start-index=1"
        self.baseUrl = "http://www.youtube.com"
        self.noImage = "hardwareinfoimage.png"

        self.requiresLogon = False

        self.episodeItemRegex = '<name>([^-]+) - (\d+)-(\d+)-(\d+)[^<]*</name>'
        self.videoItemRegex = '<entry>([\w\W]+?)</entry>'
        self.folderItemRegex = ''
        self.mediaUrlRegex = ''

        """
            The ProcessPageNavigation method will parse the current data using the pageNavigationRegex. It will
            create a pageItem using the CreatePageItem method. If no CreatePageItem method is in the channel,
            a default one will be created with the number present in the resultset location specified in the
            pageNavigationRegexIndex and the url from the combined resultset. If that url does not contain http://
            the self.baseUrl will be added.
        """
        self.pageNavigationIndicationRegex = '<page>(\d+)</page>'
        self.pageNavigationRegex = '<page>(\d+)</page>'
        self.pageNavigationRegexIndex = 0

        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownload", itemTypes="video", completeStatus=True, plugin=True))

        # http://en.wikipedia.org/wiki/YouTube#Quality_and_codecs
        self.YouTubeEncodings = {
                # Flash Video
                5: [314, "flv", "240p", "Sorenson H.263", "N/A", "0.25", "MP3", "64"],
                6: [864, "flv", "270p", "Sorenson H.263", "N/A", "0.8", "MP3", "64"],
                34: [628, "flv", "360p", "H.264", "Main", "0.5", "AAC", "128"],
                35: [1028, "flv", "480p", "H.264", "Main", "0.8-1", "AAC", "128"],

                # 3GP
                36: [208, "3gp", "240p", "MPEG-4 Visual", "Simple", "0.17", "AAC", "38"],
                13: [500, "3gp", "N/A", "MPEG-4 Visual", "N/A", "0.5", "AAC", "N/A"],
                17: [74, "3gp", "144p", "MPEG-4 Visual", "Simple", "0.05", "AAC", "24"],

                # MPEG-4
                18: [596, "mp4", "360p", "H.264", "Baseline", "0.5", "AAC", "96"],
                22: [2792, "mp4", "720p", "H.264", "High", "2-2.9", "AAC", "192"],
                37: [3800, "mp4", "1080p", "H.264", "High", "3-4.3", "AAC", "192"],
                38: [4500, "mp4", "3072p", "H.264", "High", "3.5-5", "AAC", "192"],
                82: [596, "mp4", "360p", "H.264", "3D", "0.5", "AAC", "96"],
                83: [596, "mp4", "240p", "H.264", "3D", "0.5", "AAC", "96"],
                84: [2752, "mp4", "720p", "H.264", "3D", "2-2.9", "AAC", "152"],
                85: [2752, "mp4", "520p", "H.264", "3D", "2-2.9", "AAC", "152"],

                # WebM
                43: [628, "webm", "360p", "VP8", "N/A", "0.5", "Vorbis", "128"],
                44: [1128, "webm", "480p", "VP8", "N/A", "1", "Vorbis", "128"],
                45: [2192, "webm", "720p", "VP8", "N/A", "2", "Vorbis", "192"],
                # 46: ["webm", "1080p", "VP8", "N/A", "N/A", "Vorbis", "192"],
                # 100: ["webm", "360p", "VP8", "3D", "N/A", "Vorbis", "128"],
                # 101: ["webm", "360p", "VP8", "3D", "N/A", "Vorbis", "192"],
                # 102: ["webm", "720p", "VP8", "3D", "N/A", "Vorbis", "192"]
            }
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

        if len(self.mainListItems) > 1:
            if self.episodeSort:
                # just resort again
                self.mainListItems.sort()

            if returnData:
                return (self.mainListItems, "")
            else:
                return self.mainListItems

        items = []

        # we need to create page items. So let's just spoof the paging. Youtube has
        # a 50 max results per query limit.
        itemsPerPage = 50
        data = UriHandler.Open(self.mainListUri, proxy=self.proxy)
        xml = xmlhelper.XmlHelper(data)
        nrItems = xml.GetSingleNodeContent("openSearch:totalResults")

        for index in range(1, int(nrItems), itemsPerPage):
            items.append(self.CreateEpisodeItem([index, itemsPerPage]))
            pass
        # Continue working normal!

        # sort by name
        if self.episodeSort:
            watch = stopwatch.StopWatch('Sort Timer', Logger.Instance())
            items.sort()  # lambda x, y: cmp(x.name.lower(), y.name.lower()))
            watch.Stop()

        self.mainListItems = items

        if returnData:
            return (items, data)
        else:
            return items

    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item.
        """

        url = "http://gdata.youtube.com/feeds/api/users/hardwareinfovideo/uploads?max-results=%s&start-index=%s" % (resultSet[1], resultSet[0])
        title = "Hardware Info TV %04d-%04d" % (resultSet[0], resultSet[0] + resultSet[1])
        item = mediaitem.MediaItem(title, url)
        item.complete = True
        item.icon = self.icon
        item.thumb = self.noImage
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

        xmlData = xmlhelper.XmlHelper(resultSet)

        title = xmlData.GetSingleNodeContent("title")

        # Retrieve an ID and create an URL like: http://www.youtube.com/get_video_info?hl=en_GB&asv=3&video_id=OHqu64Qnz9M
        videoId = xmlData.GetSingleNodeContent("id")
        lastSlash = videoId.rfind("/") + 1
        videoId = videoId[lastSlash:]
        url = "http://www.youtube.com/get_video_info?hl=en_GB&asv=3&video_id=%s" % (videoId,)

        item = mediaitem.MediaItem(title, url)
        item.icon = self.icon
        item.type = 'video'

        # date stuff
        date = xmlData.GetSingleNodeContent("published")
        year = date[0:4]
        month = date[5:7]
        day = date[8:10]
        hour = date[11:13]
        minute = date[14:16]
        # Logger.Trace("%s-%s-%s %s:%s", year, month, day, hour, minute)
        item.SetDate(year, month, day, hour, minute, 0)

        # description stuff
        description = xmlData.GetSingleNodeContent("media:description")
        item.description = description

        # thumbnail stuff
        thumbUrl = xmlData.GetTagAttribute("media:thumbnail", {'url': None}, {'height': '360'})
        # <media:thumbnail url="http://i.ytimg.com/vi/5sTMRR0_Wo8/0.jpg" height="360" width="480" time="00:09:52.500" xmlns:media="http://search.yahoo.com/mrss/" />
        if thumbUrl != "":
            item.thumbUrl = thumbUrl
        item.thumb = self.noImage

        # finish up
        item.complete = False
        return item

    def UpdateVideoItem(self, item):
        """
        Accepts an arraylist of results. It returns an item.
        """

        data = UriHandler.Open(item.url, pb=False)
        # get the stream data from the page
        urlEncodedFmtStreamMap = Regexer.DoRegex("url_encoded_fmt_stream_map=([^&]+)", data)
        urlEncodedFmtStreamMapData = htmlentityhelper.HtmlEntityHelper.UrlDecode(urlEncodedFmtStreamMap[0])
        # split per stream
        streams = urlEncodedFmtStreamMapData.split(',')
        Logger.Trace(streams)

        part = None
        for stream in streams:
            # let's create a new part
            qsData = dict([x.split("=") for x in stream.split("&")])
            Logger.Trace(qsData)

            if part is None:
                part = item.CreateNewEmptyMediaPart()

            # get the stream encoding information from the iTag
            iTag = int(qsData.get('itag', -1))
            streamEncoding = self.YouTubeEncodings.get(iTag, None)
            if (streamEncoding is None):
                # if the iTag was not in the list, skip it.
                Logger.Debug("Not using iTag %s as it is not in the list of supported encodings.", iTag)
                continue

            bitrate = streamEncoding[0]
            signature = qsData['sig']
            quality = qsData['quality']
            videoUrl = htmlentityhelper.HtmlEntityHelper.UrlDecode(qsData['url'])
            url = "%s&signature=%s&quality=%s&ext=.%s" % (videoUrl, signature, quality, streamEncoding[1])

            part.AppendMediaStream(url, bitrate)

        item.thumb = self.CacheThumb(item.thumbUrl)
        item.complete = True
        return item

    def CtMnDownload(self, item):
        """ downloads a video item and returns the updated one
        """
        item = self.DownloadVideoItem(item)
