#===============================================================================
# Import the default modules
#===============================================================================
import urlparse

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
        
        self.noImage = "lamasimage.png"
        self.mainListUri = "http://sites.bnn.nl/page/lamazien/zoek/doemaarwat"
        self.baseUrl = "http://sites.bnn.nl"
        self.onUpDownUpdateEnabled = False
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Update Item", "CtMnUpdateItem", itemTypes="video", completeStatus=False))            
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True, plugin=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
        
        self.requiresLogon = False
        
        self.episodeItemRegex = "(?:<div class=\"button\"[^>]+href='(/page/lamazien/[^']+)';\">([^<]+)</div>|<a href=\"(/page/lamazien/zoek/[^\"]+)\">([^<]+)</a>)" # used for the ParseMainList
        self.videoItemRegex = """<li>\W+<strong>([^<]+)</strong>+[\w\W]+?onclick="location.href='([^']+)';[\W\w]+?<img src="([^"]+)"[\W\w]+?</div>\W+</div>\W+(?:<br /> )*([^<>]+)<br />(?:\W+<small>[^,]+, (\d+) (\w+) (\d+)</small>){0,1}"""   # used for the CreateVideoItem 
        self.folderItemRegex = ''  # used for the CreateFolderItem
        self.mediaUrlRegex = "'file', '([^']+\.flv)'"    # used for the UpdateVideoItem
        
        #========================================================================== 
        # non standard items
        self.topDescription = ""
        
        return True
      
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def CtMnDownloadItem(self, item):
        item = self.DownloadVideoItem(item)

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
        
        
        
        name = resultSet[3]
        url = resultSet[2]
        if name == '':
            name = "-= %s =-" %  (resultSet[1], )
            url = resultSet[0]
        
        # dummy class
        item = mediaitem.MediaItem(name, urlparse.urljoin(self.baseUrl, url))
        item.complete = True
        item.icon = self.folderIcon
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
        
        item = mediaitem.MediaItem(resultSet[0], urlparse.urljoin(self.baseUrl, resultSet[1].replace(" ", "%20")))
        item.type = 'video'
        item.icon = self.icon
        
        # temp store the thumb for use in UpdateVideoItem
        item.thumbUrl = resultSet[2]
        item.thumb = self.noImage        
        item.description = resultSet[3]
                
        if not resultSet[4] == "":
            day = resultSet[4]
            month = resultSet[5]
            month = datehelper.DateHelper.GetMonthFromName(month, "nl", short=False)
            year = resultSet[6]
            item.SetDate(year, month, day)
        
        # getting the URL is part of the PlayVideo
        item.downloadable = True
        item.complete = False
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. Usually retrieves the MediaURL 
        and the Thumb!
        """
        #Logger.Debug('Starting UpdateVideoItem for %s (%s)', item.name, self.channelName)
        
        item = chn_class.Channel.UpdateVideoItem(self, item)
        item.thumb = self.CacheThumb(item.thumbUrl)

        #Logger.Trace('finishing UpdateVideoItem: %s', item)
        
        item.complete = True
        return item
        