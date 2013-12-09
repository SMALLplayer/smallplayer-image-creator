#===============================================================================
# Import the default modules
#===============================================================================
import xbmc 
import string
#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import contextmenu
import chn_class

from helpers import datehelper
from regexer import Regexer
from logger import Logger
from urihandler import UriHandler

#===============================================================================
# main Channel Class
#===============================================================================
class Channel(chn_class.Channel):
    #===============================================================================
    # define class variables
    #===============================================================================
    def InitialiseVariables(self, channelInfo):
        """
        Used for the initialisation of user defined parameters. All should be 
        present, but can be adjusted
        """
        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self, channelInfo)
        
        self.noImage = "dumpertimage.png"
        self.backgroundImage = ""  # if not specified, the one defined in the skin is used
        self.backgroundImage16x9 = ""  # if not specified, the one defined in the skin is used
        self.buttonID = 0
        self.onUpDownUpdateEnabled = True
        
        self.mainListUri = "http://www.dumpert.nl/%s/%s/"
        self.baseUrl = "http://www.dumpert.nl/mediabase/flv/%s_YTDL_1.flv.flv"
        self.playerUrl = ""
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True, plugin=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
        
        self.requiresLogon = False
        
        self.asxAsfRegex = '<[^\s]*REF href[^"]+"([^"]+)"' # default regex for parsing ASX/ASF files
        self.episodeSort = True
        self.videoItemRegex = '<a[^>]+href="([^"]+)"[^>]*>\W+<img src="([^"]+)[\W\w]{0,400}<h\d>([^<]+)</h\d>\W+<[^>]*date"{0,1}>(\d+) (\w+) (\d+) (\d+):(\d+)'
        self.folderItemRegex = ''  # used for the CreateFolderItem
        
        # Changed on 2008-04-23 self.mediaUrlRegex = "'(http://www.dumpert.nl/mediabase/flv/[^']+)'"    # used for the UpdateVideoItem
        self.mediaUrlRegex = ('data-vidurl="([^"]+)"',)    # used for the UpdateVideoItem
        
        return True
    
    #==============================================================================
    def ParseMainList(self):
        """ 
        accepts an url and returns an list with items of type CListItem
        Items have a name and url. This is used for the filling of the progwindow
        """
        items = []
        
        for page in range(1,3):
            item = mediaitem.MediaItem("Toppertjes - Pagina %s" % (page), self.mainListUri % ('toppers',page))
            item.icon = self.icon;
            items.append(item)                    
        
        for page in range(1,11):
            item = mediaitem.MediaItem("Filmpjes - Pagina %s" % (page), self.mainListUri % ('filmpjes',page))
            item.icon = self.icon;
            items.append(item)                    
        
        item = mediaitem.MediaItem("Zoeken", "searchSite")
        item.icon = self.icon;
        items.append(item)            
            
        return items
    
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

        #                         0              1             2                             3
        #<a class="item" href="([^"]+)"[^=]+="([^"]+)" alt="([^"]+)[^:]+<div class="date">([^<]+)
        
        #Logger.Trace(resultSet)
        
        item = mediaitem.MediaItem(resultSet[2],resultSet[0], type='video')
        item.icon = self.icon;
        item.description = resultSet[2]
        item.thumb = self.noImage 
        item.thumbUrl = resultSet[1]   
        
        try:
            month = datehelper.DateHelper.GetMonthFromName(resultSet[4], "en")                            
            item.SetDate(resultSet[5], month, resultSet[3], resultSet[6], resultSet[7], 0)
        except:
            Logger.Error("Error matching month: %s", resultSet[4].lower(), exc_info=True)
        
        item.complete = False
        item.downloadable = True
        return item
    
    #==============================================================================
    def UpdateVideoItem(self, item):        
        """
        Updates the item
        """
        item.thumb = self.CacheThumb(item.thumbUrl)
        
        data = UriHandler.Open(item.url, pb=False, proxy=self.proxy)
        
        for regex in self.mediaUrlRegex:
            results = Regexer.DoRegex(regex, data)
            for result in results:
                if result != "":
                    item.AppendSingleStream(result)
                    break
            item.complete = True
            
        Logger.Trace("VideoItem updated: %s", item)
        return item
    
    #==============================================================================
    def SearchSite(self, url=None):
        """
        Creates an list of items by searching the site
        """
        items = []
        
        keyboard = xbmc.Keyboard('')
        keyboard.doModal()
        if (keyboard.isConfirmed()):
            needle = keyboard.getText()
            if len(needle)>0:
                #convert to HTML
                needle = string.replace(needle, " ", "%20")
                searchUrl = "http://www.dumpert.nl/search/V/%s/ " % (needle)
                temp = mediaitem.MediaItem("Search", searchUrl)
                return self.ProcessFolderList(temp)
                
        return items
    
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def CtMnDownloadItem(self, item):
        item = self.DownloadVideoItem(item)