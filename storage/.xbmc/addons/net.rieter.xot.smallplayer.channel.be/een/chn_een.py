# coding:UTF-8
#===============================================================================
# Import the default modules
#===============================================================================
import urlparse

#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import contextmenu
import chn_class

from helpers.jsonhelper import JsonHelper

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
        
        self.noImage = "eenimage.png"
        self.mainListUri = "http://www.een.be/mediatheek"
        self.baseUrl = "http://www.een.be"
        self.swfUrl = "http://www.een.be/sites/een.be/modules/custom/vrt_video/player/player_4.3.swf"
        
        self.episodeItemRegex = '<option value="(\d+)">([^<]+)</option>' # used for the ParseMainList
        self.videoItemRegex = None # set in preprocess
        
        self.mediaUrlRegex = "(rtmpt*://[^']+)',file:\W*'([^']+)'"
        self.pageNavigationRegex = '<a href="([^"]+\?page=\d+)"[^>]+>(\d+)' 
        self.pageNavigationRegexIndex = 1
            
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))        
        
        """Test cases:
        
        Laura: year is first 2 digits
        Koppen: year is first 2 and last 2
        
        """
        
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
        
        items = chn_class.Channel.ParseMainList(self, returnData=returnData)
        
        recent = mediaitem.MediaItem("-= Meest recent =-", "http://mp.vrt.be/api/playlist/most_recent_een.json")
        recent.thumb = self.noImage
        recent.icon = self.icon
        recent.complete = True
        
        # no need to add a date, as they are not shown anyways for folders.
        #now = datetime.datetime.now()
        #recent.SetDate(now.year, now.month, now.day, now.hour, now.minute, now.second)
        
        items.insert(0, recent)
        return items
    
    def PreProcessFolderList(self, data):
        """Performs pre-process actions for data processing/
        
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
        
        if ("json" in self.parentItem.url):
            Logger.Debug("Json page found")
            self.videoItemRegex = '("item": \{[\w\W]{0,3000}?}\W})'
            self.CreateVideoItem = self.CreateVideoItemJson
        else:
            Logger.Debug("HTML/Ajax page found")
            self.videoItemRegex = '<li[^>]*>\W+<a href="([^"]+\/)(\d+)"[^<]+<img src="([^"]+)"[^<]*</a>\W+<h5><a[^>]+>([^<]+)</a>'
            self.CreateVideoItem = self.CreateVideoItemHtml
        return (data.replace("&apos", "'"), [])
    
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        
        # dummy class
        url = "http://www.een.be/mediatheek/tag/%s"
        item = mediaitem.MediaItem(resultSet[1], url % (resultSet[0],))
        item.icon = self.icon
        item.type = "folder"
        item.complete = True
        return item
    
    def CreatePageItem(self, resultSet):
        """Creates a MediaItem of type 'page' using the resultSet from the regex.
        
        Arguments:
        resultSet : tuple(string) - the resultSet of the self.pageNavigationRegex
        
        Returns:
        A new MediaItem of type 'page'
        
        This method creates a new MediaItem from the Regular Expression 
        results <resultSet>. The method should be implemented by derived classes 
        and are specific to the channel.
         
        """

        # we need to overwrite the page number, as the Een.be pages are zero-based.
        item = chn_class.Channel.CreatePageItem(self, (resultSet[0],''))
        item.name = resultSet[1]
        
        Logger.Trace("Created '%s' for url %s", item.name, item.url)
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
        self.UpdateVideoItem method is called if the item is focused or selected
        for playback.
         
        """
        
        
        json = JsonHelper(resultSet)
        
        title = json.GetNamedValue("title")
        url = json.GetNamedValue("website_url")
        description = json.GetNamedValue("description")
        thumb = json.GetNamedValue("url")
        date = json.GetNamedValue("broadcast_date_start")
        time = json.GetNamedValue("broadcast_time_start")
        dateParts = date.split("/")
        timeParts = time.split(":")
        guid = json.GetNamedValue("guid")
        
        # append the GUID to make sure they are recognized as separate items
        item = mediaitem.MediaItem("%s (%s)" % (title, time), "%s?guid=%s" % (url, guid))
        item.thumb = self.noImage
        item.thumbUrl = thumb
        item.description = description
        item.type = "video"
        item.SetDate(dateParts[0], dateParts[1], dateParts[2], timeParts[0], timeParts[1], 0)
        
        """
        "media_content_url": "http://mp.vod.flash.vrt.be/vod/vod_77533/PC.f4m?nvb=20121009120717&amp;nva=20121009130717&amp;token=0c862ac411e0a00908777",
        "ipad_url":          "http://mp.vod.ios.vrt.be/vod/vod_77533/ipad.m3u8?nvb=20121009120717&amp;nva=20121009130717&amp;token=051f6913a56feb3816a4a",
        "iphone_url":        "http://mp.vod.ios.vrt.be/vod/vod_77533/iphone.m3u8?nvb=20121009120717&amp;nva=20121009130717&amp;token=0c9f5a8d47220e8a647fb"
        """
        
        #pcStream = json.GetNamedValue("media_content_url").replace("&amp;","&")
        ipadStream = json.GetNamedValue("ipad_url").replace("&amp;","&")
        iphoneStream = json.GetNamedValue("iphone_url").replace("&amp;","&")
        
        part = item.CreateNewEmptyMediaPart()
        #part.AppendMediaStream(pcStream, 1200) -> Not supported by XBMC
        part.AppendMediaStream(ipadStream, 1400)
        part.AppendMediaStream(iphoneStream, 700)
        
        item.complete = True
        return item
    
    def CreateVideoItemHtml(self, resultSet):
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
        
        

        #http://www.een.be/mediatheek/ajax/video/531837

        url = "%sajax/video/%s" % (resultSet[0], resultSet[1])
        item = mediaitem.MediaItem(resultSet[3], urlparse.urljoin(self.baseUrl, url))
        
        item.thumbUrl = resultSet[2]
        item.thumb = self.noImage
        item.icon = self.icon        
        
        dateRegex = Regexer.DoRegex("/(?:20(\d{2})_[^/]+|[^\/]+)/[^/]*_(\d{2})(\d{2})(\d{2})[_.]", item.thumbUrl)
        if (len(dateRegex) == 1):
            dateRegex = dateRegex[0]
            
            # figure out if the year is the first part
            year = dateRegex[0]
            if dateRegex[1] == year or year =="":
                # The year was in the path, so use that one. OR the year was not in the
                # path and we assume that the first part is the year
                item.SetDate(2000+int(dateRegex[1]), dateRegex[2], dateRegex[3])
            else:
                # the year was in the path and tells us the first part is the day.
                item.SetDate(2000+int(dateRegex[3]), dateRegex[2], dateRegex[1])
        item.type = 'video'
        item.complete = False
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. Usually retrieves the MediaURL 
        and the Thumb! It should return a completed item. 
        """
        Logger.Debug('Starting UpdateVideoItem for %s (%s)', item.name, self.channelName)
        
        # rtmpt://vrt.flash.streampower.be/een//2011/07/1000_110723_getipt_neefs_wiels_Website_EEN.flv
        # http://www.een.be/sites/een.be/modules/custom/vrt_video/player/player_4.3.swf
        
        item.thumb = self.CacheThumb(item.thumbUrl)        
        
        # now the mediaurl is derived. First we try WMV
        data = UriHandler.Open(item.url, pb=False)
        
        descriptions = Regexer.DoRegex('<div class="teaserInfo">(?:[\W\w])*?<p><a[^>]+>([^<]+)</a>', data)
        for desc in descriptions:
            item.description = desc
            
        urls = Regexer.DoRegex(self.mediaUrlRegex, data)
        for url in urls:
            #mediaurl = "%s//%s" % (url[1],url[0])  # the extra slash in the url causes the application name in the RTMP stream to be "een" instead of "een/2011"
            mediaurl = "%s//%s" % (url[0],url[1])  # the extra slash in the url causes the application name in the RTMP stream to be "een" instead of "een/2011"
            mediaurl = mediaurl.replace(" ", "%20")
            mediaurl = self.GetVerifiableVideoUrl(mediaurl)
        
        if mediaurl != "":
            # In some cases the RTMPT does not work. Let's just try the RTMP first and then add the original if the RTMP version fails.
            item.AppendSingleStream(mediaurl.replace("rtmpt://", "rtmp://"))
            item.AppendSingleStream(mediaurl)
            
            item.complete = True            
        else:
            Logger.Debug("Media url was not found.")

        return item    
