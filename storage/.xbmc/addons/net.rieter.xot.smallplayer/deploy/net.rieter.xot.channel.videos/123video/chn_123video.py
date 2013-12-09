#===============================================================================
# Make global object available
#===============================================================================
import mediaitem
import contextmenu
import chn_class

from regexer import Regexer
from logger import Logger
from urihandler import UriHandler
from helpers.jsonhelper import JsonHelper
from helpers.encodinghelper import EncodingHelper
from encrypter import Encrypter


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

        self.mainListUri = "http://www.123video.nl/"
        self.baseUrl = "http://www.123video.nl/"
        self.noImage = "123image.png"

        self.contextMenuItems = []
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Update Item", "CtMnUpdateItem", itemTypes="video", completeStatus=None))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Download Item", "CtMnDownloadItem", itemTypes="video", completeStatus=True, plugin=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))

        # self.backgroundImage = ""
        # self.backgroundImage16x9 = ""
        self.requiresLogon = False
        # self.sortOrder = 5

        self.episodeItemRegex = '<a[^>]+href="/(video/[^"]+)" title="([^"]+)"'
        self.videoItemRegex = '<a onFocus="this.blur\(\);" href="/playvideos.asp\?MovieID=(\d+)[^"]*" title="([^"]+)"[^>]+>\W*<img src="([^"]+)"[^>]+></a>[\w\W]{0,800}?Geplaatst:[^-]*(\d+)-(\d+)-(\d+)'
        self.folderItemRegex = ''  # Pages are now seperate items '&nbsp;&nbsp;<a href="(/video.asp\?Page=\d+)[^"]+(&CatID=\d+)&[^"]+" title="Ga naar pagina (\d+)'

        """
            The ProcessPageNavigation method will parse the current data using the pageNavigationRegex. It will
            create a pageItem using the CreatePageItem method. If no CreatePageItem method is in the channel,
            a default one will be created with the number present in the resultset location specified in the
            pageNavigationRegexIndex and the url from the combined resultset. If that url does not contain http://
            the self.baseUrl will be added.
        """
        self.pageNavigationRegex = '<a href="(/video.asp\?Page=)(\d+)([^"]+)" title="Ga naar pagina'
        self.pageNavigationRegexIndex = 1

        #==============================================================================
        # non standard items
        self.ipVideoServer = "85.17.191.49"
        # http://85.17.191.49/458/458632.flv
        # http://85.17.191.44/263/263621.flv
        return True

#     #==============================================================================
#     def ParseMainList(self):
#         # get base items and add some other categories
#         items = chn_class.Channel.ParseMainList(self)
#         # remove xxx category
#         items.pop()
#
#         recent = mediaitem.MediaItem("Meest recente video's", "%s/video.asp?So=0" % self.mainListUri)
#         recent.icon = self.folderIcon
#         items.insert(0, recent)
#
#         best = mediaitem.MediaItem("Best beoordeelde video's", "%s/video.asp?So=2" % self.mainListUri)
#         best.icon = self.folderIcon
#         items.insert(0, best)
#
#         watched = mediaitem.MediaItem("Meest bekeken video's", "%s/video.asp?So=1" % self.mainListUri)
#         watched.icon = self.folderIcon
#         items.insert(0, watched)
#
#         spoken = mediaitem.MediaItem("Meest besproken video's", "%s/video.asp?So=2" % self.mainListUri)
#         spoken.icon = self.folderIcon
#         items.insert(0, spoken)
#
# #    <a onfocus="this.blur();" href="/video.asp?So=0" title="Meest recente video's" onmouseover="fOver(this);return true;">Meest recente video's</a> |
# #    <a onfocus="this.blur();" href="/video.asp?So=2" title="Best beoordeelde video's" onmouseover="fOver(this);return true;">Best beoordeelde video's</a> |
# #    <a onfocus="this.blur();" href="/video.asp?So=1" title="Meest bekeken video's" onmouseover="fOver(this);return true;">Meest bekeken video's</a> |
# #    <a onfocus="this.blur();" href="/video.asp?So=3" title="Meest besproken video's" onmouseover="fOver(this);return true;">Meest besproken video's</a>
#
#         return items

    #==============================================================================
    def CreateEpisodeItem(self, resultSet):
        """
        Accepts an arraylist of results. It returns an item.
        """

        item = mediaitem.MediaItem(resultSet[1], "%s%s" % (self.baseUrl, resultSet[0]))
        item.icon = self.folderIcon
        item.thumb = self.noImage
        return item

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

        items = []
        # first part of the data to prevent double pages
        data = Regexer.DoRegex('<div class="resultBox">([\w\W]+)', data)[0]

        Logger.Debug("Pre-Processing finished")
        return (data, items)

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

        item = mediaitem.MediaItem("Pagina %02i" % int(resultSet[2]), "%s%s%s" % (self.mainListUri, resultSet[0], resultSet[1]))
        item.description = item.name
        item.icon = self.folderIcon
        item.type = 'folder'
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

        Logger.Trace('starting FormatVideoItem for %s', self.channelName)

        item = mediaitem.MediaItem(resultSet[1].title(), resultSet[0])
        item.icon = self.icon
        item.thumb = self.noImage
        item.type = 'video'

        item.SetDate(resultSet[5], resultSet[4], resultSet[3])
        item.description = item.name

        # Do this on mouseover
        # item.thumb = self.CacheThumb(resultSet[2])
        item.thumbUrl = resultSet[2]
        item.complete = False

        return item

    #=============================================================================
    def UpdateVideoItem(self, item):
        """
        Accepts an item. It returns an updated item. Usually retrieves the MediaURL
        and the Thumb! It should return a completed item.
        """
        Logger.Debug('starting UpdateVideoItem for %s (%s)', item.name, self.channelName)

        movieId = int(item.url)
        Logger.Trace(movieId)

        # we need to encrypt stuff to get this to work
        enc = Encrypter(movieId)
        jsonInput = self.__GetJson(movieId, enc.publicKey, enc.salt)
        Logger.Trace(jsonInput)
        postData = enc.EncryptWithKey(jsonInput)

        # now send this out
        result = UriHandler.Open("http://www.123video.nl/initialize_player_v4.aspx", pb=False, proxy=self.proxy, params=postData, additionalHeaders={'123videoPlayer': enc.publicKey})
        jsonOutput = enc.DecryptWithKey(result)
        Logger.Trace(jsonOutput)

        # and create the actual video url
        jsonData = JsonHelper(jsonOutput)
        hashes = jsonData.GetValue('Hashes')
        locations = jsonData.GetValue('Locations')
        videoData = (locations[0], enc.publicKey, EncodingHelper.EncodeMD5(hashes[0], False), int(movieId / 1000), movieId, enc.EncryptWithKey('{"Salt": "%s"}' % (enc.salt,), enc.publicKey))
        mediaurl = "http://%s/%s/%s/%s/%s.flv?%s" % videoData

        if mediaurl != "":
            item.AppendSingleStream(mediaurl)

        item.thumb = self.CacheThumb(item.thumbUrl)
        item.complete = True
        item.downloadable = True

        Logger.Trace("Finished updating videoitem: %s", item)
        return item

    def __GetJson(self, movieId, publicKey, salt):
        """ Take from the 123video.swf

        Random:String(Math.floor(Math.random()*1.0E10)),
        MovieID:TopLevel.Variables.MovieID,
        MemberID:Number(TopLevel.getParameter("MemberID",0)),
        Password:String(TopLevel.getParameter("Password","")),
        PublicKey:TopLevel.Variables.PublicKey,
        IsEmbedded:TopLevel.Variables.isEmbedded,
        EmbedUrl:TopLevel.Domain.embedUrl,
        AdWanted:(TopLevel.Variables.isEmbedded)||(Boolean(Number(TopLevel.getParameter("RequestAd","1")))),
        ExternalInterfaceAvailable:ExternalInterface.available,
        Salt:TopLevel.Variables.Salt

        """

        json = dict()
        json['Random'] = "31415926"
        json['MovieID'] = movieId
        json['MemberID'] = 0
        json['Password'] = ""
        json['PublicKey'] = publicKey
        json['IsEmbedded'] = False
        json['EmbedUrl'] = ""
        json['AdWanted'] = False
        json['ExternalInterfaceAvailable'] = False
        json['Salt'] = salt
        return str(json).replace("False", "false").replace("True", "true").replace("'", '"')

    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def CtMnUpdateItem(self, item):  # @UnusedVariables
        self.onUpDown(ignoreDisabled=True)

    def CtMnDownloadItem(self, item):
        item = self.DownloadVideoItem(item)
