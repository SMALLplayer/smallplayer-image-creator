#===============================================================================
# Import the default modules
#===============================================================================
import os

#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import contextmenu
import chn_class
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
        
        self.noImage = "tvnlimage.png"
        self.onUpDownUpdateEnabled = True
        self.requiresLogon = False
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))        
        return True
      
    #==============================================================================
    # Custom Methodes, in chronological order   
    #==============================================================================
    def ParseMainList(self):
        """ 
        accepts an url and returns an list with items of type CListItem
        Items have a name and url. This is used for the filling of the progwindow
        """        
        items = []
        if len(self.mainListItems) > 1:
            return self.mainListItems
        
        # read the regional ones
        dataPath = os.path.abspath(os.path.join(__file__, '..', 'data'))
        Logger.Info("TV streams located at: %s", dataPath)
        regionals = os.listdir(dataPath)
        for regional in regionals:
            path = os.path.join(dataPath, regional) 
            if not os.path.isdir(path):
                continue
            item = mediaitem.MediaItem(regional, path)
            item.complete = True
            item.icon = self.folderIcon
            items.append(item)
            pass
        
        # sort by name
        if self.episodeSort:
            items.sort()
                
        # add the National ones
        self.mainListItems = items
        return items
    
    #==============================================================================
    
    #==============================================================================
    def ProcessFolderList(self, item):
        Logger.Debug("trying first items")
        url = item.url
        items = []
        
        stations = os.listdir(url)
        for station in stations:
            if not station.endswith(".m3u"):
                continue
            
            name = station.replace(".m3u", "")
            stream = os.path.join(url, station)
            stationItem = mediaitem.MediaItem(name, stream)
            stationItem.icon = os.path.join(url, "%s%s" % (name, ".tbn"))
            stationItem.complete = True
            stationItem.description = stationItem.name
            stationItem.AppendSingleStream(stream)
            stationItem.type = "playlist"
            stationItem.thumb = stationItem.icon
            items.append(stationItem)
            pass
        
        return items