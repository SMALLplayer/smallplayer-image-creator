import mediaitem
import chn_class

from regexer import Regexer
from urihandler import UriHandler
from logger import Logger
from helpers.jsonhelper import JsonHelper


class Channel(chn_class.Channel):
    """
    main class from which all channels inherit
    """

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

        self.videoType = None
        chn_class.Channel.__init__(self, channelInfo)

    def InitialiseVariables(self, channelInfo):
        """
        Used for the initialisation of user defined parameters. All should be 
        present, but can be adjusted
        """
        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self, channelInfo)
        
        self.noImage = "eredivisieimage.png"
        self.baseUrl = "http://foxsports.nl/"
        self.mainListUri = "http://foxsports.nl/videos/"
        self.swfUrl = "http://static.eredivisielive.nl/static/swf/edPlayer-1.6.2.plus.swf"
        
        self.episodeItemRegex = '<option[^>]+value="([^"]+)"[^=>]+(?:data-season="([^"]+)")?[^=>]*>([^<]+)</option>'
        #self.videoItemRegex = '<li class="video-item">\W+<a href="/video/(\d+)[^"]+">[\w\W]+?<img src="([^"]+)" [^>]+title="([^"]+)" />\W+<span class="date">(?:(\d+) (\w+) (\d+)|(vandaag|gisteren)) \w+ (\d+):(\d+)'
        self.mediaUrlRegex = 'BANDWIDTH=(\d+)\d{3}\W+([^\n]+.m3u8)'
        self.videoItemJson = ("item",)
        
        self.pageNavigationRegex = ''
        self.pageNavigationRegexIndex = 1
            
        self.onUpDownUpdateEnabled = True
        self.requiresLogon = False
        
        self.contextMenuItems = []        
        return True

    def PreProcessFolderList(self, data):
        """Performs pre-process actions for data processing

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
        if "type=" not in self.parentItem.url:
            Logger.Info("Initial listing, let's only show the types")
            jsonData = JsonHelper(data)

            types = set()
            for item in jsonData.GetValue("item"):
                if "login" in item['rights']:
                    continue
                types.add(item["type"] or "Other")
            Logger.Trace(types)

            for videoType in types:
                url = "%s&type=%s" % (self.parentItem.url, videoType.replace(" ", "").lower())
                item = mediaitem.MediaItem(videoType, url)
                item.thumb = self.noImage
                item.icon = self.icon
                items.append(item)

            # no need for futher processing
            data = ""
        else:
            self.videoType = self.parentItem.url[self.parentItem.url.rindex("=") + 1:]
            Logger.Info("Typed listing, let's only show videos for a specific type: %s", self.videoType)

        Logger.Debug("Pre-Processing finished")
        return data, items

    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """

        Logger.Trace(resultSet)

        title = resultSet[2]

        if resultSet[1]:
            # competition item
            if len(resultSet[1]) > 4:
                title = "%s (%s)" % (title.strip(), resultSet[1][-4:])
            else:
                title = "%s (%s)" % (title.strip(), resultSet[1])
        else:
            return None

        url = "http://api.foxsports.nl/videos/competition/%s/?offset=0&pagesize=200" % (resultSet[0])
        
        item = mediaitem.MediaItem(title, url)
        item.icon = self.icon
        item.thumb = self.noImage
        item.thumbUrl = self.noImage
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

        #{
        #    u'video_id': 88152,
        #    u'match_id': 1796070,
        #    u'title': u'SamenvattingFCBayernM\xfcnchen-Hannover96',
        #    u'views': 3101,
        #    u'timestamp': u'2013-09-26T00: 08: 01+02: 00',
        #    u'image': u'http: //cdn.fxsprts.nl/images/2013/09/26/{
        #        size
        #    }/119508.jpg',
        #    u'rights': [u'login'],
        #    u'duration': 310,
        #    u'is_ccast': False,
        #    u'streams': {
        #        u'android': u'http: //lb.streamgate.nl/LB/redirect.rtsp?_definst_/content1/eredivisie/geo_nl/2013/09/26/END_88152_E.mp4',
        #        u'normal': u'http: //lb-s.streamgate.nl/vod/_definst_/content1/eredivisie/geo_nl/2013/09/26/88152.smil/playlist.m3u8'
        #    },
        #    u'content_type': u'video',
        #    u'sociallink': u'http: //foxsports.nl/video/158698',
        #    u'date': u'2013-09-2600: 08: 01',
        #    u'publication_date': u'26-09-2013,
        #    00: 08',
        #    u'content_id': 158698,
        #    u'type': u'Samenvatting',
        #    u'id': 158698,
        #    u'description': u''
        #}

        videoType = (resultSet.get("type") or "Other").replace(" ", "").lower()
        if not self.videoType == videoType:
            Logger.Trace("Found item with invalid type: was %s should be %s", videoType, self.videoType.lower())
            return None

        name = resultSet.get("title")
        url = resultSet["streams"].get("normal")

        if "login" in resultSet['rights']:
            Logger.Warning("Found item with login rights, not showing: %s", name)
            return None

        item = mediaitem.MediaItem(name, url, "video")
        item.description = resultSet.get("description")
        item.icon = self.icon
        item.thumb = self.noImage
        item.thumbUrl = resultSet.get("image")
        if item.thumbUrl and "{size}" in item.thumbUrl:
            item.thumbUrl = item.thumbUrl.replace("{size}", "640x360")

        dateString = resultSet.get('date')
        if dateString:
            year = dateString[0:4]
            month = dateString[5:7]
            day = dateString[8:10]
            hour = dateString[11:13]
            minute = dateString[14:16]
            second = dateString[17:19]
            #Logger.Trace("%s => %s-%s-%s %s:%s:%s", dateString, year, month, day, hour, minute, second)
            item.SetDate(year, month, day, hour, minute, second)
        return item

    def CtMnDownloadItem(self, item):
        """ downloads a video item and returns the updated one
        """
        item = self.DownloadVideoItem(item)
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

        data = UriHandler.Open(item.url, pb=False)
        firstPart = item.url[:item.url.rindex('/')]

        mediaUrls = Regexer.DoRegex(self.mediaUrlRegex, data)
        
        part = item.CreateNewEmptyMediaPart()
        for mediaUrl in mediaUrls:
            rtmp = "%s/%s" % (firstPart, mediaUrl[1])
            #rtmp = self.GetVerifiableVideoUrl(rtmp)
            part.AppendMediaStream(rtmp, mediaUrl[0])
        
        item.thumb = self.CacheThumb(item.thumbUrl)
        item.complete = True
        return item