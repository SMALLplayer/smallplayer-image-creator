#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import contextmenu
import chn_class

from helpers import smilhelper
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
        
        self.noImage = "extremeimage.png"
        self.mainListUri = "http://extreme.com/"
        self.baseUrl = "http://extreme.com"
        self.onUpDownUpdateEnabled = True
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download item", "CtMnDownloadItem", itemTypes="video", completeStatus=True, plugin=True))
                
        self.requiresLogon = False
        
        self.episodeItemRegex = '<li><a href="([^"]+)" title=[^>]*>([^<]+)</a></li>'
        self.folderItemRegex = ''
        self.videoItemRegex = '<li class="node_item video[^"]*"><a href="([^"]+)"[^>]*><img [^>]+src="([^"]+)"[^>]+title="([^"]+)"\W*/>[\W\w]{0,1000}<p class="node_description">([^<]*)' 
        self.mediaUrlRegex = 'fo.addVariable\("id", "([^"]+)"\)'
        self.pageNavigationRegex = '<a href="(/[^"]+page=)(\d+)">\d+</a>' 
        self.pageNavigationRegexIndex = 1 
        return True
      
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def CtMnDownloadItem(self, item):
        self.DownloadVideoItem(item)
        
    #http://freecaster.tv/live
    #==============================================================================
    def ParseMainList(self):
        items = chn_class.Channel.ParseMainList(self)
        
        #item = mediaitem.MediaItem("Livestreams", "http://freecaster.tv/live?page=1")
        #item.icon = self.icon
        #item.complete = True
        
        #items.append(item)
        return items
    
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        #item = mediaitem.MediaItem(resultSet[0], "http://www.freecaster.com/helpers/videolist_helper.php?apID=%s&i=0&q=&sortby=date&sort=DESC&event_id=" % resultSet[1])
        item = mediaitem.MediaItem(resultSet[1], "%s%s?page=1" % (self.baseUrl, resultSet[0]))
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

        item = mediaitem.MediaItem(resultSet[2],"%s%s" % (self.baseUrl, resultSet[0]))
        
        if resultSet[3] == '':
            item.description = item.name
        else:
            item.description = resultSet[3]
        
        item.thumbUrl = resultSet[1]
        item.icon = self.icon
        item.thumb = self.noImage
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
        
        # get the thumb
        item.thumb = self.CacheThumb(item.thumbUrl)
        
        # get additional info
        data = UriHandler.Open(item.url, pb=True)
        guid = Regexer.DoRegex('<param name="flashvars" value="id=([^&]+)&amp;', data)

        #<param name="flashvars" value="id=dj0xMDEzNzQyJmM9MTAwMDAwNA&amp;tags=source%253Dfreecaster&amp;autoplay=1" />
        # http://freecaster.tv/player/smil/dj0xMDEzNzQyJmM9MTAwMDAwNA -> playlist with bitrate
        # http://freecaster.tv/player/smil/dj0xMDEzNzQyJmM9MTAwMDAwNA -> info (not needed, get description from main page.

        url = ''
        if len(guid) > 0:
            url = '%s/player/smil/%s' % (self.baseUrl, guid[0],) 
        
        if url == '':
            Logger.Error("Cannot find GUID in url: %s", item.url)
            return item
        
        data = UriHandler.Open(url, pb=True)
        
        smiller = smilhelper.SmilHelper(data)
        baseUrl = smiller.GetBaseUrl()
        urls = smiller.GetVideosAndBitrates()
        
        part = item.CreateNewEmptyMediaPart()
        for url in urls:
            part.AppendMediaStream("%s%s" % (baseUrl, url[0]), bitrate=int(int(url[1])/1000))
            item.complete = True
            
        Logger.Trace("UpdateVideoItem complete: %s", item)
        
        return item    