#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import contextmenu
import chn_class

from regexer import Regexer
from helpers import htmlentityhelper
from logger import Logger

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
        
        self.mainListUri = "http://www.myvideo.nl/"
        self.baseUrl = "http://www.myvideo.nl"
        self.noImage = "myvideoimage.png"
        
        self.requiresLogon = False
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True, plugin=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
        
        
        self.episodeItemRegex = "<a class='nArrow' href='([^']+)' title='[^']*'>([^<]+)</a>"
        self.videoItemRegex = "<img id='([^']+)' src='([^']+)' class='vThumb' alt='[^']*' [^>]+></a></div></div><div class='sCenter vTitle'><span class='title'><a[^>]+title='([^']+)'" 
        self.folderItemRegex = ''
        self.mediaUrlRegex = '<item>\W*<file>\W*([^>]*)\W*</file>\W*<bandwidth>(\d+)</bandwidth>'
        
        """ 
            The ProcessPageNavigation method will parse the current data using the pageNavigationRegex. It will
            create a pageItem using the CreatePageItem method. If no CreatePageItem method is in the channel,
            a default one will be created with the number present in the resultset location specified in the 
            pageNavigationRegexIndex and the url from the combined resultset. If that url does not contain http://
            the self.baseUrl will be added. 
        """
        # remove the &amp; from the url
        self.pageNavigationRegex = "<a class='pView pnNumbers'  href='([^?]+\?lpage=)(\d+)([^']+)"  
        self.pageNavigationRegexIndex = 1

        #========================================================================== 
        # non standard items
        self.categoryName = ""
        
        return True
    
    #==============================================================================
    def ParseMainList(self):
        """
            Add some custom categories here
        """
        items = []
        
        item = mediaitem.MediaItem("Nieuwste videos", "http://www.myvideo.nl/news.php?rubrik=rljgs")
        item.icon = self.folderIcon
        items.append(item)
        
        item = mediaitem.MediaItem("Meest bekeken videos", "http://www.myvideo.nl/news.php?rubrik=tjyec")
        item.icon = self.folderIcon
        items.append(item)

        item = mediaitem.MediaItem("Meest besproken videos", "http://www.myvideo.nl/news.php?rubrik=vpjpr")
        item.icon = self.folderIcon
        items.append(item)        
        
        item = mediaitem.MediaItem("Best beoordeelde videos", "http://www.myvideo.nl/news.php?rubrik=xayvg")
        item.icon = self.folderIcon
        items.append(item)        
        
        item = mediaitem.MediaItem("Favoriete videos", "http://www.myvideo.nl/news.php?rubrik=pcvbc")
        item.icon = self.folderIcon
        items.append(item)        
        
        return items + chn_class.Channel.ParseMainList(self)
    
    #============================================================================== 
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
        
        Logger.Info("Performing Pre-Processing")
        _items = []
        
        # extract the category name from the pagedata
        results = Regexer.DoRegex("in de categorie\W+<span class='[^']+'>[^;]+;([^<]+)&quot", data)
        
        if len(results)> 0:
            self.categoryName = results[0]
        
        Logger.Debug("Pre-Processing finished")
        return (data, _items)
    
    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        
        #<a class='nArrow' href='([^']+)' title='[^']*'>([^<]+)</a>
        #                            0                     1                                
        item = mediaitem.MediaItem(resultSet[1],htmlentityhelper.HtmlEntityHelper.StripAmp("%s%s" % (self.baseUrl, resultSet[0])))
        item.icon = self.icon
        Logger.Trace("%s (%s)", item.name, item.url)
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

        Logger.Trace('starting FormatVideoItem for %s', self.channelName)
        #<img id='([^']+)' src='([^']+)' class='vThumb' alt='[^']*'/></a></div></div><div class='sCenter vTitle'><span class='title'><a[^>]+title='([^']+)'>
        #            0            1                                                                                                                    2
        name = resultSet[2]
        item = mediaitem.MediaItem(name, htmlentityhelper.HtmlEntityHelper.StripAmp("%s%s" % (self.baseUrl, resultSet[0])))
        
        item.description = "%s\n%s" % (self.categoryName, resultSet[2])
        item.icon = self.icon
        item.thumb = self.noImage
        item.thumbUrl = resultSet[1]
        
        # now create the video url using the 
        # http://myvideo-550.vo.llnwd.net/nl/d3/movie7/4a/thumbs/3384551_1.jpg
        # http://myvideo-550.vo.llnwd.net/nl/d3/movie7/4a/3384551.flv
        
        # het script: http://myvideo-906.vo.llnwd.net/nl/d2/movie4/d93548906.flv
        # de pagina:  http://myvideo-906.vo.llnwd.net/nl/d2/movie4/d9/3548906.flv
        
        urlResult = Regexer.DoRegex("(http://myvideo[^_]+)/thumbs(/\d+)_\d+.jpg", item.thumbUrl)
        mediaurl = ""
        if len(urlResult)>0:
            for part in urlResult[0]:
                mediaurl = "%s%s" % (mediaurl, part)
        mediaurl = "%s.flv" % (mediaurl)
        
        item.AppendSingleStream(mediaurl)
        Logger.Trace("Updated mediaurl for %s", item)
        item.type = 'video'
        item.complete = False
        
        return item
    
    #============================================================================= 
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. 
        """
        Logger.Debug('Starting UpdateVideoItem for %s (%s)',item.name, self.channelName)
        item.thumb = self.CacheThumb(item.thumbUrl)
        item.complete = True
        return item

    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def CtMnDownloadItem(self, item):
        item = self.DownloadVideoItem(item)