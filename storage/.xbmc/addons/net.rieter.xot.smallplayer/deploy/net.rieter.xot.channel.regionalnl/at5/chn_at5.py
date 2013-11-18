#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import contextmenu
import chn_class
from helpers import datehelper
from helpers import xmlhelper

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
        self.noImage = "at5image.png"
        self.mainListUri = "http://www.at5.nl/tv/overzicht"
        self.baseUrl = "http://www.at5.nl"
        self.onUpDownUpdateEnabled = True
        self.swfUrl = "http://www.at5.nl/embed/at5player.swf"
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
                
        self.requiresLogon = False
        
        self.episodeItemRegex = '<li><a class="" href="(/tv/[^"]+)">([^<]+)</a></li>' # used for the ParseMainList
        self.videoItemRegex = """(?:<p class="tijd">\w+ (\d+) (\w+) (\d+), [^<]+</p>\W+<h1>([^<]+)</h1>[\w\W]+?swf\?e=(\d+)[\w\W]+?<div class="detail_tekst">(?:<p>([^<]*)</p>){0,1}|<img[^>]+src='([^']+)'[^>]+/></a>\W+<div>\W+<h3>\W+<span[^>]+>(\d+)-(\d+)-(\d+)</span>\W+<a href="([^"]+/)(\d+)">([^<]+)</a>\W+</h3>\W+<p>(?:<p>([^<]+)</p>){0,1})""" 
        self.mediaUrlRegex = '<param\W+name="URL"\W+value="([^"]+)"'
        self.pageNavigationRegex = '<a href="(/[^"]+page/)(\d+)">\d+</a>' #self.pageNavigationIndicationRegex 
        self.pageNavigationRegexIndex = 1
        return True
    
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        
        
        item = mediaitem.MediaItem(resultSet[1], "%s%s" % (self.baseUrl, resultSet[0]))
        item.icon = self.icon
        item.thumb = self.noImage
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
        
        if resultSet[0] == "":
            # not the main item
            thumbUrl = "%s%s" % (self.baseUrl, resultSet[6])
            day = resultSet[7]
            month = resultSet[8]
            year = resultSet[9]
            #url = "%s%s" % (resultSet[10], resultSet[11])
            vid = resultSet[11]
            title = resultSet[12]
            description = resultSet[13]
        else:
            # the main item on the page, only load once
            if "/page/" in self.parentItem.url:
                return None
            
            day = resultSet[0]
            month = resultSet[1]
            month = datehelper.DateHelper.GetMonthFromName(month, "nl", short=False)        
            year = resultSet[2]
            title = resultSet[3]
            vid = resultSet[4]
            description = resultSet[5]
            #url = self.parentItem.url
            thumbUrl = ''
        
        url = "http://www.at5.nl/embedder/videodata?e=%s" % (vid,)
        
        item = mediaitem.MediaItem(title, url)
        item.description = description
        item.thumbUrl = thumbUrl
        item.thumb = self.noImage
        item.icon = self.icon        
        item.SetDate(year, month, day)
        item.type = 'video'
        item.complete = False
        return item
    
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. Usually retrieves the MediaURL 
        and the Thumb! It should return a completed item. 
        """
        Logger.Debug('Starting UpdateVideoItem for %s (%s)', item.name, self.channelName)
        
        data = UriHandler.Open(item.url, pb=False)
        xml = xmlhelper.XmlHelper(data)
        
        if item.thumbUrl == '': 
            # if not thumb was present use the one from the XML
            item.thumbUrl = xml.GetSingleNodeContent("videoimage")
        item.thumb = self.CacheThumb(item.thumbUrl)      
        
        server = xml.GetSingleNodeContent("server")
        fileName = xml.GetSingleNodeContent("filename")
        mediaUrl = "%s/_definst_/%s" % (server, fileName)
        mediaUrl = self.GetVerifiableVideoUrl(mediaUrl)
        item.AppendSingleStream(mediaUrl, 0)
        
        item.complete = True                    
        return item    