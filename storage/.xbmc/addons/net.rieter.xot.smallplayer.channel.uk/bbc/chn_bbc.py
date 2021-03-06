import xbmc

#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import contextmenu
import chn_class
from locker import LockWithDialog
from config import Config
from helpers import htmlentityhelper
from helpers.xmlhelper import XmlHelper
from helpers import subtitlehelper
from xbmcwrapper import XbmcWrapper
from helpers.languagehelper import LanguageHelper

from regexer import Regexer
from logger import Logger
from urihandler import UriHandler


class Channel(chn_class.Channel):

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

        self.liveUrl = None
        chn_class.Channel.__init__(self, channelInfo)

        # if a proxy was set, set the filter
        if self.proxy:
            self.proxy.Filter = ["mediaselector"]

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

        if self.channelCode == "bbc1":
            self.noImage = "bbc1image.png"
            self.mainListUri = "http://feeds.bbc.co.uk/iplayer/bbc_one/list"
            self.liveUrl = "http://www.bbc.co.uk/mediaselector/4/mtis/stream/bbc_one_london/pc_stream_audio_video_simulcast_uk_v_lm_p006"

        elif self.channelCode == "bbc2":
            self.noImage = "bbc2image.png"
            self.mainListUri = "http://feeds.bbc.co.uk/iplayer/bbc_two/list"
            self.liveUrl = "http://www.bbc.co.uk/mediaselector/4/mtis/stream/bbc_two_england/pc_stream_audio_video_simulcast_uk_v_lm_p006"

        elif self.channelCode == "bbc3":
            self.noImage = "bbc3image.png"
            self.mainListUri = "http://feeds.bbc.co.uk/iplayer/bbc_three/list"
            self.liveUrl = "http://www.bbc.co.uk/mediaselector/4/mtis/stream/bbc_three/pc_stream_audio_video_simulcast_uk_v_lm_p006"

        elif self.channelCode == "bbc4":
            self.noImage = "bbc4image.png"
            self.mainListUri = "http://feeds.bbc.co.uk/iplayer/bbc_four/list"
            self.liveUrl = "http://www.bbc.co.uk/mediaselector/4/mtis/stream/bbc_four/pc_stream_audio_video_simulcast_uk_v_lm_p006"

        elif self.channelCode == "cbbc":
            self.noImage = "cbbcimage.png"
            self.mainListUri = "http://feeds.bbc.co.uk/iplayer/cbbc/list"
            self.liveUrl = "http://www.bbc.co.uk/mediaselector/4/mtis/stream/cbbc/pc_stream_audio_video_simulcast_uk_v_lm_p006"
            #self.liveUrl = "http://www.bbc.co.uk/mediaselector/4/mtis/stream/bbc_three/pc_stream_audio_video_simulcast_uk_v_lm_p006"

        elif self.channelCode == "cbeebies":
            self.noImage = "cbeebiesimage.png"
            self.mainListUri = "http://feeds.bbc.co.uk/iplayer/cbeebies/list"
            self.liveUrl = "http://www.bbc.co.uk/mediaselector/4/mtis/stream/cbeebies/pc_stream_audio_video_simulcast_uk_v_lm_p006"
            #self.liveUrl = "http://www.bbc.co.uk/mediaselector/4/mtis/stream/bbc_four/pc_stream_audio_video_simulcast_uk_v_lm_p006"

        elif self.channelCode == "bbchd":
            self.noImage = "bbchdimage.png"
            self.mainListUri = "http://feeds.bbc.co.uk/iplayer/bbc_hd/list"

        elif self.channelCode == "bbcnews":
            self.noImage = "bbcnewsimage.png"
            self.mainListUri = "http://feeds.bbc.co.uk/iplayer/bbc_news24/list"
            self.liveUrl = "http://www.bbc.co.uk/mediaselector/4/mtis/stream/bbc_news24/pc_stream_audio_video_simulcast_uk_v_lm_p006"

        elif self.channelCode == "bbcparliament":
            self.noImage = "bbcparliamentimage.png"
            self.mainListUri = "http://feeds.bbc.co.uk/iplayer/bbc_parliament/list"
            self.liveUrl = "http://www.bbc.co.uk/mediaselector/4/mtis/stream/bbc_parliament/pc_stream_audio_video_simulcast_uk_v_lm_p006"

        elif self.channelCode == "bbcalba":
            self.noImage = "bbcalbaimage.png"
            self.mainListUri = "http://feeds.bbc.co.uk/iplayer/bbc_alba/list"
            self.liveUrl = "http://www.bbc.co.uk/mediaselector/4/mtis/stream/bbc_alba/pc_stream_audio_video_simulcast_uk_v_lm_p006"

        elif self.channelCode == "bbciplayersearch":
            self.noImage = "bbciplayerimage.png"
            self.mainListUri = ""
        else:
            raise ValueError("No such channelcode", self.channelCode)

        self.baseUrl = "http://www.bbc.co.uk/"
        self.requiresLogon = False
        self.swfUrl = "http://www.bbc.co.uk/emp/releases/iplayer/revisions/617463_618125_4/617463_618125_4_emp.swf"
        self.episodeItemRegex = "(<entry>([\w\W]*?)</entry>)"
        self.videoItemRegex = '<manifest[^>]+>(.+)</manifest>'
        self.folderItemRegex = ''
        self.mediaUrlRegex = ''

        self.searchUrl = "http://feeds.bbc.co.uk/iplayer/search/tv/?q=%s"

        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Test Proxy Server", "CtMnTestProxy", plugin=True))

        #==============================================================================
        # non standard items
        self.programs = dict()

        return True

    #noinspection PyUnusedLocal
    @LockWithDialog(logger=Logger.Instance())
    def CtMnTestProxy(self, item):  # :@UnusedVariable
        """ Checks if the proxy is OK"""

        if not self.proxy:
            message = "Proxy not configured: %s" % (self.proxy, )
        else:
            url = Config.updateUrl + "proxy"
            data = UriHandler.Open(url, proxy=self.proxy)
            # Logger.Trace(data)
            if data == "1":
                message = LanguageHelper.GetLocalizedString(LanguageHelper.ProxyOkId) % (self.proxy, )
            else:
                message = LanguageHelper.GetLocalizedString(LanguageHelper.ProxyNokId) % (self.proxy, )

        Logger.Debug(message)

        XbmcWrapper.ShowDialog("", message)
        pass

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

        if self.channelCode == "bbciplayersearch":
            # clear some stuff
            self.mainListItems = []
            self.programs = dict()
            #noinspection PyArgumentList
            keyboard = xbmc.Keyboard('')
            keyboard.doModal()
            if not keyboard.isConfirmed():
                return None

            needle = keyboard.getText()
            Logger.Info("Searching BBC for needle: %s", needle)
            self.mainListUri = self.searchUrl % (needle,)
        elif len(self.mainListItems) == 0:
            # in case we refreshed, the mainlistitems are empty, so we should
            # clear the program list
            self.programs = dict()

        items = chn_class.Channel.ParseMainList(self, returnData=returnData)
        if self.liveUrl and False:
            item = mediaitem.MediaItem("\bLive TV", self.liveUrl)
            item.icon = self.icon
            item.type = 'folder'
            item.thumb = self.noImage
            item.complete = True

            subItem = mediaitem.MediaItem("%s - Live" % (self.channelName, ), self.liveUrl)
            subItem.icon = self.icon
            subItem.type = 'video'
            subItem.thumb = self.noImage
            subItem.complete = False
            item.items.append(subItem)

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

        # http://www.rtl.nl/system/s4m/xldata/abstract/218927.xml
        xmlData = XmlHelper(resultSet[0])

        title = xmlData.GetSingleNodeContent("title")

        # now get the program out of the title:
        program = Regexer.DoRegex("^(.+?)(: .+|)$", title)[-1][0]
        if program in self.programs:
            # attach the episode to the program
            Logger.Trace("Existing program found: %s", program)
            episodeItem = self.programs[program]
            # do not return, just append
            returnValue = None
        else:
            # create the episode item
            episodeItem = mediaitem.MediaItem(program, "")
            episodeItem.icon = self.icon
            episodeItem.complete = True
            episodeItem.thumb = self.noImage

            # store it for the next items
            self.programs[program] = episodeItem
            # return value is the new episodeitem
            returnValue = episodeItem

        # attach the sub item
        item = self.CreateNestedVideoItem(resultSet)

        # update the main item
        date = xmlData.GetSingleNodeContent("updated")
        year = date[0:4]
        month = date[5:7]
        day = date[8:10]
        item.SetDate(year, month, day)

        # update the date of the new item:
        episodeItem.SetDate(year, month, day, onlyIfNewer=True)
        episodeItem.thumbUrl = item.thumbUrl

        # link them up
        episodeItem.items.append(item)
        item.parent = episodeItem

        return returnValue

    def CreateLiveVideoItem(self, resultSet):
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

        # only used for live TV
        live = mediaitem.MediaItem("%s - Live" % (self.channelName, ), None, type="video")
        live.complete = True
        live.icon = self.icon
        live.thumb = self.noImage
        liveRegex = '<media[^>]+href="([^"]+)"[^>]+bitrate="([^"]+)"[^>]*/>'

        livePart = live.CreateNewEmptyMediaPart()
        streams = Regexer.DoRegex(liveRegex, resultSet)
        for stream in streams:
            # .replace("_definst_", "?slist=").replace("http:", "rtmp:")
            livePart.AppendMediaStream(stream[0], stream[1])

        Logger.Trace("Added live item: %s", live)
        return live

    def CreateNestedVideoItem(self, resultSet):
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

        xmlData = XmlHelper(resultSet[0])
        title = xmlData.GetSingleNodeContent("title")

        # http://www.bbc.co.uk/iplayer/images/episode/b014gsgn_512_288.jpg
        thumb = xmlData.GetTagAttribute("media:thumbnail", {'url': None})
        thumb = thumb[0:thumb.index("_")] + "_512_288.jpg"
        if thumb == "":
            thumb = self.noImage

        # description
        # TODO
        description = xmlData.GetSingleNodeContent("content").split("\n")
        description = description[len(description) - 3].strip()

        # id
        videoId = xmlData.GetSingleNodeContent("id")[-8:]
        # Logger.Trace(id)

        url = "http://www.bbc.co.uk/iplayer/playlist/%s" % (videoId,)

        item = mediaitem.MediaItem(title, url)
        item.icon = self.icon
        item.description = description
        item.type = 'video'
        item.thumb = self.noImage
        item.thumbUrl = thumb
        item.complete = False
        return item

    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item.
        """
        Logger.Debug('Starting UpdateVideoItem for %s (%s)', item.name, self.channelName)

        liveNeedle = "http://www.bbc.co.uk/mediaselector/4/mtis/stream/"
        liveStream = False
        if not liveNeedle in item.url:
            metaData = UriHandler.Open(item.url, pb=False, proxy=self.proxy)

            xmlMetaData = XmlHelper(metaData)
            # <item kind="programme" duration="3600" identifier="b014r5hj" group="b014r5jm" publisher="pips">
            videoIds = xmlMetaData.GetTagAttribute("item", {'kind': 'programme'}, {'identifier': None}, firstOnly=False)
        else:
            videoIds = [item.url.replace(liveNeedle, "")]
            liveStream = True

        for videoId in videoIds:
            Logger.Debug("Found videoId: %s", videoId)
            # foreach ID add a part
            part = item.CreateNewEmptyMediaPart()

            streamDataUrl = "http://www.bbc.co.uk/mediaselector/4/mtis/stream/%s" % (videoId, )
            streamData = UriHandler.Open(streamDataUrl, pb=False, proxy=self.proxy)
            # Logger.Trace(streamData)

            connectionDatas = Regexer.DoRegex('<media bitrate="(\d+)"[^>]+>\W*(<connection[^>]+>)\W*(<connection[^>]+>)*\W*</media>', streamData)
            for connectionData in connectionDatas:
                Logger.Trace(connectionData)
                # first the bitrate
                bitrate = connectionData[0]
                Logger.Debug("Found bitrate       : %s", bitrate)

                # go through the available connections
                for connection in connectionData[1:3]:
                    if not connection:
                        continue

                    connectionXml = XmlHelper(connection)
                    Logger.Debug("Analyzing: %s", connection)

                    # port: we take the default one
                    # determine protocol
                    protocol = connectionXml.GetTagAttribute("connection", {"protocol": None})
                    if protocol == "http":
                        Logger.Debug("Http stream found, skipping for now.")
                        continue

                    elif protocol == "":
                        protocol = "rtmp"
                    Logger.Debug("Found protocol      : %s", protocol)

                    # now for the non-http version, we need application, authentication, server, file and kind
                    application = connectionXml.GetTagAttribute("connection", {"application": None})
                    if application == "":
                        application = "ondemand"
                    Logger.Debug("Found application   : %s", application)

                    authentication = connectionXml.GetTagAttribute("connection", {"authString": None})
                    authentication = htmlentityhelper.HtmlEntityHelper.ConvertHTMLEntities(authentication)
                    Logger.Debug("Found authentication: %s", authentication)

                    server = connectionXml.GetTagAttribute("connection", {"server": None})
                    Logger.Debug("Found server        : %s", server)

                    fileName = connectionXml.GetTagAttribute("connection", {"identifier": None})
                    Logger.Debug("Found identifier    : %s", fileName)

                    kind = connectionXml.GetTagAttribute("connection", {"kind": None})
                    Logger.Debug("Found kind          : %s", kind)
                    if "akamai" in kind:
                        Logger.Debug("Not including AKAMAI streams")
                        continue
                        #url = "%s://%s/%s?%s playpath=%s?%s" % (protocol, server, application, authentication, fileName, authentication)
                        #Logger.Debug("Creating RTMP for Akamai type\n%s", url)

                    # Logger.Trace("XML: %s\nProtocol: %s, Server: %s, Application: %s, Authentication: %s, File: %s , Kind: %s", connection, protocol, server, application, authentication, fileName, kind)
                    elif kind == "limelight":
                        # for limelight we need to be more specific on what to play
                        url = "%s://%s/ app=%s?%s tcurl=%s://%s/%s?%s playpath=%s" % (protocol, server, application, authentication, protocol, server, application, authentication, fileName)
                        Logger.Debug("Creating RTMP for LimeLight type\n%s", url)
                    else:
                        # for a none-limelight we just compose a RTMP stream
                        url = "%s://%s/%s?%s playpath=%s" % (protocol, server, application, authentication, fileName)
                        Logger.Debug("Creating RTMP for a None-LimeLight type\n%s", url)
                    url = self.GetVerifiableVideoUrl(url)

                    if liveStream:
                        url = "%s live=1" % (url, )
                    part.AppendMediaStream(url, bitrate)

            # get the subtitle
            subtitles = Regexer.DoRegex('<connection href="(http://www.bbc.co.uk/iplayer/subtitles/[^"]+/)([^/]+.xml)"', streamData)
            if len(subtitles) > 0:
                subtitle = subtitles[0]
                subtitleUrl = "%s%s" % (subtitle[0], subtitle[1])
                part.Subtitle = subtitlehelper.SubtitleHelper.DownloadSubtitle(subtitleUrl, subtitle[1], "ttml", proxy=self.proxy)

        if item.thumbUrl != "":
            item.thumb = self.CacheThumb(item.thumbUrl)
        item.complete = True

        Logger.Trace('finishing UpdateVideoItem: %s.', item)
        return item
