
import mediaitem
import chn_class
import cookielib

from regexer import Regexer
from helpers.jsonhelper import JsonHelper

from logger import Logger
from urihandler import UriHandler


class Channel(chn_class.Channel):
    def InitialiseVariables(self, channelInfo):
        """Initialisation of the class.

        WindowXMLDialog(self, xmlFilename, scriptPath[, defaultSkin, defaultRes]) -- Create a new WindowXMLDialog script.

        xmlFilename     : string - the name of the xml file to look for.
        scriptPath      : string - path to script. used to fallback to if the xml doesn't exist in the current skin. (eg os.getcwd())
        defaultSkin     : [opt] string - name of the folder in the skins path to look in for the xml. (default='Default')
        defaultRes      : [opt] string - default skins resolution. (default='720p')

        *Note, skin folder structure is eg(resources/skins/Default/720p)

        All class variables should be instantiated here and this method should not
        be overridden by any derived classes.

        """

        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self, channelInfo)

        self.mainListUri = "http://www.npo.nl/"
        self.baseUrl = "http://www.npo.nl"
        self.noImage = "npoimage.png"

        self.requiresLogon = False

        self.contextMenuItems = []

        self.episodeItemRegex = '<a href="([^"]+)"[^>]+>(Live [^<]+)</a>'
        self.videoItemRegex = ('<a href="/(live)/([^/"]+)"[^>]+><img[^>]+src="([^"]+)"', '<option value="(http://[^"]+)"[^>]+>([^<]+)</option>')
        self.folderItemRegex = '<a href="/(radio)/([^/"]+)"[^>]+><img[^>]+src="([^"]+)"'
        self.mediaUrlRegex = "BANDWIDTH=(\d+)\d{3}[^\n]+\W+([^\n]+.m3u8)"

        """
            The ProcessPageNavigation method will parse the current data using the pageNavigationRegex. It will
            create a pageItem using the CreatePageItem method. If no CreatePageItem method is in the channel,
            a default one will be created with the number present in the resultset location specified in the
            pageNavigationRegexIndex and the url from the combined resultset. If that url does not contain http://
            the self.baseUrl will be added.
        """

        """
            Test cases:


        """

        # needs to be here because it will be too late in the script version
        self.__IgnoreCookieLaw()
        return True

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

        Logger.Trace(resultSet)
        item = mediaitem.MediaItem(resultSet[1], resultSet[0])
        item.icon = self.icon
        item.thumb = self.noImage
        item.complete = True
        return item

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
        items = []

        if "/radio/" in self.parentItem.url:
            # we should always add the parent as radio item
            parent = self.parentItem
            Logger.Debug("Adding main radio item to sub item list: %s", parent)
            item = mediaitem.MediaItem("%s (Hoofd kanaal)" % (parent.name,), parent.url)
            item.icon = parent.icon
            item.thumb = parent.thumb
            item.thumbUrl = parent.thumbUrl
            item.type = 'video'
            item.complete = False
            items.append(item)

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

        if not self.parentItem.url.endswith("/radio"):
            # in case of radio, just display the folders on the main url
            return None

        resultSet = list(resultSet)
        resultSet.insert(0, 0)
        folderItem = self.CreateVideoItem(resultSet)
        folderItem.type = 'folder'
        return folderItem

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

        Logger.Debug("Content = %s", resultSet)

        if resultSet[0] == 0:
            resultSet = resultSet[1:]
            # first regex matched -> video channel
            name = resultSet[1]
            name = name.replace("-", " ").capitalize()

            item = mediaitem.MediaItem(name, "%s/%s/%s" % (self.baseUrl, resultSet[0], resultSet[1]), type="video")
            item.thumb = self.noImage

            if resultSet[2].startswith("http"):
                item.thumbUrl = resultSet[2].replace("regular_", "").replace("larger_", "")
            else:
                item.thumbUrl = "%s%s" % (self.baseUrl, resultSet[2].replace("regular_", "").replace("larger_", ""))
        else:
            # radio item hit
            if self.parentItem.url.endswith("/radio"):
                # don't show playback items on main radio page
                return None

            resultSet = resultSet[1:]
            item = mediaitem.MediaItem(resultSet[1], resultSet[0], type="video")
            item.thumbUrl = self.parentItem.thumbUrl
            item.thumb = self.parentItem.thumb

        item.icon = self.icon
        item.complete = False
        return item

    def UpdateVideoItem(self, item):
        """Updates an existing MediaItem with more data.

        Arguments:
        item : MediaItem - the MediaItem that needs to be updated

        Returns:
        The original item with more data added to it's properties.

        Used to update none complete MediaItems (self.complete = False). This
        could include opening the item's URL to fetch more data and then process that
        data or retrieve it's real media-URL.

        The method should at least:
        * cache the thumbnail to disk (use self.noImage if no thumb is available).
        * set at least one MediaItemPart with a single MediaStream.
        * set self.complete = True.

        if the returned item does not have a MediaItemPart then the self.complete flag
        will automatically be set back to False.

        """

        Logger.Debug('Starting UpdateVideoItem: %s', item.name)

        item.MediaItemParts = []
        part = item.CreateNewEmptyMediaPart()

        htmlData = UriHandler.Open(item.url, pb=False, proxy=self.proxy, bytes=15000)

        mp3Urls = Regexer.DoRegex("""data-streams='{"url":"([^"]+)","codec":"[^"]+"}'""", htmlData)
        if len(mp3Urls) > 0:
            part.AppendMediaStream(mp3Urls[0], 192)
        else:
            jsonUrls = Regexer.DoRegex('<div class="video-player-container" data-auto-play="true" data-prid="([^"]+)"', htmlData)
            for url in jsonUrls:
                jsonUrl = "http://e.omroep.nl/metadata/aflevering/%s" % (url,)

            jsonData = UriHandler.Open(jsonUrl, pb=False, proxy=self.proxy)
            json = JsonHelper(jsonData, Logger.Instance())

            for stream in json.GetValue("streams"):
                if stream['type'] == "hls":
                    url = stream['url']

                    # http://ida.omroep.nl/aapi/?type=jsonp&stream=http://livestreams.omroep.nl/live/npo/thematv/journaal24/journaal24.isml/journaal24.m3u8
                    Logger.Debug("Opeing IDA server for actual URL retrieval")
                    actualStreamData = UriHandler.Open("http://ida.omroep.nl/aapi/?stream=%s" % (url,), pb=False, proxy=self.proxy)
                    actualStreamJson = JsonHelper(actualStreamData, Logger.Instance())
                    m3u8Url = actualStreamJson.GetValue('stream')

                    # now we have the m3u8 URL, but it will do a HTML 302 redirect
                    (headData, m3u8Url) = UriHandler.Header(m3u8Url, proxy=self.proxy)  # : @UnusedVariables

                    # and now we can open it
                    m3u8Data = UriHandler.Open(m3u8Url, pb=False, proxy=self.proxy)
                    serverPart = m3u8Url[:m3u8Url.rindex("/")]
                    for m3u8 in Regexer.DoRegex(self.mediaUrlRegex, m3u8Data):
                        streamUrl = "%s/%s" % (serverPart, m3u8[1])
                        part.AppendMediaStream(streamUrl, m3u8[0])

            thumbs = json.GetValue('images')
            if thumbs:
                item.thumbUrl = thumbs[-1]['url']
                item.thumb = self.CacheThumb(item.thumbUrl)
        item.complete = True
        # Logger.Trace(item)
        return item

    def __IgnoreCookieLaw(self):
        """ Accepts the cookies from UZG in order to have the site available """

        Logger.Info("Setting the Cookie-Consent cookie for www.uitzendinggemist.nl")

        # the rfc2109 parameters is not valid in Python 2.4 (Xbox), so we ommit it.
        c = cookielib.Cookie(version=0, name='site_cookie_consent', value='yes', port=None, port_specified=False, domain='.www.npo.nl', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=2327431273, discard=False, comment=None, comment_url=None, rest={'HttpOnly': None})  # , rfc2109=False)
        UriHandler.Instance().cookieJar.set_cookie(c)

        # http://pilot.odcontent.omroep.nl/codem/h264/1/nps/rest/2013/NPS_1220255/NPS_1220255.ism/NPS_1220255.m3u8
        # balancer://sapi2cluster=balancer.sapi2a

        # c = cookielib.Cookie(version=0, name='balancer://sapi2cluster', value='balancer.sapi2a', port=None, port_specified=False, domain='.pilot.odcontent.omroep.nl', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=2327431273, discard=False, comment=None, comment_url=None, rest={'HttpOnly': None})  # , rfc2109=False)
        # UriHandler.Instance().cookieJar.set_cookie(c)
        # c = cookielib.Cookie(version=0, name='balancer://sapi1cluster', value='balancer.sapi1a', port=None, port_specified=False, domain='.pilot.odcontent.omroep.nl', domain_specified=True, domain_initial_dot=False, path='/', path_specified=True, secure=False, expires=2327431273, discard=False, comment=None, comment_url=None, rest={'HttpOnly': None})  # , rfc2109=False)
        # UriHandler.Instance().cookieJar.set_cookie(c)
        return
