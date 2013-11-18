# coding:Cp1252
#===============================================================================
# Import the default modules
#===============================================================================

#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import contextmenu
import chn_class
from helpers import jsonhelper

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
        
        self.noImage = "canvasimage.png"
        self.mainListUri = "http://www.canvas.be/video_overzicht"
        self.baseUrl = "http://www.canvas.be"
        self.swfUrl = "http://www.canvas.be/sites/all/libraries/player/PolymediaShowFX16.swf"
        
        self.episodeItemRegex = '<option value="([^"]{15,100})">([^<]+)</option>' # used for the ParseMainList
        self.videoItemRegex = '\{"item":([\w\W]{0,3000})categoryBrandId'
        
        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))        
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
        
        mainItems = chn_class.Channel.ParseMainList(self, returnData=returnData)
        
        # let's add some specials
        #http://mp.vrt.be/api/playlist/collection_91.json
        for url in ("http://mp.vrt.be/api/playlist/most_viewed_canvas.json", "http://mp.vrt.be/api/playlist/most_rated_canvas.json", "http://mp.vrt.be/api/playlist/most_recent_canvas.json", "http://mp.vrt.be/api/playlist/now_available_brand_canvas_recent.json"):
            if ("most_viewed_canvas" in url):
                name = "Meest bekeken"
            elif ("most_rated_canvas" in url):
                name = "Meest gewaardeerd"
            elif ("most_recent_canvas" in url):
                name = "Meest recent"
            else:
                name = "Nieuw"
            name = "Canvas: %s" % (name,)
            item = mediaitem.MediaItem(name, url)
            item.thumb = self.noImage
            item.icon = self.icon
            item.complete = True
            mainItems.append(item)
        
        return mainItems
    
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item. 
        """
        
        code = resultSet[0].replace(":", "\:")
        url = "http://vrt-mp.polymedia.it/search/select/?q=brand:Canvas%20AND%20programme_code:" + code + "&sort=date%20desc&rows=160&wt=xslt&tr=json.xsl"
        
        item = mediaitem.MediaItem(resultSet[1], url)
        item.icon = self.icon
        item.type = "folder"
        item.complete = True
        return item
    
    def CreateVideoItem(self, resultSet):
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
        
        
        
        json = jsonhelper.JsonHelper(resultSet)
        title = json.GetNamedValue("title")
        description = json.GetNamedValue("short_description")
        thumbUrl = json.GetNamedValue("url", 0)
        guid = json.GetNamedValue("guid")
        url = "http://mp.vrt.be/api/playlist/details/%s.json" % (guid,)
        
        item = mediaitem.MediaItem(title, url)        
        item.thumbUrl = thumbUrl
        item.thumb = self.noImage
        item.icon = self.icon
        item.description = description

        item.MediaItemParts = []
        mediaUrl = json.GetNamedValue("media_content_url").replace("mp4:", "/mp4:")
        if ("rtmp" in mediaUrl):
            mediaUrl = self.GetVerifiableVideoUrl(mediaUrl)
            part = item.AppendSingleStream(mediaUrl, 1296)        
            
            # let's see if there are more streams available. If not, the update video item will do it.
            mediaUrlMedium = json.GetNamedValue("ipad_url").replace("mp4:", "/mp4:")
            mediaUrlLow = json.GetNamedValue("iphone_url").replace("mp4:", "/mp4:")
            if (mediaUrlMedium != ""):
                # not all have seperate bitrates, so these are estimates
                part.AppendMediaStream(self.GetVerifiableVideoUrl(mediaUrlMedium), 960)
            if (mediaUrlLow != ""):
                # not all have seperate bitrates, so these are estimates
                part.AppendMediaStream(self.GetVerifiableVideoUrl(mediaUrlLow), 696)
        else:
            # the encoded URL (http://mp.vod.ios.vrt.be/vod/vod_61870/ipad.m3u8?nvb=20120611190958&nva=20120611200958&token=0ac4cea3d973f33907344)
            # that we find here returns:
            """
            #EXTM3U
            #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=1327104
            1296/playlist.m3u8
            #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=983040
            960/playlist.m3u8
            #EXT-X-STREAM-INF:PROGRAM-ID=1,BANDWIDTH=712704
            696/playlist.m3u8
            """

            # Let's assume the bitrates do not vary            
            part = item.CreateNewEmptyMediaPart()
            for bitrate in (1296, 960, 696):
                mediaUrl = "http://mp.vod.ios.vrt.be/vod/vod_%s/%s/playlist.m3u8" % (guid, bitrate)
                part.AppendMediaStream(mediaUrl, bitrate)
        
        date = json.GetNamedValue("broadcast_date_start")
        time = json.GetNamedValue("broadcast_time_start")   
        """
          "broadcast_date_start": "2012/06/07",
                                   0123456789
          "broadcast_time_start": "21:30", 
                                   01234
        """     
        year = date[0:4]
        month = date[5:7]
        day = date[8:10]
        hour = time[0:2]
        minutes = time[3:5]
        Logger.Trace("%s-%s-%s %s:%s", year, month, day, hour, minutes)
        item.SetDate(year, month, day, hour, minutes, 0)
                
        item.type = 'video'
        item.complete = False
        return item
    
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. Usually retrieves the MediaURL 
        and the Thumb! It should return a completed item. 
        """
        Logger.Debug('Starting UpdateVideoItem for %s', item)
        
        # rtmpt://vrt.flash.streampower.be/een//2011/07/1000_110723_getipt_neefs_wiels_Website_EEN.flv
        # http://www.een.be/sites/een.be/modules/custom/vrt_video/player/player_4.3.swf
        
        if len(item.MediaItemParts) == 1 and len(item.MediaItemParts[0].MediaStreams) == 1:
            # just a single RTMP was found
            Logger.Debug("Updating for more RTMP streams")
            data = UriHandler.Open(item.url, pb=False)
            json = jsonhelper.JsonHelper(data)
            
            part = item.MediaItemParts[0]
            mediaUrlMedium = json.GetNamedValue("ipad_url").replace("mp4:", "/mp4:")
            mediaUrlLow = json.GetNamedValue("iphone_url").replace("mp4:", "/mp4:")
            if (mediaUrlMedium != ""):
                # not all have seperate bitrates, so these are estimates
                part.AppendMediaStream(self.GetVerifiableVideoUrl(mediaUrlMedium), 960)
            if (mediaUrlLow != ""):
                # not all have seperate bitrates, so these are estimates
                part.AppendMediaStream(self.GetVerifiableVideoUrl(mediaUrlLow), 696)
                
        item.thumb = self.CacheThumb(item.thumbUrl)        
        item.complete = True
        return item