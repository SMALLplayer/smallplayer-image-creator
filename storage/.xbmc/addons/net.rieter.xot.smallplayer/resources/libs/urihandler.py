#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================

import os
import urllib2
import cookielib
import re
import threading
import time
import string
import StringIO
import gzip
import zlib
from httplib import IncompleteRead

import xbmcgui
import xbmc

from config import Config
from cache import filecache
from cache import cachehttphandler
from logger import Logger
from envcontroller import EnvController
from envcontroller import Environments


class UriHandler:
    """Class that handles all the URL downloads"""

    __handler = None
    __error = "UriHandler not initialized. Use UriHandler.CreateUriHandler ======="

    @staticmethod
    def CreateUriHandler(useProgressBars=True, useCaching=False):
        """Initialises the UriHandler class

        Keyword Arguments:
        useProgressBars : boolean - Indicates whether progressbars need to be
                                    used when downloaded. If set to False no
                                    bars will ever be used. If set to True the
                                    Open method decides if bars are used.

        useCaching      : boolean - Indication if http caching should be enabled.

        """

        if (UriHandler.__handler is None):
            UriHandler.__handler = CustomUriHandler(useProgressBars, useCaching)

            # hook up all the methods to pass to the actual UriHandler
            UriHandler.Download = UriHandler.__handler.Download
            UriHandler.Open = UriHandler.__handler.Open
            UriHandler.Header = UriHandler.__handler.Header
            UriHandler.CookieCheck = UriHandler.__handler.CookieCheck
            UriHandler.CookiePrint = UriHandler.__handler.CookiePrint
            UriHandler.CorrectFileName = UriHandler.__handler.CorrectFileName
        else:
            Logger.Warning("Cannot create a second UriHandler instance!")
        return

    # In order for the PyDev errors to disappear, we create some fake methods here.

    @staticmethod
    def Instance():
        """ return the logger instance """
        return UriHandler.__handler

    @staticmethod
    def Download(uri, filename, folder="", pb=True, proxy=None, params="", userAgent=None, referer=None, additionalHeaders=dict()):
        pass

    @staticmethod
    def Open(uri, pb=True, proxy=None, bytes=0, params="", referer=None, headers=dict(), additionalHeaders=dict()):
        pass

    @staticmethod
    def Header(uri, proxy=None, params="", additionalHeaders=dict()):
        pass

    @staticmethod
    def CookieCheck(cookieName):
        pass

    @staticmethod
    def CookiePrint():
        pass

    @staticmethod
    def CorrectFileName(filename):
        pass

    @staticmethod
    def GetExtensionFromUrl(url):
        """ determines the file extension for a certain URL

        Arguments:
        url: String - The URL to search

        Returns an extension or "" if not was found.

        """

        extensions = {".divx": "divx", ".flv": "flv", ".mp4": "mp4", "m4v": ".mp4", ".avi": "avi", "h264": "mp4"}
        for ext in extensions:
            if  url.find(ext) > 0:
                return extensions[ext]

        return ""


class CustomUriHandler:
    """Class that handles all the URL downloads"""

    def __init__(self, useProgressBars=True, useCaching=False):
        """Initialises the UriHandler class

        Keyword Arguments:
        useProgressBars : boolean - Indicates whether progressbars need to be
                                    used when downloaded. If set to False no
                                    bars will ever be used. If set to True the
                                    Open method decides if bars are used.

        useCaching      : boolean - Indication if http caching should be enabled.

        """

        self.cookieJar = cookielib.CookieJar()

        # set caching stuff
        if useCaching:
            cachePath = os.path.join(Config.cacheDir, "www")
            self.cacheStore = filecache.FileCache(cachePath, logger=Logger.Instance())
        self.useCaching = useCaching
        self.useCompression = not EnvController.IsPlatform(Environments.Xbox)

        self.defaultLocation = xbmc.translatePath("special://home")
        self.pbAnimation = ["-", "\\", "|", "/"]
        self.pbEnabled = useProgressBars
        self.blockSize = (1024 / 4)  # *8
        self.bytesToMB = 1048576
        self.inValidCharacters = "[^a-zA-Z0-9!#$%&'()-.@\[\]^_`{}]"
        Logger.Info("UriHandler initialised [pbEnabled=%s, useCaching=%s]", self.pbEnabled, self.useCaching)
        # self.timerTimeOut = 2.0                     # used for the emergency canceler

        self.webTimeOutInterval = Config.webTimeOut  # max duration of request
        self.pollInterval = 0.1                      # time between polling of activity

    def Download(self, uri, filename, folder="", pb=True, proxy=None, params="", userAgent=None, referer=None, additionalHeaders=dict()):
        """Downloads an file

        Arguments:
        uri      : string - the URI to download
        filename : string - the filename that should be used to store the file.

        Keyword Arguments:
        folder : [opt] string  - the folder to save to. If "" then a dialog is
                                 presented to the user.
        pb     : [opt] boolean - should a progress bar be shown
        proxy  : [opt] string  - The address and port (proxy.address.ext:port) of
                                 a proxy server that should be used.
        params : [opt] string  - data to send with the request (open(uri, params))

        Returns:
        The full path of the downloaded file.

        """

        pbEnabled = pb  # and self.pbEnabled -> downloads should always show progressbar
        pbTitle = ""
        pbLine1 = ""
        pbLine2 = ""
        if pbEnabled:
            uriPB = xbmcgui.DialogProgress()

        cancelled = False

        destFilename = self.CorrectFileName(filename)
        destFolder = folder

        blockMultiplier = 16 * 8  # to increase blockSize

        # if no destination is given, get one via a dialog box
        if destFolder == "":
            browseDialog = xbmcgui.Dialog()
            destFolder = browseDialog.browse(3, 'Select download destination for "%s"' % (destFilename,), 'files', '', False, False, self.defaultLocation)

        destComplete = os.path.join(destFolder, destFilename)
        if os.path.exists(destComplete):
            Logger.Info("Url already downloaded to: %s", destComplete)
            return destComplete

        Logger.Info("Creating Downloader for url '%s' to filename '%s'", uri, destComplete)
        try:
            # create progress dialog
            if pbEnabled:
                pbTitle = 'Downloading the requested url'
                pbLine1 = uri
                uriPB.create(pbTitle, pbLine1)
            if params == "":
                sourceHandle = self.__GetOpener(proxy, userAgent, disableCaching=True, referer=referer, additionalHeaders=additionalHeaders, acceptCompression=False).open(uri)
            else:
                sourceHandle = self.__GetOpener(proxy, userAgent, disableCaching=True, referer=referer, additionalHeaders=additionalHeaders, acceptCompression=False).open(uri, params)
            destHandle = open(destComplete, 'wb')
            headers = sourceHandle.info()

            read = 0
            blocknum = 0

            if "content-length" in headers:
                fileSize = int(headers["Content-Length"])
                Logger.Info('FileSize is known (fileSize=' + str(fileSize) + ')')
            else:
                fileSize = -1
                Logger.Info('FileSize is unknown')

            while 1:
                block = sourceHandle.read(self.blockSize * blockMultiplier)
                if block == "":
                    break
                read += len(block)
                destHandle.write(block)
                blocknum += 1

                if pbEnabled:
                    cancelled = self.__PBHandler(blocknum, self.blockSize * blockMultiplier, fileSize, uriPB, pbLine1, pbLine2)
                    # check to see if cancelled
                    if cancelled:
                        break

            # clean up things
            sourceHandle.close()
            destHandle.close()

            if pbEnabled:
                uriPB.close()

            # delete parts if cancelled
            if cancelled:
                Logger.Info("Download Cancelled")
                if os.path.exists(destComplete):
                    Logger.Info("Removing partly downloaded item: %s", destComplete)
                    os.remove(destComplete)
                rtrn = ""
            else:
                Logger.Info("Url %s downloaded succesfully.", uri)
                rtrn = destComplete

            return rtrn

        except:
            Logger.Critical("Error caching file", exc_info=True)
            if os.path.exists(destComplete):
                os.remove(destComplete)
            if pbEnabled:
                uriPB.close()

            try:
                sourceHandle.close()
            except UnboundLocalError:
                pass
            try:
                destHandle.close()
            except UnboundLocalError:
                pass

            return ""

    def Open(self, uri, pb=True, proxy=None, bytes=0, params="", referer=None, additionalHeaders=dict()):
        """Open an URL Async using a thread

        Arguments:
        uri      : string - the URI to download

        Keyword Arguments:
        pb      : [opt] boolean - should a progress bar be shown
        proxy   : [opt] string  - The address and port (proxy.address.ext:port) of
                                  a proxy server that should be used.
        bytes   : [opt] integer - the number of bytes to get.
        params  : [opt] string  - data to send with the request (open(uri, params))
        headers : [opt] dict    - a dictionary of additional headers

        Returns:
        The data that was retrieved from the URI.

        """

        try:
            if uri == "":
                return ""

            if uri.startswith("file:"):
                index = string.rfind(uri, "?")
                if index > 0:
                    uri = uri[0:index]

            progressbarEnabled = pb and self.pbEnabled
            parameters = params
            targetUrl = uri
            pbTitle = ''
            pbLine1 = ''
            pbLine2 = ''
            blocks = 0
            filesize = 0
            canceled = False
            timeOut = False

            Logger.Info("Opening requested uri Async: %s (already %s threads)", targetUrl, threading.activeCount())

            if progressbarEnabled:
                pbTitle = 'Opening request url'
                pbLine1 = targetUrl
                uriPB = xbmcgui.DialogProgress()
                uriPB.create(pbTitle, pbLine1)

            # set the start time in seconds
            startTime = time.time()

            openThread = AsyncOpener(targetUrl, self.__GetOpener(proxy, referer=referer, additionalHeaders=additionalHeaders), self.blockSize, action='open', bytes=bytes, params=parameters)
            openThread.start()
            # time.sleep(0.1)

            count = 0
            while not openThread.isCompleted and not canceled:
                if progressbarEnabled:
                    blocks = openThread.blocksRead
                    filesize = openThread.fileSize
                    canceled = self.__PBHandler(blocks, self.blockSize, filesize, uriPB, pbLine1, pbLine2)

                count += 1
                openThread.join(self.pollInterval)

                # the join call should block the calling method for the interval. No sleep needed.
                # time.sleep(self.pollInterval)

                if time.time() > startTime + self.webTimeOutInterval:
                # if self.pollInterval * count > self.webTimeOutInterval:
                    timeOut = True
                    break

            # we are finished now
            if progressbarEnabled:
                # Disabled this line, because it gave errors for some users.
                # uriPB.update(100, pbLine1 ,pbLine2)
                uriPB.close()

            if canceled:
                Logger.Warning("Opening of %s was cancelled", targetUrl)
                data = ""
            if timeOut:
                Logger.Critical("The URL lookup did not respond within the TimeOut (%s s)", self.webTimeOutInterval)
                data = ""
            if openThread.error != None:
                Logger.Critical("The URL was not opened successfully: %s", openThread.error)
                # perhaps there was data?
                data = openThread.data
            else:
                Logger.Info("Url %s was opened successfully", targetUrl)
                data = openThread.data

            if (openThread.isAlive()):
                Logger.Debug("UriOpener thread is still alive, wait for it to close")
                openThread.join(Config.webTimeOut)

            return data
        except:
            if progressbarEnabled:
                uriPB.close()

            Logger.Error("Error in threading", exc_info=True)

            if (openThread.isAlive()):
                Logger.Debug("UriOpener thread is still alive, wait for it to close")
                openThread.join(Config.webTimeOut)

            return ""

    def Header(self, uri, proxy=None, params="", referer=None, additionalHeaders=dict()):
        """Retrieves header information only

        Arguments:
        uri      : string - the URI to download

        Keyword Arguments:
        proxy  : [opt] string  - The address and port (proxy.address.ext:port) of
                                 a proxy server that should be used.
        params : [opt] string  - data to send with the request (open(uri, params))

        Returns:
        Data and the URL to which a redirect could have occurred.

        """

        Logger.Info("Retreiving Header info for %s", uri)
        # uri = uri
        # params = params

        try:
            if params == "":
                uriHandle = self.__GetOpener(proxy, headOnly=True, referer=referer, additionalHeaders=additionalHeaders).open(uri)
            else:
                uriHandle = self.__GetOpener(proxy, headOnly=True, referer=referer, additionalHeaders=additionalHeaders).open(uri, params)

            data = uriHandle.info()
            realUrl = uriHandle.geturl()
            data = data.get('Content-Type')
            uriHandle.close()
            Logger.Debug("Header info retreived: %s for realUrl %s", data, realUrl)
            return (data, realUrl)
        except:
            Logger.Critical("Header info not retreived", exc_info=True)
            return ("", "")

    def CookieCheck(self, cookieName):
        """Checks if a cookie exists in the CookieJar

        Arguments:
        cookieName : string - the name of the cookie

        Returns:
        a boolean indicating whether the cookie existed or not.

        """

        retVal = False

        for cookie in self.cookieJar:
            if cookie.name == cookieName:
                Logger.Debug("Found cookie: %s", cookie.name)
                retVal = True
                break

        return retVal

    def CookiePrint(self):
        """Prints out a list of registered cookies into the logfile"""

        cookies = "Content of the CookieJar:\n"
        for cookie in self.cookieJar:
            cookies = "%s%r\n" % (cookies, cookie)
            Logger.Trace("cookieName=%s; cookieValue=%s; expires:%s; domain: %s", cookie.name, cookie.value, cookie.expires, cookie.domain)
        Logger.Debug(cookies.rstrip())
        return

    def CorrectFileName(self, filename):
        """Corrects a filename to prevent XFAT issues and other folder issues

        Arguments:
        filename : string - the original filename

        Returns:
        a filename that is save for the the XFAT and other file systems.

        """
        original = filename

        # filter out the chars that are not allowed
        filename = re.sub(self.inValidCharacters, "", filename)

        # and check for length on Xbox
        maxLength = 42
        if len(filename) > maxLength and EnvController.IsPlatform(Environments.Xbox):
            Logger.Debug("Making sure the file lenght does not exceed the maximum allowed on Xbox")
            (base, ext) = os.path.splitext(filename)
            baseLength = maxLength - len(ext)
            # regex = "^.{1,%s}" % (baseLength)
            # base = re.compile(regex).findall(base)[-1]

            if len(base) > baseLength:
                base = base[0:baseLength - 1]

            filename = "%s%s" % (base, ext)

        Logger.Debug("Corrected from '%s' to '%s'", original, filename)
        return filename

    def __PBHandler(self, blocknum, blocksize, totalsize, uriPB, pbLine1, pbLine2):
        """Callback handler for displaying Progress Bar information

        Arguments:
        blocknum  : integer        - Number of blocks that were downloaded.
        blocksize : integer        - Blocksize used for downloading.
        totalsize : integer        - Total file size.
        uriPB     : DialogProgress - The actual Progress Dialog object.
        pbLine1   : string         - First line of the Progress Dialog object.
        pbLine2   : string         - Second line of the Progress Dialog object.

        Returns:
        True if the action is canceled by the user (by clicking on the
        progress bar's Cancel button.

        """

        if uriPB.iscanceled() == False:
            try:
                retrievedsize = blocknum * blocksize
                if totalsize != 0:
                    perc = 100 * retrievedsize / totalsize
                else:
                    perc = 0

                retrievedsizeMB = 1.0 * retrievedsize / self.bytesToMB
                totalsizeMB = 1.0 * totalsize / self.bytesToMB

                if totalsize > 0:
                    pbLine2 = '%i%% (%.1f of %.1f MB)' % (perc, retrievedsizeMB, totalsizeMB)
                    animation = blocknum % len(self.pbAnimation)
                    uriPB.update(int(perc), self.pbAnimation[animation] + " - " + pbLine1, pbLine2)
                return False
            except:
                Logger.Critical("PBHandle error", exc_info=True)
                return True
        else:
            return True

    def __GetOpener(self, proxy=None, userAgent=None, headOnly=False, disableCaching=False, referer=None, additionalHeaders=dict(), acceptCompression=True):
        """Get's a urllib2 URL opener with cookie jar

        Keyword Arguments:
        proxy             : [opt] string  - The address and port (proxy.address.ext:port) of
                                            a proxy server that should be used.
        headOnly          : [opt] boolean - Indication that only the header is needed.
        disableCaching    : [opt] boolean - Indication to disable the caching.
        referer           : [opt] string  - The referer URL
        additionalHeaders : [opt] dict    - A dictionary of additional headers

        Returns:
        An urllib2 OpenerDirector object for handling URL requests.

        """

        cookieHandler = urllib2.HTTPCookieProcessor(self.cookieJar)
        headHandler = HttpHeadHandler()

        cacheHandler = None
        if self.useCaching and not disableCaching:
            cacheHandler = cachehttphandler.CacheHttpHandler(self.cacheStore, logger=Logger.Instance())

        uriOpener = urllib2.build_opener(cookieHandler)

        if proxy is None:
            pass
        else:
            proxyHandler = proxy.GetSmartProxyHandler()
            uriOpener.add_handler(proxyHandler)

        if headOnly:
            uriOpener.add_handler(headHandler)

        # add the compression handler before the cache in the
        # chain. That way we store decompressed data and save
        # cpu time.
        if acceptCompression and self.useCompression:
            compressionHandler = HttpCompressionHandler()
            uriOpener.add_handler(compressionHandler)

        if cacheHandler:
            uriOpener.add_handler(cacheHandler)

        # let's add some headers
        headers = []

        # change the user agent (thanks to VincePirez @ xbmc forums)
        if userAgent is None:
            user_agent = "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-GB; rv:1.9.2.13) Gecko/20101203 Firefox/3.6.13 (.NET CLR 3.5.30729)"
        else:
            Logger.Info("Using custom UserAgent for url: %s", userAgent)
            user_agent = userAgent
        # user_agent = "XOT/3.0 (compatible; XBMC; U)"
        # uriOpener.addheaders = [('User-Agent', user_agent)]
        headers.append(('User-Agent', user_agent))

        # add the custom referer
        if not referer is None:
            Logger.Info("Adding custom Referer: '%s'", referer)
            user_agent = userAgent
            headers.append(('referer', referer))

        if additionalHeaders:
            for header in additionalHeaders:
                headers.append((header, additionalHeaders[header]))

        uriOpener.addheaders = headers

        return uriOpener


class AsyncOpener(threading.Thread):
    def __init__(self, uri, handler, blocksize, action=None, bytes=0, params=""):
        """Creates a new Asynchronous URL opener Thread

        Arguments:
        uri       : string         - The URL to open.
        handler   : OpenerDirector - The urllib2 OpenerDirector object used for
                                     opening the URL's.
        blocksize : integer        - Blocksize to use for the download.

        Keyword Arguments:
        action   : [opt] string  - The action to perform in within this thread.
                                   Defaults to None. Possible values: "open"
        bytes    : [opt] integer - Total number of bytes to read. Defaults to 0
                                   which means that all bytes are download.
        params   : [opt] string  - data to send with the request (open(uri, params))

        Starts a new Thread which handles an action with a specific method. In this
        case the "open" action is handled by calling the self.Open method.

        """

        self.uri = uri
        self.uriHandler = handler
        self.params = params
        self.blockSize = blocksize
        self.maxBytes = bytes

        self.isCompleted = False
        self.fileSize = 0
        self.blocksRead = 0
        self.data = ""
        self.error = None

        if action == 'open':
            threading.Thread.__init__(self, name='UriOpenerThread', target=self.Open)
        else:
            raise Exception()
            return

    #===============================================================================
    def Open(self):
        """Opens an URL and updates properties of the AsyncOpener object"""

        try:
            # Check for posts
            if self.params == '':
                sourceHandle = self.uriHandler.open(self.uri)
            else:
                sourceHandle = self.uriHandler.open(self.uri, self.params)

            Logger.Debug("Determining which Progessbar to use....")
            data = sourceHandle.info()

            if data.get('Content-length'):
                self.fileSize = int(data.get('Content-length'))
                Logger.Debug('FileSize is known (fileSize=' + str(self.fileSize) + ')')
            else:
                self.fileSize = -1
                Logger.Debug('FileSize is unknown')

            # check for encoding
            charSet = None
            try:
                contentType = data.get('Content-Type')
                if contentType:
                    Logger.Trace("Found Content-Type header: %s", contentType)
                    charSetNeedle = 'charset='
                    charSetIndex = contentType.find(charSetNeedle)
                    if (charSetIndex > 0):
                        charSet = contentType[charSetIndex + len(charSetNeedle):]
                        Logger.Trace("Found Charset HTML Header: %s", charSet)
            except:
                charSet = None

            data = ""

            # time.sleep(2)

            self.blocksRead = 0
            while 1:
                block = sourceHandle.read(self.blockSize)
                if block == "":
                    break
                data = data + block
                self.blocksRead += 1

                if self.maxBytes > 0 and self.blocksRead * self.blockSize > self.maxBytes:
                    Logger.Info('Stopping download because Bytes > maxBytes')
                    break
                # need a sleep to allow reading of variables
                # time.sleep(0.0005)

            sourceHandle.close()

            # decode
            if charSet:
                Logger.Debug("Decoding data using charset HTML Header: %s", charSet)
                data = data.decode(charSet)

            self.data = data
            self.isCompleted = True

        except (IncompleteRead, ValueError), error:
            # Python 2.6 throws a IncompleteRead on Chuncked data
            # Python 2.4 throws a ValueError on Chuncked data
            self.error = error
            Logger.Error("IncompleteRead error opening url %s", self.uri)
            self.data = data
            self.isCompleted = True
            try:
                sourceHandle.close()
            except UnboundLocalError:
                pass

        except Exception, error:
            Logger.Critical("Error Opening url %s", self.uri, exc_info=True)
            self.error = error
            try:
                sourceHandle.close()
            except UnboundLocalError:
                pass

            self.data = ""
            self.isCompleted = True


class HttpHeadHandler(urllib2.BaseHandler):
    def __init__(self):
        return

    def default_open(self, request):
        """Handles GET requests. It check the cache and if a valid one is present
        returns that one if it is still valid. Is called before a request is
        actually done.

        Arguments:
        respone : urllib2.Request - The request that needs to be served.

        Returns None but sets the HEAD request

        """

        # just set the head
        Logger.Debug("Setting request type to HEAD.")
        request.get_method = lambda: 'HEAD'
        return None


class HttpCompressionHandler(urllib2.BaseHandler):
    def __init__(self):
        return

    def https_request(self, request):
        return self.http_request(request)

    def http_request(self, request):
        request.add_header("Accept-Encoding", "gzip, deflate")
        Logger.Debug("Adding header 'Accept-Encoding: %s'", "gzip, deflate")
        return request

    def https_response(self, request, response):
        return self.http_response(request, response)

    def http_response(self, request, response):  # @UnusedVariables
        Logger.Trace("Processing HTTP response for possible decompression")
        # Logger.Trace("%s\n%s", response.url, response.info())

        oldResponse = response
        # do the decompression
        contentEncoding = response.headers.get("content-encoding")
        if contentEncoding:
            responseEncoding = contentEncoding
            data = response.read()
            try:
                if "gzip" in contentEncoding:
                    Logger.Debug("Decompressing '%s' response", contentEncoding)
                    # the GzipFileReader expect a StringIO object
                    gzipStream = StringIO.StringIO(data)
                    fileStream = gzip.GzipFile(fileobj=gzipStream)
                    responseEncoding = "none"

                elif "deflate" in contentEncoding:
                    Logger.Debug("Decompressing '%s' response", contentEncoding)
                    fileStream = StringIO.StringIO(zlib.decompress(data))
                    responseEncoding = "none"

                elif contentEncoding == "none":
                    Logger.Debug("Nothing to decompress. Content-encoding: '%s'", contentEncoding)
                    # we have already used the response.read() so we need to create
                    # a new filestream with the original data in it.
                    fileStream = StringIO.StringIO(data)

                else:
                    Logger.Warning("Unknown Content-Encoding: '%s'", contentEncoding)
                    # we have already used the response.read() so we need to create
                    # a new filestream with the original data in it.
                    fileStream = StringIO.StringIO(data)
            except:
                Logger.Error("Cannot Decompress this response", exc_info=True)
                # we have already used the response.read() so we need to create
                # a new filestream with the original data in it.
                fileStream = StringIO.StringIO(data)

            response = urllib2.addinfourl(fileStream, oldResponse.headers, oldResponse.url, oldResponse.code)
            response.msg = oldResponse.msg

            # Update the content-encoding header
            response.headers["content-encoding"] = responseEncoding
            return response
        else:
            Logger.Debug("No Content-Encoding header found")
            return oldResponse
