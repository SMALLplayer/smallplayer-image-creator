# coding:UTF-8

#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import contextmenu
import chn_class
from helpers import datehelper
from logger import Logger
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

        self.noImage = "patheimage.png"
        self.mainListUri = "http://www.pathe.nl/bioscoopagenda"
        self.baseUrl = "http://www.pathe.nl"
        self.onUpDownUpdateEnabled = True
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True, plugin=True))
        
        self.episodeItemRegex = '<li><a href="(/bioscoopagenda[^"]+)">([^<\n]+)</a></li>'
        self.folderItemRegex = '<a href="(/bioscoopagenda/[^/]+/[^/]+)" rel="nofollow">([^>]+)</a>'
        self.videoItemRegex = '<img src="([^"]+)" alt="" width="75" height="100" />\W+</a>\W+<div class="heading">\W+<h3.<a href="([^"]+)">([^<]+)(?:<img[^>]+>){0,1}</a></h3>\W+</div>\W+<p>([^<]+)</p>[\w\W]{0,200}?<table class="time-table">([\w\W]{0,2000}?)</table>' 
        self.mediaUrlRegex = 'writeMoviePlayer\(\W+"(http[^"]+)'
        self.pageNavigationRegex = '(/web/Uitzending-gemist-5/TV-1/Programmas/Programma.htm\?p=Debuzz&amp;pagenr=)(\d+)[^>]+><span>' #self.pageNavigationIndicationRegex 
        self.pageNavigationRegexIndex = 1
        return True
    
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        
        
        item = mediaitem.MediaItem(resultSet[1], "%s%s" % (self.baseUrl, resultSet[0]))
        item.icon = self.icon
        item.thumb = self.noImage
        #item.thumbUrl = "%s%s" % (self.baseUrl, resultSet[1])
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
        
        url = "%s%s" % (self.baseUrl, resultSet[0])
        name = resultSet[1]
        
        if name == "Ma":
            name = "Maandag"
        elif name == "Di":
            name = "Dinsdag"
        elif name == "Wo":
            name = "Woensdag"
        elif name == "Do":
            name = "Donderdag"
        elif name == "Vr":
            name = "Vrijdag"
        elif name == "Za":
            name = "Zaterdag"
        elif name == "Zo":
            name = "Zondag"
        
        item = mediaitem.MediaItem(name, url)
        item.thumb = self.noImage
        item.icon = self.icon
        
        date = datehelper.DateHelper.GetDateForNextDay(name, ["Maandag", "Dinsdag", "Woensdag", "Donderdag", "Vrijdag", "Zaterdag", "Zondag"], "Morgen")
        item.SetDate(date.year, date.month, date.day)
        
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
        
        thumbUrl = "%s%s" % (self.baseUrl, resultSet[0])
        thumbUrl = thumbUrl.replace("/75x100/", "/180x252/")
        url = "%s%s" % (self.baseUrl, resultSet[1])
        name = resultSet[2]
                
        item = mediaitem.MediaItem(name, url)
        item.thumbUrl = thumbUrl
        item.thumb = self.noImage
        item.icon = self.icon
        item.type = 'video'
        
        # more description stuff
        description = "%s\n\n" % (resultSet[3],)
        
        timeTable = resultSet[4]
        timeTableRegex = '<th><a href="[^>]+>([^<]+)</a></th>\W+<td>([^\n]+)</td>'        
        for timeTableEntry in Regexer.DoRegex(timeTableRegex, timeTable):
            Logger.Trace(timeTableEntry)
            bios = timeTableEntry[0]
            description = "%s%s: " % (description, bios)
            times = timeTableEntry[1]
            timeRegex = '<a[^>]+>(\d+:\d+)'
            for time in Regexer.DoRegex(timeRegex, times):
                Logger.Trace(time)
                description = "%s %s, " % (description, time)
            description = "%s\n" % (description.strip(', '))
        
        item.description = description.strip()
        
        item.complete = False        
        return item
    
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. Usually retrieves the MediaURL 
        and the Thumb! It should return a completed item. 
        """
        Logger.Debug('Starting UpdateVideoItem for %s (%s)', item.name, self.channelName)
        
        data = UriHandler.Open(item.url, pb=False, proxy = self.proxy)
        videos = Regexer.DoRegex(self.mediaUrlRegex, data)
        
        for video in videos:
            Logger.Trace(video)
            item.AppendSingleStream(video)
        
        item.thumb = self.CacheThumb(item.thumbUrl)      
        item.complete = True                    
        return item
    
    def CtMnDownloadItem(self, item):
        item = self.DownloadVideoItem(item)