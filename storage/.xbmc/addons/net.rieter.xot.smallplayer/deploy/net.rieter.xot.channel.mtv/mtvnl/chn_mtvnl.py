#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import contextmenu
import chn_class
from helpers import htmlentityhelper

from logger import Logger
from helpers.jsonhelper import JsonHelper
from urihandler import UriHandler
from regexer import Regexer

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
        self.noImage = "mtvnlimage.png"
        
        if self.channelCode == "mtvnl":
            self.mainListUri = "http://api.mtvnn.com/v2/site/m79obhheh2/nl/franchises.json?per=2147483647"
            self.baseUrl = "http://www.mtv.nl"
            
        elif self.channelCode == "mtvde":
            self.mainListUri = "http://api.mtvnn.com/v2/site/va7rcfymx4/de/franchises.json?per=2147483647"
            self.baseUrl = "http://www.mtv.de"
            
        self.onUpDownUpdateEnabled = True
        self.swfUrl = "http://media.mtvnservices.com/player/prime/mediaplayerprime.1.8.1.swf"

        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))

        self.requiresLogon = False

        if ("json" in self.mainListUri):
            Logger.Debug("Doing a JSON version of MTV")
            self.episodeItemRegex = '("local_title"[\w\W]+?\}\}(?:,\{|]))'
            self.videoItemRegex = '("original_title"[\w\W]+?\}\}(?:,\{|]))'
            self.CreateEpisodeItem = self.CreateEpisodeItemJson
            self.CreateVideoItem = self.CreateVideoItemJson
        else:
            Logger.Debug("Doing a HTML version of MTV")
            self.episodeItemRegex = '<a href="/(shows/[^"]+)" title="([^"]+)"><img [^>]+src="([^"]+)"' # used for the ParseMainList
            self.videoItemRegex = '<a href="([^"]+)" title="([^"]+)">(?:<span class=\Wepisode_number\W>(\d+)</span>){0,1}[\w\W]{0,100}?<img[^>]+src="([^"]+)"[^>]+\W+</a>'
            self.folderItemRegex = '<li>\W+<a href="/(seizoen/[^"]+)">([^<]+)</a>'
            #self.mediaUrlRegex = '<param name="src" value="([^"]+)" />'    # used for the UpdateVideoItem
        return True

    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item.
        """
        

        # http://www.mtv.nl/shows/195-16-pregnant
        url = "%s/%s" % (self.baseUrl, resultSet[0])
        item = mediaitem.MediaItem(resultSet[1], url)
        item.icon = self.icon
        item.thumbUrl = resultSet[2]
        item.complete = True
        return item

    def CreateEpisodeItemJson(self, resultSet):
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

        #Logger.Debug(resultSet)

        # add  { to make it valid Json again. if it would be in the regex it would
        # not find all items
        data = JsonHelper("{%s" % (resultSet,))

        # title
        localTitle = data.GetNamedValue("local_title")
        originalTitle = data.GetNamedValue("original_name")
        if (localTitle == "" or localTitle == "(null)"):
            title = originalTitle
        elif originalTitle != "null" and originalTitle != "" and originalTitle != localTitle:
            title = "%s (%s)" % (localTitle, originalTitle)
        else:
            title = localTitle

        # the URL
        serieId = data.GetNamedValue("id", -2)
        Logger.Trace("%s - %s", title, serieId)
        #url = "http://api.mtvnn.com/v2/site/m79obhheh2/nl/episodes.json?per=2147483647&franchise_id=%s" % (serieId,)
        url = "%sepisodes.json?per=2147483647&franchise_id=%s" % (self.mainListUri[0:43],serieId)
        
        # thumbs
        thumb = data.GetNamedValue("riptide_image_id")
        thumb = "http://images.mtvnn.com/%s/original" % (thumb,)

        # others
        description = data.GetNamedValue("local_long_description")

        # http://www.mtv.nl/shows/195-16-pregnant
        item = mediaitem.MediaItem(title, url)
        item.icon = self.icon
        item.thumbUrl = thumb
        item.description = description
        item.complete = True
        return item

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
        
        name = resultSet[1].capitalize()
        item = mediaitem.MediaItem(name, "%s/%s" % (self.baseUrl, resultSet[0]))
        item.icon = self.icon
        item.type = 'folder'
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

        url = resultSet[0]
        title = resultSet[1]
        part = resultSet[2]

        # retrieve the Full quality thumb
        thumb = resultSet[3]
        thumb = "%s/original" % (thumb[:thumb.rfind("/")],)

        if not (part == ""):
            title = "%s - %s" % (part, title)

        item = mediaitem.MediaItem(title, url)
        item.thumbUrl = thumb
        item.thumb = self.noImage
        item.icon = self.icon
        item.type = 'video'
        item.complete = False
        return item

    def CreateVideoItemJson(self, resultSet):
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
        self.UpdateVideoItem method is called if the item is focussed or selected
        for playback.

        """

        data = JsonHelper("{%s" % (resultSet,))

        # get the title
        originalTitle = data.GetNamedValue("original_title")
        localTitle = data.GetNamedValue("local_title")
        #Logger.Trace("%s - %s", originalTitle, localTitle)
        if (originalTitle == ""):
            title = localTitle
        else:
            title = originalTitle

        # get the other meta data
        videoMgids = Regexer.DoRegex('"id":"(\w+)"[^}]+"(%s|en)"' % (self.language,), resultSet)
        if (len(videoMgids) == 1):
            videoMgid = videoMgids[-1][0]
        elif len(videoMgids) == 0:
            return None
        else:
            # first set a default
            videoMgid = videoMgids[-1][0]
            for mgid in videoMgids:
                # try to find the one matching the channellanguage
                if (mgid[1].lower() == self.language.lower()):
                    videoMgid = mgid[0]
                    break

        #Logger.Trace(videoMgid)
        url = "http://api.mtvnn.com/v2/mrss.xml?uri=mgid:sensei:video:mtvnn.com:local_playlist-%s" % (videoMgid,)

        thumb = data.GetNamedValue("riptide_image_id")
        thumb = "http://images.mtvnn.com/%s/original" % (thumb,)

        description = data.GetNamedValue("local_long_description")

        date = data.GetNamedValue("published_from")
        date = date[0:10].split("-")

        item = mediaitem.MediaItem(title, url)
        item.thumbUrl = thumb
        item.thumb = self.noImage
        item.description = description
        item.icon = self.icon
        item.type = 'video'
        item.SetDate(date[0], date[1], date[2])
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

        url = item.url
        data = UriHandler.Open(url, pb=False)

        if ("json" in self.mainListUri):
            metaData = data
        else:
            mgid = Regexer.DoRegex("mgid:[^ ]+playlist-[abcdef0-9]+", data)[0]
            mgidUrlEncoded = htmlentityhelper.HtmlEntityHelper.UrlEncode(mgid)
            metaData = UriHandler.Open("http://api.mtvnn.com/v2/mrss.xml?uri=%s" % (mgidUrlEncoded,), pb=False)

        videoUrl = Regexer.DoRegex("<media:content[^>]+url='([^']+)'>", metaData)[0]
        Logger.Trace(videoUrl)
        videoData = UriHandler.Open(videoUrl, pb=False)
        videoItems = Regexer.DoRegex('<rendition[^>]+bitrate="(\d+)"[^>]*>\W+<src>([^<]+)<', videoData)

        item.MediaItemParts = []
        part = item.CreateNewEmptyMediaPart()
        for videoItem in videoItems:
            mediaUrl = self.GetVerifiableVideoUrl(videoItem[1])
            part.AppendMediaStream(mediaUrl, videoItem[0])

        item.complete = True
        return item
