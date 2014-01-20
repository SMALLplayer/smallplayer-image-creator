# -*- coding: utf-8 -*-

'''
    GOmovies XBMC Addon
    Copyright (C) 2014 lambda

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import urllib,urllib2,re,os,threading,datetime,time,base64,xbmc,xbmcplugin,xbmcgui,xbmcaddon,xbmcvfs
from operator import itemgetter
try:    import json
except: import simplejson as json
try:    import CommonFunctions
except: import commonfunctionsdummy as CommonFunctions
try:    import StorageServer
except: import storageserverdummy as StorageServer
from metahandler import metahandlers
from metahandler import metacontainers
import urlresolver


language            = xbmcaddon.Addon().getLocalizedString
setSetting          = xbmcaddon.Addon().setSetting
getSetting          = xbmcaddon.Addon().getSetting
addonName           = xbmcaddon.Addon().getAddonInfo("name")
addonVersion        = xbmcaddon.Addon().getAddonInfo("version")
addonId             = xbmcaddon.Addon().getAddonInfo("id")
addonPath           = xbmcaddon.Addon().getAddonInfo("path")
addonDesc           = language(40450).encode("utf-8")
addonIcon           = os.path.join(addonPath,'icon.png')
addonFanart         = os.path.join(addonPath,'fanart.jpg')
addonArt            = os.path.join(addonPath,'resources/art')
addonPoster         = os.path.join(addonPath,'resources/art/Poster.png')
addonDownloads      = os.path.join(addonPath,'resources/art/Downloads.png')
addonGenres         = os.path.join(addonPath,'resources/art/Genres.png')
addonYears          = os.path.join(addonPath,'resources/art/Years.png')
addonAccount1       = os.path.join(addonPath,'resources/art/Watch-List.png')
addonAccount2       = os.path.join(addonPath,'resources/art/Watch-Added.png')
addonAccount3       = os.path.join(addonPath,'resources/art/Watch-Title.png')
addonAccount4       = os.path.join(addonPath,'resources/art/Lists.png')
addonNext           = os.path.join(addonPath,'resources/art/Next.png')
dataPath            = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
viewData            = os.path.join(dataPath,'views.cfg')
favData             = os.path.join(dataPath,'favourites.cfg')
metaget             = metahandlers.MetaData(preparezip=False)
cache               = StorageServer.StorageServer(addonName+addonVersion,1).cacheFunction
cache2              = StorageServer.StorageServer(addonName+addonVersion,24).cacheFunction
cache3              = StorageServer.StorageServer(addonName+addonVersion,720).cacheFunction
common              = CommonFunctions
action              = None


class main:
    def __init__(self):
        global action
        index().container_data()
        params = {}
        splitparams = sys.argv[2][sys.argv[2].find('?') + 1:].split('&')
        for param in splitparams:
            if (len(param) > 0):
                splitparam = param.split('=')
                key = splitparam[0]
                try:    value = splitparam[1].encode("utf-8")
                except: value = splitparam[1]
                params[key] = value

        try:        action = urllib.unquote_plus(params["action"])
        except:     action = None
        try:        name = urllib.unquote_plus(params["name"])
        except:     name = None
        try:        url = urllib.unquote_plus(params["url"])
        except:     url = None
        try:        image = urllib.unquote_plus(params["image"])
        except:     image = None
        try:        query = urllib.unquote_plus(params["query"])
        except:     query = None
        try:        title = urllib.unquote_plus(params["title"])
        except:     title = None
        try:        year = urllib.unquote_plus(params["year"])
        except:     year = None
        try:        imdb = urllib.unquote_plus(params["imdb"])
        except:     imdb = None

        if action == None:                          root().get()
        elif action == 'item_play':                 contextMenu().item_play()
        elif action == 'item_random_play':          contextMenu().item_random_play()
        elif action == 'item_queue':                contextMenu().item_queue()
        elif action == 'favourite_add':             contextMenu().favourite_add(favData, name, url, image, imdb, year)
        elif action == 'favourite_from_search':     contextMenu().favourite_from_search(favData, name, url, image, imdb, year)
        elif action == 'favourite_delete':          contextMenu().favourite_delete(favData, name, url)
        elif action == 'favourite_moveUp':          contextMenu().favourite_moveUp(favData, name, url)
        elif action == 'favourite_moveDown':        contextMenu().favourite_moveDown(favData, name, url)
        elif action == 'playlist_open':             contextMenu().playlist_open()
        elif action == 'settings_open':             contextMenu().settings_open()
        elif action == 'addon_home':                contextMenu().addon_home()
        elif action == 'view_movies':               contextMenu().view('movies')
        elif action == 'metadata_movies':           contextMenu().metadata('movie', imdb, '', '')
        elif action == 'metadata_movies2':          contextMenu().metadata('movie', imdb, '', '')
        elif action == 'playcount_movies':          contextMenu().playcount('movie', imdb, '', '')
        elif action == 'library':                   contextMenu().library(name, title, imdb, year, url)
        elif action == 'download':                  contextMenu().download(name, title, imdb, year, url)
        elif action == 'sources':                   contextMenu().sources(name, title, imdb, year, url)
        elif action == 'autoplay':                  contextMenu().autoplay(name, title, imdb, year, url)
        elif action == 'trailer':                   contextMenu().trailer(name, url)
        elif action == 'movies':                    movies().imdb(url)
        elif action == 'movies_popular':            movies().imdb_popular()
        elif action == 'movies_boxoffice':          movies().imdb_boxoffice()
        elif action == 'movies_views':              movies().imdb_views()
        elif action == 'movies_oscars':             movies().imdb_oscars()
        elif action == 'movies_search':             movies().imdb_search(query)
        elif action == 'movies_favourites':         favourites().movies()
        elif action == 'genres_movies':             genres().imdb()
        elif action == 'years_movies':              years().imdb()
        elif action == 'account_movies':            mymovies().account()
        elif action == 'mymovies':                  mymovies().imdb(url)
        elif action == 'play':                      resolver().run(name, title, imdb, year, url)

        if action is None:
            pass
        elif action.startswith('movies') or action.startswith('mymovies'):
            xbmcplugin.setContent(int(sys.argv[1]), 'movies')
            index().container_view('movies', {'skin.confluence' : 500})
        xbmcplugin.setPluginFanart(int(sys.argv[1]), addonFanart)
        xbmcplugin.endOfDirectory(int(sys.argv[1]))
        return

class getUrl(object):
    def __init__(self, url, fetch=True, close=True, cookie=False, mobile=False, proxy=None, post=None, referer=None):
        if not proxy is None:
            proxy_handler = urllib2.ProxyHandler({'http':'%s' % (proxy)})
            opener = urllib2.build_opener(proxy_handler, urllib2.HTTPHandler)
            opener = urllib2.install_opener(opener)
        if cookie == True:
            import cookielib
            cookie_handler = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
            opener = urllib2.build_opener(cookie_handler, urllib2.HTTPBasicAuthHandler(), urllib2.HTTPHandler())
            opener = urllib2.install_opener(opener)
        if not post is None:
            request = urllib2.Request(url, post)
        else:
            request = urllib2.Request(url,None)
        if mobile == True:
            request.add_header('User-Agent', 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7')
        else:
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0')
        if not referer is None:
            request.add_header('Referer', referer)
        response = urllib2.urlopen(request, timeout=10)
        if fetch == True:
            result = response.read()
        else:
            result = response.geturl()
        if close == True:
            response.close()
        self.result = result

class uniqueList(object):
    def __init__(self, list):
        uniqueSet = set()
        uniqueList = []
        for n in list:
            if n not in uniqueSet:
                uniqueSet.add(n)
                uniqueList.append(n)
        self.list = uniqueList

class Thread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args
        threading.Thread.__init__(self)
    def run(self):
        self._target(*self._args)

class player(xbmc.Player):
    def __init__ (self):
        self.property = addonName+'player_status'
        xbmc.Player.__init__(self)

    def status(self):
        getProperty = index().getProperty(self.property)
        index().clearProperty(self.property)
        if not xbmc.getInfoLabel('Container.FolderPath') == '': return
        if getProperty == 'true': return True
        return

    def run(self, name, url, imdb='0'):
        if xbmc.getInfoLabel('Container.FolderPath').startswith(sys.argv[0]):
            item = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
        else:
            try:
                file = name + '.strm'
                file = file.translate(None, '\/:*?"<>|')

                meta = xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.GetMovies", "params": {"properties" : ["title", "genre", "year", "rating", "director", "trailer", "tagline", "plot", "plotoutline", "originaltitle", "lastplayed", "playcount", "writer", "studio", "mpaa", "country", "imdbnumber", "runtime", "votes", "fanart", "thumbnail", "file", "sorttitle", "resume", "dateadded"]}, "id": 1}')
                meta = unicode(meta, 'utf-8', errors='ignore')
                meta = json.loads(meta)
                meta = meta['result']['movies']
                self.meta = [i for i in meta if i['file'].endswith(file)][0]
                meta = {'title': self.meta['title'], 'originaltitle': self.meta['originaltitle'], 'year': self.meta['year'], 'genre': str(self.meta['genre']).replace("[u'", '').replace("']", '').replace("', u'", ' / '), 'director': str(self.meta['director']).replace("[u'", '').replace("']", '').replace("', u'", ' / '), 'country': str(self.meta['country']).replace("[u'", '').replace("']", '').replace("', u'", ' / '), 'rating': self.meta['rating'], 'votes': self.meta['votes'], 'mpaa': self.meta['mpaa'], 'duration': self.meta['runtime'], 'trailer': self.meta['trailer'], 'writer': str(self.meta['writer']).replace("[u'", '').replace("']", '').replace("', u'", ' / '), 'studio': str(self.meta['studio']).replace("[u'", '').replace("']", '').replace("', u'", ' / '), 'tagline': self.meta['tagline'], 'plotoutline': self.meta['plotoutline'], 'plot': self.meta['plot']}
                poster = self.meta['thumbnail']
            except:
                meta = {'label' : name, 'title' : name}
                poster = ''
            item = xbmcgui.ListItem(path=url, iconImage="DefaultVideo.png", thumbnailImage=poster)
            item.setInfo( type="Video", infoLabels= meta )
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)

        for i in range(1, 21):
            try: self.totalTime = self.getTotalTime()
            except: self.totalTime = 0
            if not self.totalTime == 0: continue
            xbmc.sleep(1000)
        if self.totalTime == 0: return

        subtitles().get(name)

        self.content = 'movie'
        self.season = str(xbmc.getInfoLabel('VideoPlayer.season'))
        self.episode = str(xbmc.getInfoLabel('VideoPlayer.episode'))
        if imdb == '0': imdb = metaget.get_meta('movie', xbmc.getInfoLabel('VideoPlayer.title') ,year=str(xbmc.getInfoLabel('VideoPlayer.year')))['imdb_id']
        imdb = re.sub("[^0-9]", "", imdb)
        self.imdb = imdb

        while True:
            try: self.currentTime = self.getTime()
            except: break
            xbmc.sleep(1000)

    def onPlayBackEnded(self):
        if xbmc.getInfoLabel('Container.FolderPath') == '': index().setProperty(self.property, 'true')
        if xbmc.getInfoLabel('Container.FolderPath').startswith(sys.argv[0]):
            metaget.change_watched(self.content, '', self.imdb, season=self.season, episode=self.episode, year='', watched='')
            index().container_refresh()
        else:
            try: xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "playcount" : 1 }, "id": 1 }' % str(self.meta['movieid']))
            except: pass

    def onPlayBackStopped(self):
        index().clearProperty(self.property)
        if not self.currentTime / self.totalTime >= .9: return
        if xbmc.getInfoLabel('Container.FolderPath').startswith(sys.argv[0]):
            metaget.change_watched(self.content, '', self.imdb, season=self.season, episode=self.episode, year='', watched='')
            index().container_refresh()
        else:
            try: xbmc.executeJSONRPC('{"jsonrpc": "2.0", "method": "VideoLibrary.SetMovieDetails", "params": {"movieid" : %s, "playcount" : 1 }, "id": 1 }' % str(self.meta['movieid']))
            except: pass

class subtitles:
    def get(self, name):
        subs = getSetting("subs")
        if subs == '1': self.greek(name)

    def greek(self, name):
        try:
            import shutil, zipfile, time
            sub_tmp = os.path.join(dataPath,'sub_tmp')
            sub_tmp2 = os.path.join(sub_tmp, "subs")
            sub_stream = os.path.join(dataPath,'sub_stream')
            sub_file = os.path.join(sub_tmp, 'sub_tmp.zip')
            try: os.makedirs(dataPath)
            except: pass
            try: os.remove(sub_tmp)
            except: pass
            try: shutil.rmtree(sub_tmp)
            except: pass
            try: os.makedirs(sub_tmp)
            except: pass
            try: os.remove(sub_stream)
            except: pass
            try: shutil.rmtree(sub_stream)
            except: pass
            try: os.makedirs(sub_stream)
            except: pass

            subtitles = []
            query = ''.join(e for e in name if e.isalnum() or e == ' ')
            query = urllib.quote_plus(query)
            url = 'http://www.greeksubtitles.info/search.php?name=' + query
            result = getUrl(url).result
            result = result.decode('iso-8859-7').encode('utf-8')
            result = result.lower().replace('"',"'")
            match = "get_greek_subtitles[.]php[?]id=(.+?)'.+?%s.+?<"
            quality = ['bluray', 'brrip', 'bdrip', 'dvdrip', 'hdtv']
            for q in quality:
                subtitles += re.compile(match % q).findall(result)
            if subtitles == []: raise Exception()
            for subtitle in subtitles:
                url = 'http://www.findsubtitles.eu/getp.php?id=' + subtitle
                response = urllib.urlopen(url)
                content = response.read()
                response.close()
                if content[:4] == 'PK': break

            file = open(sub_file, 'wb')
            file.write(content)
            file.close()
            file = zipfile.ZipFile(sub_file, 'r')
            file.extractall(sub_tmp)
            file.close()
            files = os.listdir(sub_tmp2)
            if files == []: raise Exception()
            file = [i for i in files if i.endswith('.srt') or i.endswith('.sub')]
            if file == []:
                pack = [i for i in files if i.endswith('.zip') or i.endswith('.rar')]
                pack = os.path.join(sub_tmp2, pack[0])
                xbmc.executebuiltin('Extract("%s","%s")' % (pack, sub_tmp2))
                time.sleep(1)
            files = os.listdir(sub_tmp2)
            file = [i for i in files if i.endswith('.srt') or i.endswith('.sub')][0]
            copy = os.path.join(sub_tmp2, file)
            shutil.copy(copy, sub_stream)
            try: shutil.rmtree(sub_tmp)
            except: pass
            file = os.path.join(sub_stream, file)
            if not os.path.isfile(file): raise Exception()

            xbmc.Player().setSubtitles(file)
        except:
            try: shutil.rmtree(sub_tmp)
            except: pass
            try: shutil.rmtree(sub_stream)
            except: pass
            index().infoDialog(language(30317).encode("utf-8"), name)
            return

class index:
    def infoDialog(self, str, header=addonName):
        try: xbmcgui.Dialog().notification(header, str, addonIcon, 3000, sound=False)
        except: xbmc.executebuiltin("Notification(%s,%s, 3000, %s)" % (header, str, addonIcon))

    def okDialog(self, str1, str2, header=addonName):
        xbmcgui.Dialog().ok(header, str1, str2)

    def selectDialog(self, list, header=addonName):
        select = xbmcgui.Dialog().select(header, list)
        return select

    def yesnoDialog(self, str1, str2, header=addonName):
        answer = xbmcgui.Dialog().yesno(header, str1, str2)
        return answer

    def getProperty(self, str):
        property = xbmcgui.Window(10000).getProperty(str)
        return property

    def setProperty(self, str1, str2):
        xbmcgui.Window(10000).setProperty(str1, str2)

    def clearProperty(self, str):
        xbmcgui.Window(10000).clearProperty(str)

    def addon_status(self, id):
        check = xbmcaddon.Addon(id=id).getAddonInfo("name")
        if not check == addonName: return True

    def container_refresh(self):
        xbmc.executebuiltin("Container.Refresh")

    def container_data(self):
        if not xbmcvfs.exists(dataPath):
            xbmcvfs.mkdir(dataPath)
        if not xbmcvfs.exists(favData):
            file = xbmcvfs.File(favData, 'w')
            file.write('')
            file.close()
        if not xbmcvfs.exists(viewData):
            file = xbmcvfs.File(viewData, 'w')
            file.write('')
            file.close()

    def container_view(self, content, viewDict):
        try:
            skin = xbmc.getSkinDir()
            file = xbmcvfs.File(viewData)
            read = file.read().replace('\n','')
            file.close()
            view = re.compile('"%s"[|]"%s"[|]"(.+?)"' % (skin, content)).findall(read)[0]
            xbmc.executebuiltin('Container.SetViewMode(%s)' % str(view))
        except:
            try:
                id = str(viewDict[skin])
                xbmc.executebuiltin('Container.SetViewMode(%s)' % id)
            except:
                pass

    def rootList(self, rootList):
        total = len(rootList)
        for i in rootList:
            try:
                name = language(i['name']).encode("utf-8")
                image = '%s/%s' % (addonArt, i['image'])
                action = i['action']
                u = '%s?action=%s' % (sys.argv[0], action)

                item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=image)
                item.setInfo( type="Video", infoLabels={ "Label": name, "Title": name, "Plot": addonDesc } )
                item.setProperty("Fanart_Image", addonFanart)
                item.addContextMenuItems([], replaceItems=False)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=total,isFolder=True)
            except:
                pass

    def pageList(self, pageList):
        if pageList == None: return

        total = len(pageList)
        for i in pageList:
            try:
                name, url, image = i['name'], i['url'], i['image']
                sysname, sysurl, sysimage = urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(image)

                if action == 'account_movies':
                    u = '%s?action=mymovies&url=%s' % (sys.argv[0], sysurl)
                else:
                    u = '%s?action=movies&url=%s' % (sys.argv[0], sysurl)

                item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=image)
                item.setInfo( type="Video", infoLabels={ "Label": name, "Title": name, "Plot": addonDesc } )
                item.setProperty("Fanart_Image", addonFanart)
                item.addContextMenuItems([], replaceItems=False)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=total,isFolder=True)
            except:
                pass

    def nextList(self, nextList):
        try: next = nextList[0]['next']
        except: return
        if next == '': return
        name, url, image = language(30361).encode("utf-8"), next, addonNext
        sysurl = urllib.quote_plus(url)

        if action == 'mymovies':
            u = '%s?action=mymovies&url=%s' % (sys.argv[0], sysurl)
        else:
            u = '%s?action=movies&url=%s' % (sys.argv[0], sysurl)

        item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=image)
        item.setInfo( type="Video", infoLabels={ "Label": name, "Title": name, "Plot": addonDesc } )
        item.setProperty("Fanart_Image", addonFanart)
        item.addContextMenuItems([], replaceItems=False)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=True)

    def downloadList(self):
        u = getSetting("downloads")
        if u == '': return
        name, image = language(30363).encode("utf-8"), addonDownloads

        item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=image)
        item.setInfo( type="Video", infoLabels={ "Label": name, "Title": name, "Plot": addonDesc } )
        item.setProperty("Fanart_Image", addonFanart)
        item.addContextMenuItems([], replaceItems=False)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,isFolder=True)

    def movieList(self, movieList):
        if movieList == None: return

        file = xbmcvfs.File(favData)
        favRead = file.read()
        file.close()

        total = len(movieList)
        for i in movieList:
            try:
                name, url, image, title, year, imdb, genre, plot = i['name'], i['url'], i['image'], i['title'], i['year'], i['imdb'], i['genre'], i['plot']
                if plot == '': plot = addonDesc
                if genre == '': genre = ' '

                sysname, sysurl, sysimage, systitle, sysyear, sysimdb = urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(image), urllib.quote_plus(title), urllib.quote_plus(year), urllib.quote_plus(imdb)
                u = '%s?action=play&name=%s&title=%s&imdb=%s&year=%s&url=%s&t=%s' % (sys.argv[0], sysname, systitle, sysimdb, sysyear, sysurl, datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))

                if getSetting("meta") == 'true':
                    meta = metaget.get_meta('movie', title ,year=year)
                    playcountMenu = language(30407).encode("utf-8")
                    if meta['overlay'] == 6: playcountMenu = language(30408).encode("utf-8")
                    metaimdb = urllib.quote_plus(re.sub("[^0-9]", "", meta['imdb_id']))
                    trailer, poster = urllib.quote_plus(meta['trailer_url']), meta['cover_url']
                    if trailer == '': trailer = sysurl
                    if poster == '': poster = image
                else:
                    meta = {'label': title, 'title': title, 'year': year, 'imdb_id' : imdb, 'genre' : genre, 'plot': plot}
                    trailer, poster = sysurl, image
                if getSetting("meta") == 'true' and getSetting("fanart") == 'true':
                    fanart = meta['backdrop_url']
                    if fanart == '': fanart = addonFanart
                else:
                    fanart = addonFanart

                cm = []
                if getSetting("autoplay") == 'true': cm.append((language(30432).encode("utf-8"), 'RunPlugin(%s?action=sources&name=%s&title=%s&imdb=%s&year=%s&url=%s)' % (sys.argv[0], sysname, systitle, sysimdb, sysyear, sysurl)))
                else: cm.append((language(30433).encode("utf-8"), 'RunPlugin(%s?action=autoplay&name=%s&title=%s&imdb=%s&year=%s&url=%s)' % (sys.argv[0], sysname, systitle, sysimdb, sysyear, sysurl)))
                cm.append((language(30405).encode("utf-8"), 'RunPlugin(%s?action=item_queue)' % (sys.argv[0])))
                cm.append((language(30406).encode("utf-8"), 'RunPlugin(%s?action=download&name=%s&title=%s&imdb=%s&year=%s&url=%s)' % (sys.argv[0], sysname, systitle, sysimdb, sysyear, sysurl)))

                if action == 'movies_favourites':
                    if not getSetting("fav_sort") == '2': cm.append((language(30412).encode("utf-8"), 'Action(Info)'))
                    if not getSetting("fav_sort") == '2': cm.append((language(30416).encode("utf-8"), 'RunPlugin(%s?action=trailer&name=%s&url=%s)' % (sys.argv[0], sysname, trailer)))
                    if getSetting("meta") == 'true': cm.append((language(30415).encode("utf-8"), 'RunPlugin(%s?action=metadata_movies&imdb=%s)' % (sys.argv[0], metaimdb)))
                    if getSetting("meta") == 'true': cm.append((playcountMenu, 'RunPlugin(%s?action=playcount_movies&imdb=%s)' % (sys.argv[0], metaimdb)))
                    cm.append((language(30422).encode("utf-8"), 'RunPlugin(%s?action=library&name=%s&title=%s&imdb=%s&year=%s&url=%s)' % (sys.argv[0], sysname, systitle, sysimdb, sysyear, sysurl)))
                    cm.append((language(30428).encode("utf-8"), 'RunPlugin(%s?action=view_movies)' % (sys.argv[0])))
                    if getSetting("fav_sort") == '2': cm.append((language(30419).encode("utf-8"), 'RunPlugin(%s?action=favourite_moveUp&name=%s&url=%s)' % (sys.argv[0], systitle, sysurl)))
                    if getSetting("fav_sort") == '2': cm.append((language(30420).encode("utf-8"), 'RunPlugin(%s?action=favourite_moveDown&name=%s&url=%s)' % (sys.argv[0], systitle, sysurl)))
                    cm.append((language(30421).encode("utf-8"), 'RunPlugin(%s?action=favourite_delete&name=%s&url=%s)' % (sys.argv[0], systitle, sysurl)))
                elif action == 'movies_search':
                    cm.append((language(30412).encode("utf-8"), 'Action(Info)'))
                    cm.append((language(30416).encode("utf-8"), 'RunPlugin(%s?action=trailer&name=%s&url=%s)' % (sys.argv[0], sysname, trailer)))
                    cm.append((language(30422).encode("utf-8"), 'RunPlugin(%s?action=library&name=%s&title=%s&imdb=%s&year=%s&url=%s)' % (sys.argv[0], sysname, systitle, sysimdb, sysyear, sysurl)))
                    cm.append((language(30417).encode("utf-8"), 'RunPlugin(%s?action=favourite_from_search&name=%s&imdb=%s&url=%s&image=%s&year=%s)' % (sys.argv[0], systitle, sysimdb, sysurl, sysimage, sysyear)))
                    cm.append((language(30428).encode("utf-8"), 'RunPlugin(%s?action=view_movies)' % (sys.argv[0])))
                    cm.append((language(30409).encode("utf-8"), 'RunPlugin(%s?action=settings_open)' % (sys.argv[0])))
                    cm.append((language(30411).encode("utf-8"), 'RunPlugin(%s?action=addon_home)' % (sys.argv[0])))
                elif action == 'mymovies':
                    cm.append((language(30412).encode("utf-8"), 'Action(Info)'))
                    cm.append((language(30416).encode("utf-8"), 'RunPlugin(%s?action=trailer&name=%s&url=%s)' % (sys.argv[0], sysname, trailer)))
                    if getSetting("meta") == 'true': cm.append((language(30415).encode("utf-8"), 'RunPlugin(%s?action=metadata_movies2&imdb=%s)' % (sys.argv[0], metaimdb)))
                    if getSetting("meta") == 'true': cm.append((playcountMenu, 'RunPlugin(%s?action=playcount_movies&imdb=%s)' % (sys.argv[0], metaimdb)))
                    cm.append((language(30422).encode("utf-8"), 'RunPlugin(%s?action=library&name=%s&title=%s&imdb=%s&year=%s&url=%s)' % (sys.argv[0], sysname, systitle, sysimdb, sysyear, sysurl)))
                    if not '"%s"' % url in favRead: cm.append((language(30417).encode("utf-8"), 'RunPlugin(%s?action=favourite_add&name=%s&imdb=%s&url=%s&image=%s&year=%s)' % (sys.argv[0], systitle, sysimdb, sysurl, sysimage, sysyear)))
                    else: cm.append((language(30418).encode("utf-8"), 'RunPlugin(%s?action=favourite_delete&name=%s&url=%s)' % (sys.argv[0], systitle, sysurl)))
                    cm.append((language(30428).encode("utf-8"), 'RunPlugin(%s?action=view_movies)' % (sys.argv[0])))
                else:
                    cm.append((language(30412).encode("utf-8"), 'Action(Info)'))
                    cm.append((language(30416).encode("utf-8"), 'RunPlugin(%s?action=trailer&name=%s&url=%s)' % (sys.argv[0], sysname, trailer)))
                    if getSetting("meta") == 'true': cm.append((language(30415).encode("utf-8"), 'RunPlugin(%s?action=metadata_movies2&imdb=%s)' % (sys.argv[0], metaimdb)))
                    cm.append((language(30422).encode("utf-8"), 'RunPlugin(%s?action=library&name=%s&title=%s&imdb=%s&year=%s&url=%s)' % (sys.argv[0], sysname, systitle, sysimdb, sysyear, sysurl)))
                    if not '"%s"' % url in favRead: cm.append((language(30417).encode("utf-8"), 'RunPlugin(%s?action=favourite_add&name=%s&imdb=%s&url=%s&image=%s&year=%s)' % (sys.argv[0], systitle, sysimdb, sysurl, sysimage, sysyear)))
                    else: cm.append((language(30418).encode("utf-8"), 'RunPlugin(%s?action=favourite_delete&name=%s&url=%s)' % (sys.argv[0], systitle, sysurl)))
                    cm.append((language(30428).encode("utf-8"), 'RunPlugin(%s?action=view_movies)' % (sys.argv[0])))
                    cm.append((language(30411).encode("utf-8"), 'RunPlugin(%s?action=addon_home)' % (sys.argv[0])))

                item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=poster)
                item.setInfo( type="Video", infoLabels = meta )
                item.setProperty("IsPlayable", "true")
                item.setProperty("Video", "true")
                item.setProperty("art(poster)", poster)
                item.setProperty("Fanart_Image", fanart)
                item.addContextMenuItems(cm, replaceItems=True)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=total,isFolder=False)
            except:
                pass

class contextMenu:
    def item_play(self):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        xbmc.executebuiltin('Action(Queue)')
        playlist.unshuffle()
        xbmc.Player().play(playlist)

    def item_random_play(self):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        xbmc.executebuiltin('Action(Queue)')
        playlist.shuffle()
        xbmc.Player().play(playlist)

    def item_queue(self):
        xbmc.executebuiltin('Action(Queue)')

    def playlist_open(self):
        xbmc.executebuiltin('ActivateWindow(VideoPlaylist)')

    def settings_open(self):
        xbmc.executebuiltin('Addon.OpenSettings(%s)' % (addonId))

    def addon_home(self):
        xbmc.executebuiltin('Container.Update(plugin://%s/,replace)' % (addonId))

    def view(self, content):
        try:
            skin = xbmc.getSkinDir()
            if xbmcvfs.exists(xbmc.translatePath('special://xbmc/addons/%s/addon.xml' % (skin))):
                xml = xbmc.translatePath('special://xbmc/addons/%s/addon.xml' % (skin))
            elif xbmcvfs.exists(xbmc.translatePath('special://home/addons/%s/addon.xml' % (skin))):
                xml = xbmc.translatePath('special://home/addons/%s/addon.xml' % (skin))
            else:
                return
            file = xbmcvfs.File(xml)
            read = file.read().replace('\n','')
            file.close()
            src = os.path.dirname(xml) + '/'
            try:
                src += re.compile('defaultresolution="(.+?)"').findall(read)[0] + '/'
            except:
                src += re.compile('<res.+?folder="(.+?)"').findall(read)[0] + '/'
            src += 'MyVideoNav.xml'
            file = xbmcvfs.File(src)
            read = file.read().replace('\n','')
            file.close()
            views = re.compile('<views>(.+?)</views>').findall(read)[0]
            views = [int(x) for x in views.split(',')]
            for view in views:
                label = xbmc.getInfoLabel('Control.GetLabel(%s)' % (view))
                if not (label == '' or label is None): break
            file = xbmcvfs.File(viewData)
            read = file.read()
            file.close()
            file = open(viewData, 'w')
            for line in re.compile('(".+?\n)').findall(read):
                if not line.startswith('"%s"|"%s"|"' % (skin, content)): file.write(line)
            file.write('"%s"|"%s"|"%s"\n' % (skin, content, str(view)))
            file.close()
            viewName = xbmc.getInfoLabel('Container.Viewmode')
            index().infoDialog('%s%s%s' % (language(30301).encode("utf-8"), viewName, language(30302).encode("utf-8")))
        except:
            return

    def favourite_add(self, data, name, url, image, imdb, year):
        try:
            index().container_refresh()
            file = open(data, 'a+')
            file.write('"%s"|"%s"|"%s"|"%s"|"%s"\n' % (name, year, imdb, url, image))
            file.close()
            index().infoDialog(language(30303).encode("utf-8"), name)
        except:
            return

    def favourite_from_search(self, data, name, url, image, imdb, year):
        try:
            file = xbmcvfs.File(data)
            read = file.read()
            file.close()
            if url in read:
                index().infoDialog(language(30307).encode("utf-8"), name)
                return
            file = open(data, 'a+')
            file.write('"%s"|"%s"|"%s"|"%s"|"%s"\n' % (name, year, imdb, url, image))
            file.close()
            index().infoDialog(language(30303).encode("utf-8"), name)
        except:
            return

    def favourite_delete(self, data, name, url):
        try:
            index().container_refresh()
            file = xbmcvfs.File(data)
            read = file.read()
            file.close()
            line = [x for x in re.compile('(".+?)\n').findall(read) if '"%s"' % url in x][0]
            list = re.compile('(".+?\n)').findall(read.replace(line, ''))
            file = open(data, 'w')
            for line in list: file.write(line)
            file.close()
            index().infoDialog(language(30304).encode("utf-8"), name)
        except:
            return

    def favourite_moveUp(self, data, name, url):
        try:
            index().container_refresh()
            file = xbmcvfs.File(data)
            read = file.read()
            file.close()
            list = re.compile('(".+?)\n').findall(read)
            line = [x for x in re.compile('(".+?)\n').findall(read) if '"%s"' % url in x][0]
            i = list.index(line)
            if i == 0 : return
            list[i], list[i-1] = list[i-1], list[i]
            file = open(data, 'w')
            for line in list: file.write('%s\n' % (line))
            file.close()
            index().infoDialog(language(30305).encode("utf-8"), name)
        except:
            return

    def favourite_moveDown(self, data, name, url):
        try:
            index().container_refresh()
            file = xbmcvfs.File(data)
            read = file.read()
            file.close()
            list = re.compile('(".+?)\n').findall(read)
            line = [x for x in re.compile('(".+?)\n').findall(read) if '"%s"' % url in x][0]
            i = list.index(line)
            if i+1 == len(list): return
            list[i], list[i+1] = list[i+1], list[i]
            file = open(data, 'w')
            for line in list: file.write('%s\n' % (line))
            file.close()
            index().infoDialog(language(30306).encode("utf-8"), name)
        except:
            return

    def metadata(self, content, imdb, season, episode):
        try:
            if content == 'movie' or content == 'tvshow':
                metaget.update_meta(content, '', imdb, year='')
                index().container_refresh()
            elif content == 'season':
                metaget.update_episode_meta('', imdb, season, episode)
                index().container_refresh()
            elif content == 'episode':
                metaget.update_season('', imdb, season)
                index().container_refresh()
        except:
            return

    def playcount(self, content, imdb, season, episode):
        try:
            metaget.change_watched(content, '', imdb, season=season, episode=episode, year='', watched='')
            index().container_refresh()
        except:
            return

    def library(self, name, title, imdb, year, url, silent=False):
        try:
            library = xbmc.translatePath(getSetting("movie_library"))
            sysname, systitle, sysimdb, sysyear = urllib.quote_plus(name), urllib.quote_plus(title), urllib.quote_plus(imdb), urllib.quote_plus(year)
            content = '%s?action=play&name=%s&title=%s&imdb=%s&year=%s' % (sys.argv[0], sysname, systitle, sysimdb, sysyear)
            enc_name = name.translate(None, '\/:*?"<>|')
            folder = os.path.join(library, enc_name)
            stream = os.path.join(folder, enc_name + '.strm')
            xbmcvfs.mkdir(dataPath)
            xbmcvfs.mkdir(library)
            xbmcvfs.mkdir(folder)
            file = xbmcvfs.File(stream, 'w')
            file.write(content)
            file.close()
            if silent == False:
                index().infoDialog(language(30311).encode("utf-8"), name)
        except:
            return

    def download(self, name, title, imdb, year, url):
        try:
            property = (addonName+name)+'download'
            download = xbmc.translatePath(getSetting("downloads"))
            enc_name = name.translate(None, '\/:*?"<>|')
            xbmcvfs.mkdir(dataPath)
            xbmcvfs.mkdir(download)

            file = [i for i in xbmcvfs.listdir(download)[1] if i.startswith(enc_name + '.')]
            if not file == []: file = os.path.join(download, file[0])
            else: file = None

            if download == '':
            	yes = index().yesnoDialog(language(30341).encode("utf-8"), language(30342).encode("utf-8"))
            	if yes: contextMenu().settings_open()
            	return

            if file is None:
            	pass
            elif not file.endswith('.tmp'):
            	yes = index().yesnoDialog(language(30343).encode("utf-8"), language(30344).encode("utf-8"), name)
            	if yes:
            	    xbmcvfs.delete(file)
            	else:
            	    return
            elif file.endswith('.tmp'):
            	if index().getProperty(property) == 'open':
            	    yes = index().yesnoDialog(language(30345).encode("utf-8"), language(30346).encode("utf-8"), name)
            	    if yes: index().setProperty(property, 'cancel')
            	    return
            	else:
            	    xbmcvfs.delete(file)

            url = resolver().run(name, title, imdb, year, 'download://')
            if url is None: return
            ext = url.rsplit('/', 1)[-1].rsplit('?', 1)[0].rsplit('|', 1)[0].strip().lower()
            ext = os.path.splitext(ext)[1][1:]
            if ext == '': ext = 'mp4'
            stream = os.path.join(download, enc_name + '.' + ext)
            temp = stream + '.tmp'

            count = 0
            CHUNK = 16 * 1024
            request = urllib2.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_0 like Mac OS X; en-us) AppleWebKit/532.9 (KHTML, like Gecko) Version/4.0.5 Mobile/8A293 Safari/6531.22.7')
            request.add_header('Cookie', 'video=true') #add cookie
            response = urllib2.urlopen(request, timeout=10)
            size = response.info()["Content-Length"]

            file = xbmcvfs.File(temp, 'w')
            index().setProperty(property, 'open')
            index().infoDialog(language(30308).encode("utf-8"), name)
            while True:
            	chunk = response.read(CHUNK)
            	if not chunk: break
            	if index().getProperty(property) == 'cancel': raise Exception()
            	if xbmc.abortRequested == True: raise Exception()
            	part = xbmcvfs.File(temp)
            	quota = int(100 * float(part.size())/float(size))
            	part.close()
            	if not count == quota and count in [0,10,20,30,40,50,60,70,80,90]:
            		index().infoDialog(language(30309).encode("utf-8") + str(count) + '%', name)
            	file.write(chunk)
            	count = quota
            response.close()
            file.close()

            index().clearProperty(property)
            xbmcvfs.rename(temp, stream)
            index().infoDialog(language(30310).encode("utf-8"), name)
        except:
            file.close()
            index().clearProperty(property)
            xbmcvfs.delete(temp)
            sys.exit()
            return

    def sources(self, name, title, imdb, year, url):
        meta = {'title': xbmc.getInfoLabel('ListItem.title'), 'originaltitle': xbmc.getInfoLabel('ListItem.originaltitle'), 'year': xbmc.getInfoLabel('ListItem.year'), 'genre': xbmc.getInfoLabel('ListItem.genre'), 'director': xbmc.getInfoLabel('ListItem.director'), 'country': xbmc.getInfoLabel('ListItem.country'), 'rating': xbmc.getInfoLabel('ListItem.rating'), 'votes': xbmc.getInfoLabel('ListItem.votes'), 'mpaa': xbmc.getInfoLabel('ListItem.mpaa'), 'duration': xbmc.getInfoLabel('ListItem.duration'), 'trailer': xbmc.getInfoLabel('ListItem.trailer'), 'writer': xbmc.getInfoLabel('ListItem.writer'), 'studio': xbmc.getInfoLabel('ListItem.studio'), 'tagline': xbmc.getInfoLabel('ListItem.tagline'), 'plotoutline': xbmc.getInfoLabel('ListItem.plotoutline'), 'plot': xbmc.getInfoLabel('ListItem.plot')}
        label, poster, fanart = xbmc.getInfoLabel('ListItem.label'), xbmc.getInfoLabel('ListItem.icon'), xbmc.getInfoLabel('ListItem.Property(Fanart_Image)')

        sysname, systitle, sysimdb, sysyear = urllib.quote_plus(name), urllib.quote_plus(title), urllib.quote_plus(imdb), urllib.quote_plus(year)
        u = '%s?action=play&name=%s&title=%s&imdb=%s&year=%s&url=sources://' % (sys.argv[0], sysname, systitle, sysimdb, sysyear)

        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        item = xbmcgui.ListItem(label, iconImage="DefaultVideo.png", thumbnailImage=poster)
        item.setInfo( type="Video", infoLabels= meta )
        item.setProperty("IsPlayable", "true")
        item.setProperty("Video", "true")
        item.setProperty("Fanart_Image", fanart)
        xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(u, item)

    def autoplay(self, name, title, imdb, year, url):
        meta = {'title': xbmc.getInfoLabel('ListItem.title'), 'originaltitle': xbmc.getInfoLabel('ListItem.originaltitle'), 'year': xbmc.getInfoLabel('ListItem.year'), 'genre': xbmc.getInfoLabel('ListItem.genre'), 'director': xbmc.getInfoLabel('ListItem.director'), 'country': xbmc.getInfoLabel('ListItem.country'), 'rating': xbmc.getInfoLabel('ListItem.rating'), 'votes': xbmc.getInfoLabel('ListItem.votes'), 'mpaa': xbmc.getInfoLabel('ListItem.mpaa'), 'duration': xbmc.getInfoLabel('ListItem.duration'), 'trailer': xbmc.getInfoLabel('ListItem.trailer'), 'writer': xbmc.getInfoLabel('ListItem.writer'), 'studio': xbmc.getInfoLabel('ListItem.studio'), 'tagline': xbmc.getInfoLabel('ListItem.tagline'), 'plotoutline': xbmc.getInfoLabel('ListItem.plotoutline'), 'plot': xbmc.getInfoLabel('ListItem.plot')}
        label, poster, fanart = xbmc.getInfoLabel('ListItem.label'), xbmc.getInfoLabel('ListItem.icon'), xbmc.getInfoLabel('ListItem.Property(Fanart_Image)')

        sysname, systitle, sysimdb, sysyear = urllib.quote_plus(name), urllib.quote_plus(title), urllib.quote_plus(imdb), urllib.quote_plus(year)
        u = '%s?action=play&name=%s&title=%s&imdb=%s&year=%s&url=play://' % (sys.argv[0], sysname, systitle, sysimdb, sysyear)

        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        item = xbmcgui.ListItem(label, iconImage="DefaultVideo.png", thumbnailImage=poster)
        item.setInfo( type="Video", infoLabels= meta )
        item.setProperty("IsPlayable", "true")
        item.setProperty("Video", "true")
        item.setProperty("Fanart_Image", fanart)
        xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(u, item)

    def trailer(self, name, url):
        url = trailer().run(name, url)
        if url is None: return
        item = xbmcgui.ListItem(path=url)
        item.setProperty("IsPlayable", "true")
        xbmc.Player(xbmc.PLAYER_CORE_AUTO).play(url, item)

class favourites:
    def __init__(self):
        self.list = []

    def movies(self):
        file = xbmcvfs.File(favData)
        read = file.read()
        file.close()

        match = re.compile('"(.+?)"[|]"(.+?)"[|]"(.+?)"[|]"(.+?)"[|]"(.+?)"').findall(read)
        for title, year, imdb, url, image in match:
            name = '%s (%s)' % (title, year)
            self.list.append({'name': name, 'url': url, 'image': image, 'title': title, 'year': year, 'imdb': imdb, 'genre': '', 'plot': ''})

        if getSetting("fav_sort") == '0':
            self.list = sorted(self.list, key=itemgetter('title'))
        elif getSetting("fav_sort") == '1':
            self.list = sorted(self.list, key=itemgetter('title'))[::-1]
            self.list = sorted(self.list, key=itemgetter('year'))[::-1]

        index().movieList(self.list)

class root:
    def get(self):
        rootList = []
        rootList.append({'name': 30501, 'image': 'BOXoffice.png', 'action': 'movies_boxoffice'})
        rootList.append({'name': 30502, 'image': 'Views.png', 'action': 'movies_views'})
        rootList.append({'name': 30503, 'image': 'Popular.png', 'action': 'movies_popular'})
        rootList.append({'name': 30504, 'image': 'Oscars.png', 'action': 'movies_oscars'})
        rootList.append({'name': 30505, 'image': 'Genres.png', 'action': 'genres_movies'})
        rootList.append({'name': 30506, 'image': 'Years.png', 'action': 'years_movies'})
        rootList.append({'name': 30507, 'image': 'Favourites.png', 'action': 'movies_favourites'})
        if not (getSetting("imdb_mail") == '' or getSetting("imdb_password") == ''):
            rootList.append({'name': 30508, 'image': 'IMDb.png', 'action': 'account_movies'})
        rootList.append({'name': 30509, 'image': 'Search.png', 'action': 'movies_search'})
        index().rootList(rootList)
        index().downloadList()

class link:
    def __init__(self):
        self.imdb_base = 'http://www.imdb.com'
        self.imdb_akas = 'http://akas.imdb.com'
        self.imdb_login = 'https://secure.imdb.com/oauth/m_login?origpath=/&ref_=m_nv_usr_lgin'
        self.imdb_genre = 'http://akas.imdb.com/genre/'
        self.imdb_genres = 'http://akas.imdb.com/search/title?title_type=feature,tv_movie&sort=boxoffice_gross_us&count=25&start=1&genres=%s'
        self.imdb_years = 'http://akas.imdb.com/search/title?title_type=feature,tv_movie&sort=boxoffice_gross_us&count=25&start=1&&year=%s,%s'
        self.imdb_popular = 'http://akas.imdb.com/search/title?title_type=feature,tv_movie&sort=moviemeter,asc&count=25&start=1'
        self.imdb_boxoffice = 'http://akas.imdb.com/search/title?title_type=feature,tv_movie&sort=boxoffice_gross_us,desc&count=25&start=1'
        self.imdb_views = 'http://akas.imdb.com/search/title?title_type=feature,tv_movie&sort=num_votes,desc&count=25&start=1'
        self.imdb_oscars = 'http://akas.imdb.com/search/title?title_type=feature,tv_movie&groups=oscar_best_picture_winners&sort=year,desc&count=25&start=1'
        self.imdb_search = 'http://akas.imdb.com/search/title?title_type=feature,tv_movie&sort=moviemeter,asc&count=25&start=1&title=%s'

        self.myimdb_listorian = 'http://akas.imdb.com/list/watchlist?title_type=feature,tv_movie&sort=listorian:asc&view=detail&count=100&start=1'
        self.myimdb_added = 'http://akas.imdb.com/list/watchlist?title_type=feature,tv_movie&sort=created:desc&view=detail&count=100&start=1'
        self.myimdb_title = 'http://akas.imdb.com/list/watchlist?title_type=feature,tv_movie&sort=title:asc&view=detail&count=100&start=1'
        self.myimdb_lists = 'http://akas.imdb.com/user/%s/lists?tab=all&sort=modified:desc&filter=titles'
        self.myimdb_list = 'http://akas.imdb.com%s?title_type=feature,tv_movie&sort=listorian:asc&view=detail&count=100&start=1'

class genres:
    def __init__(self):
        self.list = []

    def imdb(self):
        #self.list = self.imdb_list()
        self.list = cache3(self.imdb_list)
        index().pageList(self.list)

    def imdb_list(self):
        try:
            result = getUrl(link().imdb_genre).result
            result = common.parseDOM(result, "table", attrs = { "class": "genre-table" })[0]
            genres = common.parseDOM(result, "h3")
        except:
            return
        for genre in genres:
            try:
                name = common.parseDOM(genre, "a")[0]
                name = name.split('<', 1)[0].rsplit('>', 1)[0].strip()
                name = common.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = common.parseDOM(genre, "a", ret="href")[0]
                url = re.compile('/genre/(.+?)/').findall(url)[0]
                url = link().imdb_genres % url
                url = common.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                image = addonGenres.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'image': image})
            except:
                pass

        return self.list

class years:
    def __init__(self):
        self.list = []

    def imdb(self):
        self.list = self.imdb_list()
        index().pageList(self.list)

    def imdb_list(self):
        year = (datetime.datetime.utcnow() - datetime.timedelta(hours = 5)).strftime("%Y")

        for i in range(int(year)-1, int(year)-51, -1):
            name = str(i).encode('utf-8')
            url = link().imdb_years % (str(i), str(i))
            url = url.encode('utf-8')
            image = addonYears.encode('utf-8')
            self.list.append({'name': name, 'url': url, 'image': image})

        return self.list

class movies:
    def __init__(self):
        self.list = []

    def imdb(self, url):
        #self.list = self.imdb_list(url)
        self.list = cache(self.imdb_list, url)
        index().movieList(self.list)
        index().nextList(self.list)

    def imdb_popular(self):
        #self.list = self.imdb_list(link().imdb_popular)
        self.list = cache(self.imdb_list, link().imdb_popular)
        index().movieList(self.list)
        index().nextList(self.list)

    def imdb_boxoffice(self):
        #self.list = self.imdb_list(link().imdb_boxoffice)
        self.list = cache(self.imdb_list, link().imdb_boxoffice)
        index().movieList(self.list)
        index().nextList(self.list)

    def imdb_views(self):
        #self.list = self.imdb_list(link().imdb_views)
        self.list = cache(self.imdb_list, link().imdb_views)
        index().movieList(self.list)
        index().nextList(self.list)

    def imdb_oscars(self):
        #self.list = self.imdb_list(link().imdb_oscars)
        self.list = cache(self.imdb_list, link().imdb_oscars)
        index().movieList(self.list)
        index().nextList(self.list)

    def imdb_search(self, query=None):
        if query is None:
            self.query = common.getUserInput(language(30362).encode("utf-8"), '')
        else:
            self.query = query
        if not (self.query is None or self.query == ''):
            self.query = link().imdb_search % urllib.quote_plus(self.query)
            self.list = self.imdb_list(self.query)
            if getSetting("filter_search") == 'true': self.list = self.imdb_filter()
            index().movieList(self.list)

    def imdb_list(self, url):
        try:
            result = getUrl(url.replace(link().imdb_base, link().imdb_akas)).result
            result = result.decode('iso-8859-1').encode('utf-8')
            movies = common.parseDOM(result, "tr", attrs = { "class": ".+?" })
        except:
            return

        try:
            next = common.parseDOM(result, "span", attrs = { "class": "pagination" })[0]
            name = common.parseDOM(next, "a")[-1]
            if 'laquo' in name: raise Exception()
            next = common.parseDOM(next, "a", ret="href")[-1]
            next = '%s%s' % (link().imdb_akas, next)
            next = common.replaceHTMLCodes(next)
            next = next.encode('utf-8')
        except:
            next = ''

        for movie in movies:
            try:
                title = common.parseDOM(movie, "a")[1]
                title = common.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = common.parseDOM(movie, "span", attrs = { "class": "year_type" })[0]
                year = re.sub("[^0-9]", "", year)[:4]
                year = year.encode('utf-8')

                name = '%s (%s)' % (title, year)
                name = common.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = common.parseDOM(movie, "a", ret="href")[0]
                url = '%s%s' % (link().imdb_base, url)
                url = common.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                image = common.parseDOM(movie, "img", ret="src")[0]
                if not ('._SX' in image or '._SY' in image): raise Exception()
                image = image.rsplit('._SX', 1)[0].rsplit('._SY', 1)[0] + '._SX1000.' + image.rsplit('.', 1)[-1]
                image = common.replaceHTMLCodes(image)
                image = image.encode('utf-8')

                imdb = re.sub("[^0-9]", "", url.rsplit('tt', 1)[-1])
                imdb = imdb.encode('utf-8')

                try:
                    genre = common.parseDOM(movie, "span", attrs = { "class": "genre" })
                    genre = common.parseDOM(genre, "a")
                    genre = str(genre).replace("[u'", '').replace("']", '').replace("', u'", ' / ')
                    genre = common.replaceHTMLCodes(genre)
                    genre = genre.encode('utf-8')
                except:
                    genre = ''

                try:
                    plot = common.parseDOM(movie, "span", attrs = { "class": "outline" })[0]
                    plot = common.replaceHTMLCodes(plot)
                    plot = plot.encode('utf-8')
                except:
                    plot = ''

                self.list.append({'name': name, 'url': url, 'image': image, 'title': title, 'year': year, 'imdb': imdb, 'genre': genre, 'plot': plot, 'next': next})
            except:
                pass

        return self.list

    def imdb_filter(self):
        filter = []
        for i in self.list:
            sources = resolver().sources_get(i['name'], i['title'], i['imdb'], i['year'], resolver().hostDict)
            if not sources == []: filter.append(i['url'])
        self.list = [i for i in self.list if any(x == i['url'] for x in filter)]

        return self.list

class mymovies:
    def __init__(self):
        self.list = []

    def account(self):
        mail, password = getSetting("imdb_mail"), getSetting("imdb_password")
        #self.list = self.imdb_account(mail, password)
        self.list = cache(self.imdb_account, mail, password)
        index().pageList(self.list)

    def imdb(self, url):
        mail, password = getSetting("imdb_mail"), getSetting("imdb_password")
        #self.list = self.imdb_list(mail, password, url)
        self.list = cache(self.imdb_list, mail, password, url)
        index().movieList(self.list)
        index().nextList(self.list)

    def imdb_account(self, mail, password):
        try:
            post = 'login=%s&password=%s' % (urllib.quote_plus(mail), urllib.quote_plus(password))

            result = getUrl(link().imdb_login, post=post, close=False, cookie=True).result
            result = getUrl(link().imdb_akas, close=False).result
            result = result.decode('iso-8859-1').encode('utf-8')
            url = re.compile('/user/(ur.+?)/').findall(result)[0]
            url = link().myimdb_lists % url

            result = getUrl(url).result
            result = result.decode('iso-8859-1').encode('utf-8')
            lists = common.parseDOM(result, "table", attrs = { "class": "lists" })[0]
            lists = common.parseDOM(lists, "tr", attrs = { "id": ".+?" })
        except:
            return

        self.list.append({'name': 'Watch-List', 'url': link().myimdb_listorian, 'image': addonAccount1.encode('utf-8')})
        self.list.append({'name': 'Watch-Added', 'url': link().myimdb_added, 'image': addonAccount2.encode('utf-8')})
        self.list.append({'name': 'Watch-Title', 'url': link().myimdb_title, 'image': addonAccount3.encode('utf-8')})

        for list in lists:
            try:
                name = common.parseDOM(list, "a", ret="title")[0]
                name = common.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = common.parseDOM(list, "a", ret="href")[0]
                url = link().myimdb_list % url
                url = common.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                image = addonAccount4.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'image': image})
            except:
                pass

        return self.list

    def imdb_list(self, mail, password, url):
        try:
            post = 'login=%s&password=%s' % (urllib.quote_plus(mail), urllib.quote_plus(password))

            result = getUrl(link().imdb_login, post=post, close=False, cookie=True).result
            result = getUrl(url.replace(link().imdb_base, link().imdb_akas)).result
            result = result.decode('iso-8859-1').encode('utf-8')
            movies = common.parseDOM(result, "div", attrs = { "class": "list_item.+?" })
        except:
            return

        try:
            next = common.parseDOM(result, "div", attrs = { "class": "pagination" })[0]
            base = common.parseDOM(result, "link", ret="href", attrs = { "rel": "canonical" })[0]
            name = common.parseDOM(next, "a")[-1]
            if 'laquo' in name: raise Exception()
            next = common.parseDOM(next, "a", ret="href")[-1]
            next = '%s%s' % (base, next)
            next = common.replaceHTMLCodes(next)
            next = next.encode('utf-8')
        except:
            next = ''

        for movie in movies:
            try:
                title = common.parseDOM(movie, "a")[1]
                title = common.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                year = common.parseDOM(movie, "span", attrs = { "class": "year_type" })[0]
                year = re.sub("[^0-9]", "", year)[:4]
                year = year.encode('utf-8')

                name = '%s (%s)' % (title, year)
                name = common.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = common.parseDOM(movie, "a", ret="href")[0]
                url = '%s%s' % (link().imdb_base, url)
                url = common.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                try: image = common.parseDOM(movie, "img", ret="loadlate")[0]
                except: image = common.parseDOM(movie, "img", ret="src")[0]
                if not ('._SX' in image or '._SY' in image): raise Exception()
                image = image.rsplit('._SX', 1)[0].rsplit('._SY', 1)[0] + '._SX1000.' + image.rsplit('.', 1)[-1]
                image = common.replaceHTMLCodes(image)
                image = image.encode('utf-8')

                imdb = re.sub("[^0-9]", "", url.rsplit('tt', 1)[-1])
                imdb = imdb.encode('utf-8')

                try:
                    plot = common.parseDOM(movie, "div", attrs = { "class": "item_description" })[0]
                    plot = plot.rsplit('<', 1)[0].rsplit('<', 1)[0].strip()
                    plot = common.replaceHTMLCodes(plot)
                    plot = plot.encode('utf-8')
                except:
                    plot = ''

                self.list.append({'name': name, 'url': url, 'image': image, 'title': title, 'year': year, 'imdb': imdb, 'genre': '', 'plot': plot, 'next': next})
            except:
                pass

        return self.list

class trailer:
    def __init__(self):
        self.youtube_base = 'http://www.youtube.com'
        self.youtube_query = 'http://gdata.youtube.com/feeds/api/videos?q='
        self.youtube_watch = 'http://www.youtube.com/watch?v=%s'
        self.youtube_info = 'http://gdata.youtube.com/feeds/api/videos/%s?v=2'

    def run(self, name, url):
        try:
            if url.startswith(self.youtube_base):
                url = self.youtube(url)
                if url is None: raise Exception()
                return url
            elif not url.startswith('http://'):
                url = self.youtube_watch % url
                url = self.youtube(url)
                if url is None: raise Exception()
                return url
            else:
                raise Exception()
        except:
            url = self.youtube_query + name + ' trailer'
            url = self.youtube_search(url)
            if url is None: return
            return url

    def youtube_search(self, url):
        try:
            if index().addon_status('plugin.video.youtube') is None:
                index().okDialog(language(30321).encode("utf-8"), language(30322).encode("utf-8"))
                return

            query = url.split("?q=")[-1].split("/")[-1].split("?")[0]
            url = url.replace(query, urllib.quote_plus(query))
            result = getUrl(url).result
            result = common.parseDOM(result, "entry")
            result = common.parseDOM(result, "id")

            for url in result[:5]:
                url = url.split("/")[-1]
                url = self.youtube_watch % url
                url = self.youtube(url)
                if not url is None: return url
        except:
            return

    def youtube(self, url):
        try:
            if index().addon_status('plugin.video.youtube') is None:
                index().okDialog(language(30321).encode("utf-8"), language(30322).encode("utf-8"))
                return
            id = url.split("?v=")[-1].split("/")[-1].split("?")[0].split("&")[0]
            state, reason = None, None
            result = getUrl(self.youtube_info % id).result
            try:
                state = common.parseDOM(result, "yt:state", ret="name")[0]
                reason = common.parseDOM(result, "yt:state", ret="reasonCode")[0]
            except:
                pass
            if state == 'deleted' or state == 'rejected' or state == 'failed' or reason == 'requesterRegion' : return
            try:
                result = getUrl(self.youtube_watch % id).result
                alert = common.parseDOM(result, "div", attrs = { "id": "watch7-notification-area" })[0]
                return
            except:
                pass
            url = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s' % id
            return url
        except:
            return

class resolver:
    def __init__(self):
        self.sources_dict()
        self.sources = []

    def run(self, name, title, imdb, year, url):
        try:
            if player().status() is True: return

            self.sources = self.sources_get(name, title, imdb, year, self.hostDict)
            self.sources = self.sources_filter()
            if self.sources == []: raise Exception()

            autoplay = getSetting("autoplay")
            if not xbmc.getInfoLabel('Container.FolderPath').startswith(sys.argv[0]):
                autoplay = getSetting("autoplay_library")

            if url == 'play://':
                url = self.sources_direct()
            elif url == 'sources://' or url == 'download://' or not autoplay == 'true':
                url = self.sources_dialog()
            else:
                url = self.sources_direct()


            if url is None: raise Exception()
            if url == 'download://': return url
            if url == 'close://': return

            player().run(name, url, imdb)
            return url
        except:
            index().infoDialog(language(30318).encode("utf-8"))
            return

    def sources_get(self, name, title, imdb, year, hostDict):
        threads = []

        global movie25_sources
        movie25_sources = []
        threads.append(Thread(movie25().get, name, title, imdb, year, hostDict))

        global simplymovies_sources
        simplymovies_sources = []
        if getSetting("simplymovies") == 'true':
            threads.append(Thread(simplymovies().get, name, title, imdb, year, hostDict))

        global istreamhd_sources
        istreamhd_sources = []
        if getSetting("istreamhd") == 'true':
            threads.append(Thread(istreamhd().get, name, title, imdb, year, hostDict))

        global muchmovies_sources
        muchmovies_sources = []
        if getSetting("muchmovies") == 'true':
            threads.append(Thread(muchmovies().get, name, title, imdb, year, hostDict))

        global yify_sources
        yify_sources = []
        if getSetting("yify") == 'true':
            threads.append(Thread(yify().get, name, title, imdb, year, hostDict))

        global moviestorm_sources
        moviestorm_sources = []
        if getSetting("moviestorm") == 'true':
            threads.append(Thread(moviestorm().get, name, title, imdb, year, hostDict))

        [i.start() for i in threads]
        [i.join() for i in threads]

        self.sources = movie25_sources + simplymovies_sources + istreamhd_sources + muchmovies_sources + yify_sources + moviestorm_sources

        return self.sources

    def sources_resolve(self, url, provider):
        try:
            if provider == 'Movie25': url = movie25().resolve(url)
            elif provider == 'Simplymovies': url = simplymovies().resolve(url)
            elif provider == 'iStreamHD': url = istreamhd().resolve(url)
            elif provider == 'Muchmovies': url = muchmovies().resolve(url)
            elif provider == 'YIFY': url = yify().resolve(url)
            elif provider == 'Moviestorm': url = moviestorm().resolve(url)
            return url
        except:
            return

    def sources_filter(self):
        filter = []
        #host_rank = ['VKHD', 'Muchmovies', 'YIFY', 'iShared', 'VK', 'Flashx', 'Played', 'Divxstage', 'Movreel', 'Putlocker', 'Sockshare', 'Vidx', 'Streamcloud']
        host_rank = [getSetting("hosthd1"), getSetting("hosthd2"), getSetting("hosthd3"), getSetting("host1"), getSetting("host2"), getSetting("host3"), getSetting("host4"), getSetting("host5"), getSetting("host6"), getSetting("host7"), getSetting("host8"), getSetting("host9"), getSetting("host10")]
        host_rank = uniqueList(host_rank + sorted(self.hostDict.keys())).list
        for host in host_rank: filter += [i for i in self.sources if i['source'] == host]
        self.sources = filter

        filter = []
        filter += [i for i in self.sources if i['quality'] == 'HD']
        filter += [i for i in self.sources if i['quality'] == 'SD']
        filter += [i for i in self.sources if i['quality'] == 'SCR']
        filter += [i for i in self.sources if i['quality'] == 'CAM']
        self.sources = filter

        if not getSetting("quality") == 'true':
            self.sources = [i for i in self.sources if not i['quality'] == 'HD']
        if not getSetting("hosthd1") == 'VKHD':
            self.sources = [i for i in self.sources if not i['source'] == 'VKHD']
        if not getSetting("hosthd2") == 'Muchmovies':
            self.sources = [i for i in self.sources if not i['source'] == 'Muchmovies']
        if not getSetting("hosthd3") == 'YIFY':
            self.sources = [i for i in self.sources if not i['source'] == 'YIFY']

        count = 1
        for i in range(len(self.sources)):
            self.sources[i]['source'] = '#'+ str(count) + ' | ' + self.sources[i]['provider'].upper() + ' | ' + self.sources[i]['source'].upper() + ' | ' + self.sources[i]['quality']
            count = count + 1

        return self.sources

    def sources_dialog(self):
        try:
            sourceList, urlList, providerList = [], [], []

            for i in self.sources:
                sourceList.append(i['source'])
                urlList.append(i['url'])
                providerList.append(i['provider'])

            select = index().selectDialog(sourceList)
            if select == -1: return 'close://'
            if not select > -1: return

            url = self.sources_resolve(urlList[select], providerList[select])
            return url
        except:
            return

    def sources_direct(self):
        for i in self.sources:
            try:
                url = self.sources_resolve(i['url'], i['provider'])
                xbmc.sleep(1000)
                if url is None: raise Exception()
                return url
            except:
                pass

    def sources_dict(self):
        self.hostDict = {
        '2gb-hosting' : '2gb-hosting.com',
        'Allmyvideos' : 'allmyvideos.net',
        #'180upload' : '180upload.com',
        'Bayfiles' : 'bayfiles.com',
        #'BillionUploads' : 'billionuploads.com',
        'Castamp' : 'castamp.com',
        #'Clicktoview' : 'clicktoview.org',
        'Daclips' : 'daclips.com',
        'Divxstage' : 'divxstage.eu',
        'Donevideo' : 'donevideo.com',
        'Ecostream' : 'ecostream.tv',
        'Filenuke' : 'filenuke.com',
        'Flashx' : 'flashx.tv',
        'Gorillavid' : 'gorillavid.com',
        'Hostingbulk' : 'hostingbulk.com',
        #'Hugefiles' : 'hugefiles.net',
        'iShared' : 'ishared.eu',
        'Jumbofiles' : 'jumbofiles.com',
        'Lemuploads' : 'lemuploads.com',
        'Limevideo' : 'limevideo.net',
        #'Megarelease' : 'megarelease.org',
        'Mightyupload' : 'mightyupload.com',
        'Movdivx' : 'movdivx.com',
        'Movpod' : 'movpod.net',
        'Movreel' : 'movreel.com',
        'Movshare' : 'movshare.net',
        'Movzap' : 'movzap.com',
        'Muchmovies' : 'muchmovies.org',
        'Muchshare' : 'muchshare.net',
        'Nosvideo' : 'nosvideo.com',
        'Novamov' : 'novamov.com',
        'Nowvideo' : 'nowvideo.co',
        'Played' : 'played.to',
        'Playwire' : 'playwire.com',
        'Primeshare' : 'primeshare.tv',
        'Promptfile' : 'promptfile.com',
        'Purevid' : 'purevid.com',
        'Putlocker' : 'putlocker.com',
        'Sharerepo' : 'sharerepo.com',
        'Sharesix' : 'sharesix.com',
        'Sockshare' : 'sockshare.com',
        'StageVu' : 'stagevu.com',
        'Streamcloud' : 'streamcloud.eu',
        'Thefile' : 'thefile.me',
        'TVonline' : 'tvonline.cc',
        'Uploadc' : 'uploadc.com',
        'Vidbull' : 'vidbull.com',
        'Videobb' : 'videobb.com',
        'Videoweed' : 'videoweed.es',
        'Videozed' : 'videozed.net',
        #'Vidhog' : 'vidhog.com',
        #'Vidplay' : 'vidplay.net',
        'Vidx' : 'vidx.to',
        #'Vidxden' : 'vidxden.com',
        'VK' : '.vk.me',
        'VKHD' : '.vk.me',
        'WatchfreeinHD' : 'watchfreeinhd.com',
        'Xvidstage' : 'xvidstage.com',
        'YIFY' : 'yify.tv',
        'Youwatch' : 'youwatch.org',
        'Zalaa' : 'zalaa.com'
        }


class movie25:
    def __init__(self):
        self.movie25_base = 'http://www.movie25.so'
        self.movie25_search = 'http://www.movie25.so/search.php?key=%s'

    def get(self, name, title, imdb, year, hostDict):
        try:
            global movie25_sources
            movie25_sources = []

            url = None
            query = self.movie25_search % urllib.quote_plus(title)

            result = getUrl(query).result
            result = result.decode('iso-8859-1').encode('utf-8')
            result = common.parseDOM(result, "div", attrs = { "class": "movie_table" })[0]
            result = common.parseDOM(result, "li")

            match = [i for i in result if any(x in i for x in [' (%s)' % str(year), ' (%s)' % str(int(year)+1), ' (%s)' % str(int(year)-1)])]
            match2 = [self.movie25_base + common.parseDOM(i, "a", ret="href")[0] for i in match]
            if match2 == []: return
            for i in match2[:5]:
                try:
                    result = getUrl(i).result
                    result = result.decode('iso-8859-1').encode('utf-8')
                    if str('tt' + imdb) in result:
                        url = i
                        break
                except:
                    pass
            if url == None: return
            url = common.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            result = getUrl(url).result
            result = result.decode('iso-8859-1').encode('utf-8')
            result = common.parseDOM(result, "div", attrs = { "class": "links_quality" })[0]

            quality = common.parseDOM(result, "h1")[0]
            quality = quality.replace('\n','').rsplit(' ', 1)[-1]
            if quality == 'CAM' or quality == 'TS': quality = 'CAM'
            elif quality == 'SCREENER': quality = 'SCR'
            else: quality = 'SD'

            links = common.parseDOM(result, "ul")
            for i in links:
                try:
                    name = common.parseDOM(i, "a")[0]
                    name = common.replaceHTMLCodes(name)
                    if name.isdigit(): raise Exception()
                    host = common.parseDOM(i, "li", attrs = { "class": "link_name" })[0]
                    host = common.replaceHTMLCodes(host)
                    host = host.encode('utf-8')
                    host = [x for x in hostDict.keys() if host.lower() == x.lower()][0]
                    url = common.parseDOM(i, "a", ret="href")[0]
                    url = '%s%s' % (self.movie25_base, url)
                    url = common.replaceHTMLCodes(url)
                    url = url.encode('utf-8')
                    movie25_sources.append({'source': host, 'quality': quality, 'provider': 'Movie25', 'url': url})
                except:
                    pass

            movie25_sources = sorted(movie25_sources, key=itemgetter('source'))
        except:
            return

    def resolve(self, url):
        try:
            result = getUrl(url).result
            result = result.decode('iso-8859-1').encode('utf-8')
            url = common.parseDOM(result, "input", ret="onclick")
            url = [i for i in url if 'location.href' in i and 'http://' in i][0]
            url = url.split("'", 1)[-1].rsplit("'", 1)[0]

            if url.startswith('http://ishared.eu'):
                result = getUrl(url).result
                url = re.compile('var xxxx = "(.+?)"').findall(result)[0]
                return url

            host = urlresolver.HostedMediaFile(url)
            if host: resolver = urlresolver.resolve(url)
            if not resolver.startswith('http://'): return
            if not resolver == url: return resolver
        except:
            return

class simplymovies:
    def __init__(self):
        self.simplymovies_base = 'http://simplymovies.net'
        self.simplymovies_search = 'http://simplymovies.net/index.php?searchTerm='

    def get(self, name, title, imdb, year, hostDict):
        try:
            global simplymovies_sources
            simplymovies_sources = []

            query = self.simplymovies_search + urllib.quote_plus(title.replace(' ', '-'))

            result = getUrl(query).result
            url = common.parseDOM(result, "div", attrs = { "class": "movieInfoHolder" })
            try: match = [i for i in url if str('>' + re.sub('\n|\s\s','',re.sub('\n|\s(:|-)\s|(:|-)\s|\s(:|-)|(:|-)|([[].+?[]])',' ',title).lower()) + '<') in re.sub('\n|\s\s','',re.sub('\n|\s(:|-)\s|(:|-)\s|\s(:|-)|(:|-)|([[].+?[]])',' ',i).lower()) and any(x in i for x in [', %s<' % str(year), ', %s<' % str(int(year)+1), ', %s<' % str(int(year)-1)])][0]
            except: pass
            try: match = [i for i in url if str('tt' + imdb) in i][0]
            except: pass
            url = common.parseDOM(match, "a", ret="href")[0]
            url = '%s/%s' % (self.simplymovies_base, url)
            url = common.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            result = getUrl(url).result
            url = common.parseDOM(result, "iframe", ret="src", attrs = { "class": "videoPlayerIframe" })[0]
            url = common.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            result = getUrl(url).result
            try:
                url = re.compile('url720=(.+?)&').findall(result)[0]
                simplymovies_sources.append({'source': 'VKHD', 'quality': 'HD', 'provider': 'Simplymovies', 'url': url})
            except:
                pass
            try:
                url = re.compile('url540=(.+?)&').findall(result)[0]
                simplymovies_sources.append({'source': 'VK', 'quality': 'SD', 'provider': 'Simplymovies', 'url': url})
            except:
                pass
            try:
                url = re.compile('url480=(.+?)&').findall(result)[0]
                simplymovies_sources.append({'source': 'VK', 'quality': 'SD', 'provider': 'Simplymovies', 'url': url})
            except:
                pass
        except:
            return

    def resolve(self, url):
        return url

class istreamhd:
    def __init__(self):
        self.istreamhd_base = 'http://istreamhd.org'
        self.istreamhd_get = 'http://istreamhd.org/get'
        self.istreamhd_search = 'http://istreamhd.org/get/mini_search.php?&count=10&q=%s'
        self.istreamhd_watch = 'http://istreamhd.org/lib/get_embed.php?%s'

    def get(self, name, title, imdb, year, hostDict):
        try:
            global istreamhd_sources
            istreamhd_sources = []

            query = self.istreamhd_search % (urllib.quote_plus(title))

            result = getUrl(query).result
            url = common.parseDOM(result, "div", attrs = { "class": "ui-block.+?" })
            url = [i for i in url if str('tt' + imdb) in i][0]
            url = common.parseDOM(url, "a", ret="href")[0]
            url = '%s%s' % (self.istreamhd_base, url)
            url = common.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            result = getUrl(url).result
            url = re.compile('/lib/get_embed.php.+?"(.+?)"').findall(result)[0]
            url = self.istreamhd_watch % url
            url = common.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            result = getUrl(url).result
            url = common.parseDOM(result, "iframe", ret="src")[0]
            url = common.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            result = getUrl(url).result
            try:
                url = re.compile('url720=(.+?)&').findall(result)[0]
                istreamhd_sources.append({'source': 'VKHD', 'quality': 'HD', 'provider': 'iStreamHD', 'url': url})
            except:
                pass
            try:
                url = re.compile('url540=(.+?)&').findall(result)[0]
                istreamhd_sources.append({'source': 'VK', 'quality': 'SD', 'provider': 'iStreamHD', 'url': url})
            except:
                pass
            try:
                url = re.compile('url480=(.+?)&').findall(result)[0]
                istreamhd_sources.append({'source': 'VK', 'quality': 'SD', 'provider': 'iStreamHD', 'url': url})
            except:
                pass
        except:
            return

    def resolve(self, url):
        return url

class muchmovies:
    def __init__(self):
        self.muchmovies_base = 'http://www.muchmovies.org'
        self.muchmovies_search = 'http://www.muchmovies.org/search'

    def get(self, name, title, imdb, year, hostDict):
        try:
            global muchmovies_sources
            muchmovies_sources = []

            query = self.muchmovies_search + '/' + urllib.quote_plus(title.replace(' ', '-'))

            result = getUrl(query, mobile=True).result
            url = common.parseDOM(result, "li", attrs = { "data-icon": "false" })
            url = [i for i in url if str('>' + re.sub('\n|\s\s','',re.sub('\n|\s(:|-)\s|(:|-)\s|\s(:|-)|(:|-)|([[].+?[]])',' ',title).lower()) + ' (') in re.sub('\n|\s\s','',re.sub('\n|\s(:|-)\s|(:|-)\s|\s(:|-)|(:|-)|([[].+?[]])',' ',i).lower()) and any(x in i for x in [' (%s)' % str(year), ' (%s)' % str(int(year)+1), ' (%s)' % str(int(year)-1)])][0]
            url = common.parseDOM(url, "a", ret="href")[0]
            url = '%s%s' % (self.muchmovies_base, url)
            url = common.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            muchmovies_sources.append({'source': 'Muchmovies', 'quality': 'HD', 'provider': 'Muchmovies', 'url': url})
        except:
            return

    def resolve(self, url):
        try:
            result = getUrl(url, mobile=True).result
            url = common.parseDOM(result, "a", ret="href")
            url = [i for i in url if "?action=stream" in i][0]
            url = url.split("?")[0]

            start = time.clock()
            request = urllib2.Request(url)
            request.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0')
            response = urllib2.urlopen(request, timeout=10)
            for i in range(0, 26):
                chunk = response.read(16 * 1024)
                end = time.clock() - start
                if end > 3: break
            response.close()
            if end > 3: return

            return url
        except:
            return

class yify:
    def __init__(self):
        self.yify_base = 'http://yify.tv'
        self.yify_ajax = 'http://yify.tv/wp-admin/admin-ajax.php'
        self.yify_post = 'action=ajaxy_sf&sf_value=%s'
        self.yify_watch = 'http://yify.tv/reproductor2/pk/pk/plugins/player_picasa.php?url=https%3A//picasaweb.google.com/'

    def get(self, name, title, imdb, year, hostDict):
        try:
            global yify_sources
            yify_sources = []

            query = self.yify_post % (urllib.quote_plus(title))

            result = getUrl(self.yify_ajax, post=query).result
            result = result.replace('&#8211;','-')
            url = json.loads(result)
            url = url['post']['all']
            url = [i['post_link'] for i in url if re.sub('\n|\s\s','',re.sub('\n|\s(:|-)\s|(:|-)\s|\s(:|-)|(:|-)|([[].+?[]])',' ',title).lower()) == re.sub('\n|\s\s','',re.sub('\n|\s(:|-)\s|(:|-)\s|\s(:|-)|(:|-)|([[].+?[]])',' ',i['post_title']).lower())][0]
            url = common.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            result = getUrl(url).result
            if not str('tt' + imdb) in result: raise Exception()

            yify_sources.append({'source': 'YIFY', 'quality': 'HD', 'provider': 'YIFY', 'url': url})
        except:
            return

    def resolve(self, url):
        try:
            result = getUrl(url).result
            url = re.compile('showPkPlayer[(]"(.+?)"[)]').findall(result)[0]
            url = self.yify_watch + url
            result = getUrl(url).result
            result = re.compile('{(.+?)}').findall(result)[-1]
            url = re.compile('"url":"(.+?)"').findall(result)[0]
            return url
        except:
            return

class moviestorm:
    def __init__(self):
        self.moviestorm_base = 'http://moviestorm.eu'
        self.moviestorm_search = 'http://moviestorm.eu/search?q=%s'

    def get(self, name, title, imdb, year, hostDict):
        try:
            global moviestorm_sources
            moviestorm_sources = []

            query = self.moviestorm_search % (urllib.quote_plus(title))

            result = getUrl(query).result
            url = common.parseDOM(result, "div", attrs = { "class": "movie_box" })
            url = [i for i in url if str('tt' + imdb) in i][0]
            url = common.parseDOM(url, "a", ret="href")[0]
            url = common.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            result = getUrl(url).result
            result = common.parseDOM(result, "div", attrs = { "class": "links" })[0]
            links = common.parseDOM(result, "tr")

            sd_links = [re.compile('"(http://ishared.eu/.+?)"').findall(i)[0] for i in links if not any(x in common.parseDOM(i, "td", attrs = { "class": "quality_td" })[0] for x in ['CAM', 'TS'])]
            ts_links = [re.compile('"(http://ishared.eu/.+?)"').findall(i)[0] for i in links if any(x in common.parseDOM(i, "td", attrs = { "class": "quality_td" })[0] for x in ['CAM', 'TS'])]

            if (len(sd_links) == 1):
                moviestorm_sources.append({'source': 'iShared', 'quality': 'SD', 'provider': 'Moviestorm', 'url': sd_links[0]})
            if (len(ts_links) == 1):
                moviestorm_sources.append({'source': 'iShared', 'quality': 'CAM', 'provider': 'Moviestorm', 'url': ts_links[0]})
        except:
            return

    def resolve(self, url):
        try:
            result = getUrl(url).result
            url = re.compile('var xxxx = "(.+?)"').findall(result)[0]
            return url
        except:
            return


main()