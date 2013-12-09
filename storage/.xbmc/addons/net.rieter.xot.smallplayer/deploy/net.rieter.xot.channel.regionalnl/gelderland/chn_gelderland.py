#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import contextmenu
import chn_class
from helpers import datehelper
from logger import Logger

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
        
        self.noImage = "gelderlandimage.png"
        self.mainListUri = "http://www.omroepgelderland.nl/web/Uitzending-gemist-5/TV-1/Programmas/Actuele-programmas.htm"
        self.baseUrl = "http://www.omroepgelderland.nl"
        self.onUpDownUpdateEnabled = True
        self.swfUrl = "%s/design/channel/tv/swf/player.swf" % (self.baseUrl, )
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True, plugin=True))
        
        self.episodeItemRegex = '<a href="(/web/Uitzending-gemist-5/TV-1/Programmas/Programma.htm\?p=[^"]+)"\W*>\W*<div[^>]+>\W+<img src="([^"]+)"[^>]+>\W+</div>\W+<div[^>]+>([^<]+)' # used for the ParseMainList
        self.videoItemRegex = """<div class="videouitzending[^>]+\('([^']+)','[^']+','[^']+','[^']+','([^']+) (\d+) (\w+) (\d+)','([^']+)','([^']+)'""" 
        self.mediaUrlRegex = '<param\W+name="URL"\W+value="([^"]+)"'
        self.pageNavigationRegex = '(/web/Uitzending-gemist-5/TV-1/Programmas/Programma.htm\?p=Debuzz&amp;pagenr=)(\d+)[^>]+><span>' #self.pageNavigationIndicationRegex 
        self.pageNavigationRegexIndex = 1
        return True
    
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        
        
        item = mediaitem.MediaItem(resultSet[2], "%s%s" % (self.baseUrl, resultSet[0]))
        item.icon = self.icon
        item.thumb = self.noImage
        item.thumbUrl = "%s%s" % (self.baseUrl, resultSet[1])
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

        #Logger.Trace(resultSet)
        
        thumbUrl = "%s%s" % (self.baseUrl, resultSet[6])
        url = "%s%s" % (self.baseUrl, resultSet[5])
        name = "%s %s %s %s" % (resultSet[1], resultSet[2], resultSet[3], resultSet[4])
        
        videoUrl = resultSet[0]
        videoUrl = videoUrl.replace(" ", "%20")
        #videoUrl = self.GetVerifiableVideoUrl(videoUrl)
        # convert RTMP to HTTP
        #rtmp://media.omroepgelderland.nl         /uitzendingen/video/2012/07/120714 338 Carrie on.mp4
        #http://content.omroep.nl/omroepgelderland/uitzendingen/video/2012/07/120714 338 Carrie on.mp4
        videoUrl = videoUrl.replace("rtmp://media.omroepgelderland.nl", "http://content.omroep.nl/omroepgelderland")
        
        item = mediaitem.MediaItem(name, url)
        item.thumbUrl = thumbUrl
        item.thumb = self.noImage
        item.icon = self.icon        
        item.type = 'video'
        item.AppendSingleStream(videoUrl)
        
        # set date
        month = datehelper.DateHelper.GetMonthFromName(resultSet[3], "nl", False)
        day = resultSet[2]
        year = resultSet[4]
        item.SetDate(year, month, day)
        
        item.complete = False        
        return item
    
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. Usually retrieves the MediaURL 
        and the Thumb! It should return a completed item. 
        """
        Logger.Debug('Starting UpdateVideoItem for %s (%s)', item.name, self.channelName)
        
        item.thumb = self.CacheThumb(item.thumbUrl)      
        item.complete = True                    
        return item
    
    def CtMnDownloadItem(self, item):
        item = self.DownloadVideoItem(item)