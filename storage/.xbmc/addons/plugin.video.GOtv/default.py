# -*- coding: utf-8 -*-

'''
    GOtv XBMC Addon
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

import urllib,urllib2,urlparse,re,os,threading,datetime,time,base64,xbmc,xbmcplugin,xbmcgui,xbmcaddon,xbmcvfs
from operator import itemgetter
import urlresolver
try:    import CommonFunctions
except: import commonfunctionsdummy as CommonFunctions
try:    import StorageServer
except: import storageserverdummy as StorageServer
from metahandler import metahandlers
from metahandler import metacontainers


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
addonNext           = os.path.join(addonPath,'resources/art/Next.png')
dataPath            = xbmc.translatePath('special://profile/addon_data/%s' % (addonId))
viewData            = os.path.join(dataPath,'views.cfg')
favData             = os.path.join(dataPath,'favourites.cfg')
subData             = os.path.join(dataPath,'subscriptions.cfg')
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
        try:        genre = urllib.unquote_plus(params["genre"])
        except:     genre = None
        try:        plot = urllib.unquote_plus(params["plot"])
        except:     plot = None
        try:        show = urllib.unquote_plus(params["show"])
        except:     show = None
        try:        season = urllib.unquote_plus(params["season"])
        except:     season = None
        try:        episode = urllib.unquote_plus(params["episode"])
        except:     episode = None

        if action == None:                          root().get()
        elif action == 'item_play':                 contextMenu().item_play()
        elif action == 'item_random_play':          contextMenu().item_random_play()
        elif action == 'item_queue':                contextMenu().item_queue()
        elif action == 'item_play_from_here':       contextMenu().item_play_from_here(url)
        elif action == 'favourite_add':             contextMenu().favourite_add(favData, name, url, image, imdb, year)
        elif action == 'favourite_from_search':     contextMenu().favourite_from_search(favData, name, url, image, imdb, year)
        elif action == 'favourite_delete':          contextMenu().favourite_delete(favData, name, url)
        elif action == 'favourite_moveUp':          contextMenu().favourite_moveUp(favData, name, url)
        elif action == 'favourite_moveDown':        contextMenu().favourite_moveDown(favData, name, url)
        elif action == 'subscription_add':          contextMenu().subscription_add(name, url, image, imdb, year)
        elif action == 'subscription_from_search':  contextMenu().subscription_from_search(name, url, image, imdb, year)
        elif action == 'subscription_delete':       contextMenu().subscription_delete(name, url)
        elif action == 'subscriptions_update':      contextMenu().subscriptions_update()
        elif action == 'subscriptions_service':     contextMenu().subscriptions_update(silent=True)
        elif action == 'subscriptions_clean':       contextMenu().subscriptions_clean()
        elif action == 'playlist_open':             contextMenu().playlist_open()
        elif action == 'settings_open':             contextMenu().settings_open()
        elif action == 'addon_home':                contextMenu().addon_home()
        elif action == 'view_tvshows':              contextMenu().view('tvshows')
        elif action == 'view_seasons':              contextMenu().view('seasons')
        elif action == 'view_episodes':             contextMenu().view('episodes')
        elif action == 'metadata_tvshows':          contextMenu().metadata('tvshow', imdb, '', '')
        elif action == 'metadata_seasons':          contextMenu().metadata('season', imdb, season, '')
        elif action == 'metadata_episodes':         contextMenu().metadata('episode', imdb, season, episode)
        elif action == 'playcount_tvshows':         contextMenu().playcount('tvshow', imdb, '', '')
        elif action == 'playcount_seasons':         contextMenu().playcount('season', imdb, season, '')
        elif action == 'playcount_episodes':        contextMenu().playcount('episode', imdb, season, episode)
        elif action == 'library':                   contextMenu().library(name, url, imdb, year)
        elif action == 'download':                  contextMenu().download(name, title, imdb, year, url)
        elif action == 'sources':                   contextMenu().sources(name, title, imdb, year, url)
        elif action == 'shows_favourites':          favourites().shows()
        elif action == 'shows_subscriptions':       subscriptions().shows()
        elif action == 'episodes_subscriptions':    subscriptions().episodes()
        elif action == 'shows':                     shows().imdb(url)
        elif action == 'shows_popular':             shows().imdb_popular()
        elif action == 'shows_rating':              shows().imdb_rating()
        elif action == 'shows_views':               shows().imdb_views()
        elif action == 'shows_active':              shows().imdb_active()
        elif action == 'shows_search':              shows().imdb_search(query)
        elif action == 'genres_shows':              genres().imdb()
        elif action == 'seasons':                   seasons().get(url, image, year, imdb, genre, plot, show)
        elif action == 'episodes':                  episodes().get(name, url, image, year, imdb, genre, plot, show)
        elif action == 'play':                      resolver().run(name, title, imdb, year, url)

        if action is None:
            pass
        elif action.startswith('shows'):
            xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
            index().container_view('tvshows', {'skin.confluence' : 500})
        elif action.startswith('seasons'):
            xbmcplugin.setContent(int(sys.argv[1]), 'seasons')
            index().container_view('seasons', {'skin.confluence' : 500})
        elif action.startswith('episodes'):
            xbmcplugin.setContent(int(sys.argv[1]), 'episodes')
            index().container_view('episodes', {'skin.confluence' : 504})
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
        response = urllib2.urlopen(request, timeout=30)
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

    def run(self, name, url):
        if xbmc.getInfoLabel('Container.FolderPath').startswith(sys.argv[0]):
            item = xbmcgui.ListItem(path=url)
            xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, item)
        else:
            try: season = re.compile('S(\d{3})E\d*').findall(name)[-1]
            except: season = None
            try: season = re.compile('S(\d{2})E\d*').findall(name)[-1]
            except: season = None
            try: episode = re.compile('S%sE(\d*)' % (season)).findall(name)[-1]
            except: episode = None
            try: year = re.compile('[(](\d{4})[)]').findall(name)[-1]
            except: year = None
            try:
                if not (season is None and episode is None):
                	show = name.replace('S%sE%s' % (season, episode), '').strip()
                	season, episode = '%01d' % int(season), '%01d' % int(episode)
                	imdb = metaget.get_meta('tvshow', show)['imdb_id']
                	imdb = re.sub("[^0-9]", "", imdb)
                	meta = metaget.get_episode_meta('', imdb, season, episode)
                	meta.update({'tvshowtitle': show})
                	poster = meta['cover_url']
                elif not year is None:
                	title = name.replace('(%s)' % year, '').strip()
                	meta = metaget.get_meta('movie', title ,year=year ,overlay=6)
                	poster = meta['cover_url']
                else: raise Exception()
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

        self.season = str(xbmc.getInfoLabel('VideoPlayer.season'))
        self.episode = str(xbmc.getInfoLabel('VideoPlayer.episode'))
        if self.season == '' or self.episode == '':
            self.content = 'movie'
            self.imdb = metaget.get_meta('movie', xbmc.getInfoLabel('VideoPlayer.title') ,year=str(xbmc.getInfoLabel('VideoPlayer.year')))['imdb_id']
            self.imdb = re.sub("[^0-9]", "", self.imdb)
        else:
            self.content = 'episode'
            self.imdb = metaget.get_meta('tvshow', xbmc.getInfoLabel('VideoPlayer.tvshowtitle'))['imdb_id']
            self.imdb = re.sub("[^0-9]", "", self.imdb)

        while True:
            try: self.currentTime = self.getTime()
            except: break
            xbmc.sleep(1000)

    def onPlayBackEnded(self):
        if xbmc.getInfoLabel('Container.FolderPath') == '': index().setProperty(self.property, 'true')
        if not self.currentTime / self.totalTime >= .9: return
        metaget.change_watched(self.content, '', self.imdb, season=self.season, episode=self.episode, year='', watched='')
        index().container_refresh()

    def onPlayBackStopped(self):
        index().clearProperty(self.property)

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
        xbmc.executebuiltin("Notification(%s,%s, 3000, %s)" % (header, str, addonIcon))

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
        if not xbmcvfs.exists(subData):
            file = xbmcvfs.File(subData, 'w')
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

                cm = []
                if action.endswith('_subscriptions'):
                    cm.append((language(30425).encode("utf-8"), 'RunPlugin(%s?action=subscriptions_update)' % (sys.argv[0])))
                    cm.append((language(30426).encode("utf-8"), 'RunPlugin(%s?action=subscriptions_clean)' % (sys.argv[0])))

                item = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=image)
                item.setInfo( type="Video", infoLabels={ "Label": name, "Title": name, "Plot": addonDesc } )
                item.setProperty("Fanart_Image", addonFanart)
                item.addContextMenuItems(cm, replaceItems=False)
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

                u = '%s?action=shows&url=%s' % (sys.argv[0], sysurl)

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

        u = '%s?action=shows&url=%s' % (sys.argv[0], sysurl)

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

    def showList(self, showList):
        if showList == None: return

        file = xbmcvfs.File(favData)
        favRead = file.read()
        file.close()
        file = xbmcvfs.File(subData)
        subRead = file.read()
        file.close()

        total = len(showList)
        for i in showList:
            try:
                name, url, image, year, imdb, genre, plot = i['name'], i['url'], i['image'], i['year'], i['imdb'], i['genre'], i['plot']
                if plot == '': plot = addonDesc
                if genre == '': genre = ' '
                title = name

                sysname, sysurl, sysimage, sysyear, sysimdb, sysgenre, sysplot = urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(image), urllib.quote_plus(year), urllib.quote_plus(imdb), urllib.quote_plus(genre), urllib.quote_plus(plot)
                u = '%s?action=seasons&url=%s&image=%s&year=%s&imdb=%s&genre=%s&plot=%s&show=%s' % (sys.argv[0], sysurl, sysimage, sysyear, sysimdb, sysgenre, sysplot, sysname)

                if getSetting("meta") == 'true':
                    meta = metaget.get_meta('tvshow', title, imdb_id=imdb)
                    playcountMenu = language(30407).encode("utf-8")
                    if meta['overlay'] == 6: playcountMenu = language(30408).encode("utf-8")
                    metaimdb = urllib.quote_plus(re.sub("[^0-9]", "", meta['imdb_id']))
                    poster, banner = meta['cover_url'], meta['banner_url']
                    if banner == '': banner = poster
                    if banner == '': banner = image
                    if poster == '': poster = image
                else:
                    meta = {'label': title, 'title': title, 'tvshowtitle': title, 'year' : year, 'imdb_id' : imdb, 'genre' : genre, 'plot': plot}
                    poster, banner = image, image
                if getSetting("meta") == 'true' and getSetting("fanart") == 'true':
                    fanart = meta['backdrop_url']
                    if fanart == '': fanart = addonFanart
                else:
                    fanart = addonFanart

                meta.update({'art(banner)': banner, 'art(poster)': poster})

                cm = []
                cm.append((language(30401).encode("utf-8"), 'RunPlugin(%s?action=item_play)' % (sys.argv[0])))
                cm.append((language(30413).encode("utf-8"), 'Action(Info)'))
                if action == 'shows_favourites':
                    if getSetting("meta") == 'true': cm.append((language(30415).encode("utf-8"), 'RunPlugin(%s?action=metadata_tvshows&imdb=%s)' % (sys.argv[0], metaimdb)))
                    if getSetting("meta") == 'true': cm.append((playcountMenu, 'RunPlugin(%s?action=playcount_tvshows&imdb=%s)' % (sys.argv[0], metaimdb)))
                    if not '"%s"' % url in subRead: cm.append((language(30423).encode("utf-8"), 'RunPlugin(%s?action=subscription_add&name=%s&imdb=%s&url=%s&image=%s&year=%s)' % (sys.argv[0], sysname, sysimdb, sysurl, sysimage, sysyear)))
                    else: cm.append((language(30424).encode("utf-8"), 'RunPlugin(%s?action=subscription_delete&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                    cm.append((language(30422).encode("utf-8"), 'RunPlugin(%s?action=library&name=%s&url=%s&imdb=%s&year=%s)' % (sys.argv[0], sysname, sysurl, sysimdb, sysyear)))
                    cm.append((language(30429).encode("utf-8"), 'RunPlugin(%s?action=view_tvshows)' % (sys.argv[0])))
                    if getSetting("fav_sort") == '2': cm.append((language(30419).encode("utf-8"), 'RunPlugin(%s?action=favourite_moveUp&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                    if getSetting("fav_sort") == '2': cm.append((language(30420).encode("utf-8"), 'RunPlugin(%s?action=favourite_moveDown&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                    cm.append((language(30421).encode("utf-8"), 'RunPlugin(%s?action=favourite_delete&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                elif action == 'shows_subscriptions':
                    if getSetting("meta") == 'true': cm.append((language(30415).encode("utf-8"), 'RunPlugin(%s?action=metadata_tvshows&imdb=%s)' % (sys.argv[0], metaimdb)))
                    if getSetting("meta") == 'true': cm.append((playcountMenu, 'RunPlugin(%s?action=playcount_tvshows&imdb=%s)' % (sys.argv[0], metaimdb)))
                    if not '"%s"' % url in subRead: cm.append((language(30423).encode("utf-8"), 'RunPlugin(%s?action=subscription_add&name=%s&imdb=%s&url=%s&image=%s&year=%s)' % (sys.argv[0], sysname, sysimdb, sysurl, sysimage, sysyear)))
                    else: cm.append((language(30424).encode("utf-8"), 'RunPlugin(%s?action=subscription_delete&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                    cm.append((language(30425).encode("utf-8"), 'RunPlugin(%s?action=subscriptions_update)' % (sys.argv[0])))
                    cm.append((language(30426).encode("utf-8"), 'RunPlugin(%s?action=subscriptions_clean)' % (sys.argv[0])))
                    if not '"%s"' % url in favRead: cm.append((language(30417).encode("utf-8"), 'RunPlugin(%s?action=favourite_add&name=%s&imdb=%s&url=%s&image=%s&year=%s)' % (sys.argv[0], sysname, sysimdb, sysurl, sysimage, sysyear)))
                    else: cm.append((language(30418).encode("utf-8"), 'RunPlugin(%s?action=favourite_delete&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                    cm.append((language(30429).encode("utf-8"), 'RunPlugin(%s?action=view_tvshows)' % (sys.argv[0])))
                    cm.append((language(30409).encode("utf-8"), 'RunPlugin(%s?action=settings_open)' % (sys.argv[0])))
                elif action.startswith('shows_search'):
                    cm.append((language(30423).encode("utf-8"), 'RunPlugin(%s?action=subscription_from_search&name=%s&imdb=%s&url=%s&image=%s&year=%s)' % (sys.argv[0], sysname, sysimdb, sysurl, sysimage, sysyear)))
                    cm.append((language(30422).encode("utf-8"), 'RunPlugin(%s?action=library&name=%s&url=%s&imdb=%s&year=%s)' % (sys.argv[0], sysname, sysurl, sysimdb, sysyear)))
                    cm.append((language(30417).encode("utf-8"), 'RunPlugin(%s?action=favourite_from_search&name=%s&imdb=%s&url=%s&image=%s&year=%s)' % (sys.argv[0], sysname, sysimdb, sysurl, sysimage, sysyear)))
                    cm.append((language(30429).encode("utf-8"), 'RunPlugin(%s?action=view_tvshows)' % (sys.argv[0])))
                    cm.append((language(30409).encode("utf-8"), 'RunPlugin(%s?action=settings_open)' % (sys.argv[0])))
                    cm.append((language(30410).encode("utf-8"), 'RunPlugin(%s?action=playlist_open)' % (sys.argv[0])))
                    cm.append((language(30411).encode("utf-8"), 'RunPlugin(%s?action=addon_home)' % (sys.argv[0])))
                else:
                    if not '"%s"' % url in subRead: cm.append((language(30423).encode("utf-8"), 'RunPlugin(%s?action=subscription_add&name=%s&imdb=%s&url=%s&image=%s&year=%s)' % (sys.argv[0], sysname, sysimdb, sysurl, sysimage, sysyear)))
                    else: cm.append((language(30424).encode("utf-8"), 'RunPlugin(%s?action=subscription_delete&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                    cm.append((language(30422).encode("utf-8"), 'RunPlugin(%s?action=library&name=%s&url=%s&imdb=%s&year=%s)' % (sys.argv[0], sysname, sysurl, sysimdb, sysyear)))
                    if not '"%s"' % url in favRead: cm.append((language(30417).encode("utf-8"), 'RunPlugin(%s?action=favourite_add&name=%s&imdb=%s&url=%s&image=%s&year=%s)' % (sys.argv[0], sysname, sysimdb, sysurl, sysimage, sysyear)))
                    else: cm.append((language(30418).encode("utf-8"), 'RunPlugin(%s?action=favourite_delete&name=%s&url=%s)' % (sys.argv[0], sysname, sysurl)))
                    cm.append((language(30429).encode("utf-8"), 'RunPlugin(%s?action=view_tvshows)' % (sys.argv[0])))
                    cm.append((language(30409).encode("utf-8"), 'RunPlugin(%s?action=settings_open)' % (sys.argv[0])))
                    cm.append((language(30410).encode("utf-8"), 'RunPlugin(%s?action=playlist_open)' % (sys.argv[0])))
                    cm.append((language(30411).encode("utf-8"), 'RunPlugin(%s?action=addon_home)' % (sys.argv[0])))

                if action == 'shows_search':
                    if ('"%s"' % url in favRead and '"%s"' % url in subRead): suffix = '|F|S| '
                    elif '"%s"' % url in favRead: suffix = '|F| '
                    elif '"%s"' % url in subRead: suffix = '|S| '
                    else: suffix = ''
                    name = suffix + name

                item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=poster)
                item.setInfo( type="Video", infoLabels = meta )
                item.setProperty("IsPlayable", "true")
                item.setProperty("Video", "true")
                item.setProperty("Fanart_Image", fanart)
                item.addContextMenuItems(cm, replaceItems=True)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=total,isFolder=True)
            except:
                pass

    def seasonList(self, seasonList):
        if seasonList == None: return

        try:
            year, imdb, genre, plot, show = seasonList[0]['year'], seasonList[0]['imdb'], seasonList[0]['genre'], seasonList[0]['plot'], seasonList[0]['show']

            if plot == '': plot = addonDesc
            if genre == '': genre = ' '

            if getSetting("meta") == 'true':
                seasons = []
                for i in seasonList: seasons.append(i['season'])
                season_meta = metaget.get_seasons(show, imdb, seasons)
                meta = metaget.get_meta('tvshow', show, imdb_id=imdb)
                banner = meta['banner_url']
            else:
                meta = {'tvshowtitle': show, 'imdb_id' : imdb, 'genre' : genre, 'plot': plot}
                banner = ''
            if getSetting("meta") == 'true' and getSetting("fanart") == 'true':
                fanart = meta['backdrop_url']
                if fanart == '': fanart = addonFanart
            else:
                fanart = addonFanart
        except:
            return

        total = len(seasonList)
        for i in range(0, int(total)):
            try:
                name, url, image = seasonList[i]['name'], seasonList[i]['url'], seasonList[i]['image']
                sysname, sysurl, sysimage, sysyear, sysimdb, sysgenre, sysplot, sysshow = urllib.quote_plus(name), urllib.quote_plus(url), urllib.quote_plus(image), urllib.quote_plus(year), urllib.quote_plus(imdb), urllib.quote_plus(genre), urllib.quote_plus(plot), urllib.quote_plus(show)
                u = '%s?action=episodes&name=%s&url=%s&image=%s&year=%s&imdb=%s&genre=%s&plot=%s&show=%s' % (sys.argv[0], sysname, sysurl, sysimage, sysyear, sysimdb, sysgenre, sysplot, sysshow)

                if getSetting("meta") == 'true':
                    meta.update({'playcount': season_meta[i]['playcount'], 'overlay': season_meta[i]['overlay']})
                    poster = season_meta[i]['cover_url']
                    playcountMenu = language(30407).encode("utf-8")
                    if season_meta[i]['overlay'] == 6: playcountMenu = language(30408).encode("utf-8")
                    metaimdb, metaseason = urllib.quote_plus(re.sub("[^0-9]", "", str(season_meta[i]['imdb_id']))), urllib.quote_plus(str(season_meta[i]['season']))
                    if poster == '': poster = image
                    if banner == '': banner = poster
                    if banner == '': banner = image
                else:
                    poster, banner = image, image

                meta.update({'label': name, 'title': name, 'art(season.banner)': banner, 'art(season.poster': poster})

                cm = []
                cm.append((language(30401).encode("utf-8"), 'RunPlugin(%s?action=item_play)' % (sys.argv[0])))
                cm.append((language(30404).encode("utf-8"), 'RunPlugin(%s?action=item_queue)' % (sys.argv[0])))
                cm.append((language(30413).encode("utf-8"), 'Action(Info)'))
                if getSetting("meta") == 'true': cm.append((language(30415).encode("utf-8"), 'RunPlugin(%s?action=metadata_seasons&imdb=%s&season=%s)' % (sys.argv[0], metaimdb, metaseason)))
                if getSetting("meta") == 'true': cm.append((playcountMenu, 'RunPlugin(%s?action=playcount_seasons&imdb=%s&season=%s)' % (sys.argv[0], metaimdb, metaseason)))
                cm.append((language(30430).encode("utf-8"), 'RunPlugin(%s?action=view_seasons)' % (sys.argv[0])))
                cm.append((language(30409).encode("utf-8"), 'RunPlugin(%s?action=settings_open)' % (sys.argv[0])))
                cm.append((language(30410).encode("utf-8"), 'RunPlugin(%s?action=playlist_open)' % (sys.argv[0])))
                cm.append((language(30411).encode("utf-8"), 'RunPlugin(%s?action=addon_home)' % (sys.argv[0])))

                item = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=poster)
                item.setInfo( type="Video", infoLabels = meta )
                item.setProperty("IsPlayable", "true")
                item.setProperty("Video", "true")
                item.setProperty("Fanart_Image", fanart)
                item.addContextMenuItems(cm, replaceItems=True)
                xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=item,totalItems=total,isFolder=True)
            except:
                pass

    def episodeList(self, episodeList):
        if episodeList == None: return

        total = len(episodeList)
        for i in episodeList:
            try:
                name, url, image, date, year, imdb, genre, plot = i['name'], i['url'], i['image'], i['date'], i['year'], i['imdb'], i['genre'], i['plot']
                title, show, season, episode = i['title'], i['show'], i['season'], i['episode']
                if plot == '': plot = addonDesc
                if genre == '': genre = ' '

                sysname, systitle, sysimdb, sysyear, sysurl = urllib.quote_plus(name), urllib.quote_plus(title), urllib.quote_plus(imdb), urllib.quote_plus(year), urllib.quote_plus(url)
                u = '%s?action=play&name=%s&title=%s&imdb=%s&year=%s&url=%s&t=%s' % (sys.argv[0], sysname, systitle, sysimdb, sysyear, sysurl, datetime.datetime.now().strftime("%Y%m%d%H%M%S%f"))

                if getSetting("meta") == 'true':
                    imdb = re.sub("[^0-9]", "", imdb)
                    meta = metaget.get_episode_meta(title, imdb, season, episode)
                    meta.update({'tvshowtitle': show})
                    if meta['title'] == '': meta.update({'title': title})
                    if meta['episode'] == '': meta.update({'episode': episode})
                    if meta['premiered'] == '': meta.update({'premiered': date})
                    if meta['plot'] == '': meta.update({'plot': plot})
                    playcountMenu = language(30407).encode("utf-8")
                    if meta['overlay'] == 6: playcountMenu = language(30408).encode("utf-8")
                    metaimdb, metaseason, metaepisode = urllib.quote_plus(re.sub("[^0-9]", "", str(meta['imdb_id']))), urllib.quote_plus(str(meta['season'])), urllib.quote_plus(str(meta['episode']))
                    label = str(meta['season']) + 'x' + '%02d' % int(meta['episode']) + ' . ' + meta['title']
                    if action == 'episodes_subscriptions': label = show + ' - ' + label
                    poster = meta['cover_url']
                    if poster == '': poster = image
                else:
                    meta = {'label': title, 'title': title, 'tvshowtitle': show, 'season': season, 'episode': episode, 'imdb_id' : imdb, 'year' : year, 'premiered' : date, 'genre' : genre, 'plot': plot}
                    label = season + 'x' + '%02d' % int(episode) + ' . ' + title
                    if action == 'episodes_subscriptions': label = show + ' - ' + label
                    poster = image
                if getSetting("meta") == 'true' and getSetting("fanart") == 'true':
                    fanart = meta['backdrop_url']
                    if fanart == '': fanart = addonFanart
                else:
                    fanart = addonFanart

                cm = []
                cm.append((language(30432).encode("utf-8"), 'RunPlugin(%s?action=sources&name=%s&title=%s&imdb=%s&year=%s&url=%s)' % (sys.argv[0], sysname, systitle, sysimdb, sysyear, sysurl)))
                cm.append((language(30405).encode("utf-8"), 'RunPlugin(%s?action=item_queue)' % (sys.argv[0])))
                cm.append((language(30406).encode("utf-8"), 'RunPlugin(%s?action=download&name=%s&title=%s&imdb=%s&year=%s&url=%s)' % (sys.argv[0], sysname, systitle, sysimdb, sysyear, sysurl)))
                cm.append((language(30403).encode("utf-8"), 'RunPlugin(%s?action=item_play_from_here&url=%s)' % (sys.argv[0], sysurl)))
                cm.append((language(30414).encode("utf-8"), 'Action(Info)'))
                if getSetting("meta") == 'true': cm.append((language(30415).encode("utf-8"), 'RunPlugin(%s?action=metadata_episodes&imdb=%s&season=%s&episode=%s)' % (sys.argv[0], metaimdb, metaseason, metaepisode)))
                if getSetting("meta") == 'true': cm.append((playcountMenu, 'RunPlugin(%s?action=playcount_episodes&imdb=%s&season=%s&episode=%s)' % (sys.argv[0], metaimdb, metaseason, metaepisode)))
                cm.append((language(30431).encode("utf-8"), 'RunPlugin(%s?action=view_episodes)' % (sys.argv[0])))
                cm.append((language(30410).encode("utf-8"), 'RunPlugin(%s?action=playlist_open)' % (sys.argv[0])))
                cm.append((language(30411).encode("utf-8"), 'RunPlugin(%s?action=addon_home)' % (sys.argv[0])))

                item = xbmcgui.ListItem(label, iconImage="DefaultVideo.png", thumbnailImage=poster)
                item.setInfo( type="Video", infoLabels = meta )
                item.setProperty("IsPlayable", "true")
                item.setProperty("Video", "true")
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

    def item_play_from_here(self, url):
        playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        playlist.clear()
        playlist.unshuffle()
        total = xbmc.getInfoLabel('Container.NumItems')
        for i in range(0, int(total)):
            i = str(i)
            label = xbmc.getInfoLabel('ListItemNoWrap(%s).Label' % i)
            if label == '': break

            path = xbmc.getInfoLabel('ListItemNoWrap(%s).FileNameAndPath' % i)
            query = urlparse.urlparse(path.replace(sys.argv[0],'')).query
            name, title, imdb, year, url = urlparse.parse_qs(query)['name'][0], urlparse.parse_qs(query)['title'][0], urlparse.parse_qs(query)['imdb'][0], urlparse.parse_qs(query)['year'][0], urlparse.parse_qs(query)['url'][0]
            sysname, systitle, sysimdb, sysyear, sysurl = urllib.quote_plus(name), urllib.quote_plus(title), urllib.quote_plus(imdb), urllib.quote_plus(year), urllib.quote_plus(url)
            u = '%s?action=play&name=%s&title=%s&imdb=%s&year=%s&url=%s' % (sys.argv[0], sysname, systitle, sysimdb, sysyear, sysurl)

            meta = {'label' : xbmc.getInfoLabel('ListItemNoWrap(%s).title' % i), 'title' : xbmc.getInfoLabel('ListItemNoWrap(%s).title' % i), 'tvshowtitle': xbmc.getInfoLabel('ListItemNoWrap(%s).tvshowtitle' % i), 'imdb_id' : xbmc.getInfoLabel('ListItemNoWrap(%s).imdb_id' % i), 'season' : xbmc.getInfoLabel('ListItemNoWrap(%s).season' % i), 'episode' : xbmc.getInfoLabel('ListItemNoWrap(%s).episode' % i), 'writer' : xbmc.getInfoLabel('ListItemNoWrap(%s).writer' % i), 'director' : xbmc.getInfoLabel('ListItemNoWrap(%s).director' % i), 'rating' : xbmc.getInfoLabel('ListItemNoWrap(%s).rating' % i), 'duration' : xbmc.getInfoLabel('ListItemNoWrap(%s).duration' % i), 'plot' : xbmc.getInfoLabel('ListItemNoWrap(%s).plot' % i), 'premiered' : xbmc.getInfoLabel('ListItemNoWrap(%s).premiered' % i), 'genre' : xbmc.getInfoLabel('ListItemNoWrap(%s).genre' % i)}
            poster, fanart = xbmc.getInfoLabel('ListItemNoWrap(%s).icon' % i), xbmc.getInfoLabel('ListItemNoWrap(%s).Property(Fanart_Image)' % i)

            item = xbmcgui.ListItem(label, iconImage="DefaultVideo.png", thumbnailImage=poster)
            item.setInfo( type="Video", infoLabels= meta )
            item.setProperty("IsPlayable", "true")
            item.setProperty("Video", "true")
            item.setProperty("Fanart_Image", fanart)
            playlist.add(u, item)
        xbmc.Player().play(playlist)

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

    def subscription_add(self, name, url, image, imdb, year):
        try:
            status = metaget.get_meta('tvshow', name, imdb_id=imdb)['status']
            if status == 'Ended':
            	yes = index().yesnoDialog(language(30347).encode("utf-8"), language(30348).encode("utf-8"))
            	if not yes: return
            file = open(subData, 'a+')
            file.write('"%s"|"%s"|"%s"|"%s"|"%s"\n' % (name, year, imdb, url, image))
            file.close()
            self.library(name, url, imdb, year, silent=True)
            index().container_refresh()
            index().infoDialog(language(30312).encode("utf-8"), name)
        except:
            return

    def subscription_from_search(self, name, url, image, imdb, year):
        try:
            file = xbmcvfs.File(subData)
            read = file.read()
            file.close()
            if url in read:
                index().infoDialog(language(30316).encode("utf-8"), name)
                return
            status = metaget.get_meta('tvshow', name, imdb_id=imdb)['status']
            if status == 'Ended':
            	yes = index().yesnoDialog(language(30347).encode("utf-8"), language(30348).encode("utf-8"))
            	if not yes: return
            file = open(subData, 'a+')
            file.write('"%s"|"%s"|"%s"|"%s"|"%s"\n' % (name, year, imdb, url, image))
            file.close()
            self.library(name, url, imdb, year, silent=True)
            index().infoDialog(language(30312).encode("utf-8"), name)
        except:
            return

    def subscription_delete(self, name, url, silent=False):
        try:
            file = xbmcvfs.File(subData)
            read = file.read()
            file.close()
            line = [x for x in re.compile('(".+?)\n').findall(read) if '"%s"' % url in x][0]
            list = re.compile('(".+?\n)').findall(read.replace(line, ''))
            file = open(subData, 'w')
            for line in list: file.write(line)
            file.close()
            if silent == False:
                index().container_refresh()
                index().infoDialog(language(30313).encode("utf-8"), name)
        except:
            return

    def subscriptions_update(self, silent=False):
        try:
            if getSetting("subscriptions_update") == 'true' and getSetting("subscriptions_clean") == 'true':
                self.subscriptions_clean(silent=True)
            file = xbmcvfs.File(subData)
            read = file.read()
            file.close()
            match = re.compile('"(.+?)"[|]"(.+?)"[|]"(.+?)"[|]"(.+?)"[|]"(.+?)"').findall(read)
            for name, year, imdb, url, image in match:
                if xbmc.abortRequested == True: sys.exit()
                self.library(name, url, imdb, year, silent=True)
            if getSetting("subscriptions_update") == 'true' and getSetting("subscriptions_updatelibrary") == 'true':
                xbmc.executebuiltin('UpdateLibrary(video)')
            if silent == False:
                index().infoDialog(language(30314).encode("utf-8"))
        except:
            return

    def subscriptions_clean(self, silent=False):
        try:
            file = xbmcvfs.File(subData)
            read = file.read()
            file.close()
            match = re.compile('"(.+?)"[|]"(.+?)"[|]"(.+?)"[|]"(.+?)"').findall(read)
            for name, imdb, url, image in match:
            	status = metaget.get_meta('tvshow', name, imdb_id=imdb)['status']
            	if status == 'Ended':
            	    self.subscription_delete(name, url, silent=True)
            if silent == False:
                index().container_refresh()
                index().infoDialog(language(30315).encode("utf-8"))
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

    def library(self, name, url, imdb, year, silent=False):
        try:
            library = xbmc.translatePath(getSetting("tv_library"))
            show = name
            enc_show = show.translate(None, '\/:*?"<>|')
            folder = os.path.join(library, enc_show)
            xbmcvfs.mkdir(dataPath)
            xbmcvfs.mkdir(library)
            xbmcvfs.mkdir(folder)
            seasonList = seasons().get(url, '', year, imdb, '', '', show, idx=False)
            for i in seasonList:
                season = i['name']
                seasonUrl = i['url']
                enc_season = season.translate(None, '\/:*?"<>|')
                seasonDir = os.path.join(folder, enc_season)
                xbmcvfs.mkdir(seasonDir)
                episodeList = episodes().get(season, seasonUrl, '', '', '', '', '', show, idx=False)
                for i in episodeList:
                    name, title, date = i['name'], i['title'], i['date']
                    sysname, systitle, sysyear, sysdate, sysimdb = urllib.quote_plus(name), urllib.quote_plus(title), urllib.quote_plus(year), urllib.quote_plus(date), urllib.quote_plus(imdb)
                    content = '%s?action=play&name=%s&title=%s&imdb=%s&year=%s&date=%s' % (sys.argv[0], sysname, systitle, sysimdb, sysyear, sysdate)
                    enc_name = name.translate(None, '\/:*?"<>|')
                    stream = os.path.join(seasonDir, enc_name + '.strm')
                    file = xbmcvfs.File(stream, 'w')
                    file.write(content)
                    file.close()
            if silent == False:
                index().infoDialog(language(30311).encode("utf-8"), show)
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
        meta = {'label': xbmc.getInfoLabel('ListItem.label'), 'title': xbmc.getInfoLabel('ListItem.title'), 'tvshowtitle': xbmc.getInfoLabel('ListItem.tvshowtitle'), 'season': xbmc.getInfoLabel('ListItem.season'), 'episode': xbmc.getInfoLabel('ListItem.episode'), 'imdb_id': xbmc.getInfoLabel('ListItem.imdb_id'), 'tvdb_id': xbmc.getInfoLabel('ListItem.tvdb_id'), 'episode_id': xbmc.getInfoLabel('ListItem.episode_id'), 'trailer_url': xbmc.getInfoLabel('ListItem.trailer_url'), 'premiered': xbmc.getInfoLabel('ListItem.premiered'), 'director': xbmc.getInfoLabel('ListItem.director'), 'writer': xbmc.getInfoLabel('ListItem.writer'), 'rating': xbmc.getInfoLabel('ListItem.rating'), 'overlay': xbmc.getInfoLabel('ListItem.overlay'), 'genre': xbmc.getInfoLabel('ListItem.genre'), 'plot': xbmc.getInfoLabel('ListItem.plot')}
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

class subscriptions:
    def __init__(self):
        self.list = []

    def shows(self):
        file = xbmcvfs.File(subData)
        read = file.read()
        file.close()
        match = re.compile('"(.+?)"[|]"(.+?)"[|]"(.+?)"[|]"(.+?)"[|]"(.+?)"').findall(read)
        for name, year, imdb, url, image in match:
            self.list.append({'name': name, 'url': url, 'image': image, 'year': year, 'imdb': imdb, 'genre': '', 'plot': ''})
        self.list = sorted(self.list, key=itemgetter('name'))
        index().showList(self.list)

    def episodes(self):
        try:
            file = xbmcvfs.File(subData)
            read = file.read()
            file.close()

            if read == '':
                index().okDialog(language(30323).encode("utf-8"), language(30324).encode("utf-8"))
            if not getSetting("subscriptions_update") == 'true':
                index().okDialog(language(30325).encode("utf-8"), language(30326).encode("utf-8"))

            imdbDict, seasons, episodes = {}, [], []
            library = xbmc.translatePath(getSetting("tv_library"))
            match = re.compile('"(.+?)"[|]"(.+?)"[|]"(.+?)"[|]"(.+?)"[|]"(.+?)"').findall(read)
            for name, year, imdb, url, image in match: imdbDict.update({imdb:image})
            shows = [os.path.join(library, i) for i in xbmcvfs.listdir(library)[0]]
            for show in shows: seasons += [os.path.join(show, i) for i in xbmcvfs.listdir(show)[0]]
            for season in seasons: episodes += [os.path.join(season, i) for i in xbmcvfs.listdir(season)[1] if i.endswith('.strm')]
        except:
            pass

        for episode in episodes:
            try:
                file = xbmcvfs.File(episode)
                read = file.read()
                file.close()
                if not read.startswith(sys.argv[0]): raise Exception()
                path = urlparse.urlparse(read).path
                name, title, imdb, year, date = urlparse.parse_qs(path)['name'][0], urlparse.parse_qs(path)['title'][0], urlparse.parse_qs(path)['imdb'][0], urlparse.parse_qs(path)['year'][0], urlparse.parse_qs(path)['date'][0]
                image = imdbDict[imdb]
                show = name.rsplit(' ', 1)[0]
                season = '%01d' % int(name.rsplit(' ', 1)[-1].split('S')[-1].split('E')[0])
                num = '%01d' % int(name.rsplit(' ', 1)[-1].split('E')[-1])
                sort = date.replace('-','')
                self.list.append({'name': name, 'url': name, 'image': image, 'date': date, 'year': year, 'imdb': imdb, 'genre': '', 'plot': '', 'title': title, 'show': show, 'season': season, 'episode': num, 'episode': num, 'sort': sort})
            except:
                pass

        self.list = sorted(self.list, key=itemgetter('sort'))
        self.list = self.list[::-1][:100]

        index().episodeList(self.list)

class favourites:
    def __init__(self):
        self.list = []

    def shows(self):
        file = xbmcvfs.File(favData)
        read = file.read()
        file.close()
        match = re.compile('"(.+?)"[|]"(.+?)"[|]"(.+?)"[|]"(.+?)"[|]"(.+?)"').findall(read)
        for name, year, imdb, url, image in match:
            if getSetting("fav_sort") == '1':
                try: status = metaget.get_meta('tvshow', name, imdb_id=imdb)['status']
                except: status = ''
            else:
                status = ''
            self.list.append({'name': name, 'url': url, 'image': image, 'year': year, 'imdb': imdb, 'genre': '', 'plot': '', 'status': status})

        if getSetting("fav_sort") == '0':
            self.list = sorted(self.list, key=itemgetter('name'))
        elif getSetting("fav_sort") == '1':
            filter = []
            self.list = sorted(self.list, key=itemgetter('name'))
            filter += [i for i in self.list if not i['status'] == 'Ended']
            filter += [i for i in self.list if i['status'] == 'Ended']
            self.list = filter

        index().showList(self.list)

class root:
    def get(self):
        rootList = []
        rootList.append({'name': 30501, 'image': 'Episodes.png', 'action': 'episodes_subscriptions'})
        rootList.append({'name': 30502, 'image': 'Popular.png', 'action': 'shows_popular'})
        rootList.append({'name': 30503, 'image': 'Rating.png', 'action': 'shows_rating'})
        rootList.append({'name': 30504, 'image': 'Views.png', 'action': 'shows_views'})
        rootList.append({'name': 30505, 'image': 'Active.png', 'action': 'shows_active'})
        rootList.append({'name': 30506, 'image': 'Genres.png', 'action': 'genres_shows'})
        rootList.append({'name': 30507, 'image': 'Favourites.png', 'action': 'shows_favourites'})
        rootList.append({'name': 30508, 'image': 'Subscriptions.png', 'action': 'shows_subscriptions'})
        rootList.append({'name': 30509, 'image': 'Search.png', 'action': 'shows_search'})
        index().rootList(rootList)
        index().downloadList()

class link:
    def __init__(self):
        self.imdb_base = 'http://www.imdb.com'
        self.imdb_akas = 'http://akas.imdb.com'
        self.imdb_genre = 'http://akas.imdb.com/genre'
        self.imdb_genres = 'http://akas.imdb.com/search/title?title_type=tv_series,mini_series&sort=moviemeter,asc&count=25&start=1&genres=%s'
        self.imdb_popular = 'http://akas.imdb.com/search/title?title_type=tv_series,mini_series&sort=moviemeter,asc&count=25&start=1'
        self.imdb_rating = 'http://akas.imdb.com/search/title?title_type=tv_series,mini_series&sort=user_rating,desc&count=25&start=1'
        self.imdb_views = 'http://akas.imdb.com/search/title?title_type=tv_series,mini_series&sort=num_votes,desc&count=25&start=1'
        self.imdb_active = 'http://akas.imdb.com/search/title?title_type=tv_series,mini_series&production_status=active&sort=moviemeter,asc&count=25&start=1'
        self.imdb_search = 'http://akas.imdb.com/search/title?title_type=tv_series,mini_series&sort=moviemeter,asc&count=25&start=1&title=%s'
        self.imdb_episodes = 'http://www.imdb.com/title/tt%s/episodes?season=%s'

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
            genres = common.parseDOM(result, "table")
            genres = common.parseDOM(result, "td")
        except:
            return
        for genre in genres:
            try:
                name = common.parseDOM(genre, "a")[0]
                name = common.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = common.parseDOM(genre, "a", ret="href")[0]
                if not url.startswith('/genre/'): raise Exception()
                url = url.split('/genre/', 1)[-1]
                url = link().imdb_genres % url
                url = common.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                image = addonGenres.encode('utf-8')

                self.list.append({'name': name, 'url': url, 'image': image})
            except:
                pass

        return self.list

class shows:
    def __init__(self):
        self.list = []

    def imdb(self, url):
        #self.list = self.imdb_list(url)
        self.list = cache(self.imdb_list, url)
        index().showList(self.list)
        index().nextList(self.list)

    def imdb_popular(self):
        #self.list = self.imdb_list(link().imdb_popular)
        self.list = cache(self.imdb_list, link().imdb_popular)
        index().showList(self.list)
        index().nextList(self.list)

    def imdb_rating(self):
        #self.list = self.imdb_list(link().imdb_rating)
        self.list = cache(self.imdb_list, link().imdb_rating)
        index().showList(self.list)
        index().nextList(self.list)

    def imdb_views(self):
        #self.list = self.imdb_list(link().imdb_views)
        self.list = cache(self.imdb_list, link().imdb_views)
        index().showList(self.list)
        index().nextList(self.list)

    def imdb_active(self):
        #self.list = self.imdb_list(link().imdb_active)
        self.list = cache(self.imdb_list, link().imdb_active)
        index().showList(self.list)
        index().nextList(self.list)

    def imdb_search(self, query=None):
        if query is None:
            self.query = common.getUserInput(language(30362).encode("utf-8"), '')
        else:
            self.query = query
        if not (self.query is None or self.query == ''):
            self.query = link().imdb_search % urllib.quote_plus(self.query)
            self.list = self.imdb_list(self.query)
            index().showList(self.list)

    def imdb_list(self, url):
        try:
            result = getUrl(url.replace(link().imdb_base, link().imdb_akas)).result
            result = result.decode('iso-8859-1').encode('utf-8')
            shows = common.parseDOM(result, "tr", attrs = { "class": ".+?" })
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

        for show in shows:
            try:
                name = common.parseDOM(show, "a")[1]
                name = common.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                url = common.parseDOM(show, "a", ret="href")[0]
                url = '%s%s' % (link().imdb_base, url)
                url = common.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                image = common.parseDOM(show, "img", ret="src")[0]
                if not ('._SX' in image or '._SY' in image): raise Exception()
                image = image.rsplit('._SX', 1)[0].rsplit('._SY', 1)[0] + '._SX1000.' + image.rsplit('.', 1)[-1]
                image = common.replaceHTMLCodes(image)
                image = image.encode('utf-8')

                year = common.parseDOM(show, "span", attrs = { "class": "year_type" })[0]
                year = re.sub("[^0-9]", "", year)[:4]
                year = year.encode('utf-8')

                imdb = re.sub("[^0-9]", "", url.rsplit('tt', 1)[-1])
                imdb = imdb.encode('utf-8')

                try:
                    genre = common.parseDOM(show, "span", attrs = { "class": "genre" })
                    genre = common.parseDOM(genre, "a")
                    genre = str(genre).replace("[u'", '').replace("']", '').replace("', u'", ' / ')
                    genre = common.replaceHTMLCodes(genre)
                    genre = genre.encode('utf-8')
                except:
                    genre = ''

                try:
                    plot = common.parseDOM(show, "span", attrs = { "class": "outline" })[0]
                    plot = common.replaceHTMLCodes(plot)
                    plot = plot.encode('utf-8')
                except:
                    plot = ''

                self.list.append({'name': name, 'url': url, 'image': image, 'year': year, 'imdb': imdb, 'genre': genre, 'plot': plot, 'next': next})
            except:
                pass

        return self.list

class seasons:
    def __init__(self):
        self.list = []

    def get(self, url, image, year, imdb, genre, plot, show, idx=True):
        if idx == True:
            #self.list = self.imdb_list(url, image, year, imdb, genre, plot, show)
            self.list = cache2(self.imdb_list, url, image, year, imdb, genre, plot, show)
            index().seasonList(self.list)
        else:
            self.list = self.imdb_list(url, image, year, imdb, genre, plot, show)
            return self.list

    def imdb_list(self, url, image, year, imdb, genre, plot, show):
        try:
            result = getUrl(url.replace(link().imdb_base, link().imdb_akas)).result
            result = result.decode('iso-8859-1').encode('utf-8')
            if imdb == '0': imdb = re.sub("[^0-9]", "", url.rsplit('tt', 1)[-1])
            seasons = re.compile('/title/tt%s/episodes[?]season=(\d+)' % imdb).findall(result.replace('\n',''))
            seasons = uniqueList(seasons).list
            seasons = seasons[::-1]
        except:
            return

        for season in seasons:
            try:
                num = re.sub("[^0-9]", "", season)
                num = '%01d' % int(num)
                num = num.encode('utf-8')

                name = '%s %s' % ('Season', num)
                name = name.encode('utf-8')

                url = link().imdb_episodes % (imdb, season)
                url = common.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                if season == seasons[-1]:
                    episodeList = episodes().get(name, url, '', '', '', '', '', show, idx=False)
                    if episodeList == []: raise Exception()

                self.list.append({'name': name, 'url': url, 'image': image, 'year': year, 'imdb': imdb, 'genre': genre, 'plot': plot, 'show': show, 'season': num})
            except:
                pass

        return self.list

class episodes:
    def __init__(self):
        self.list = []

    def get(self, name, url, image, year, imdb, genre, plot, show, idx=True):
        if idx == True:
            #self.list = self.imdb_list(name, url, image, year, imdb, genre, plot, show)
            self.list = cache(self.imdb_list, name, url, image, year, imdb, genre, plot, show)
            index().episodeList(self.list)
        else:
            self.list = self.imdb_list(name, url, image, year, imdb, genre, plot, show)
            return self.list

    def imdb_list(self, name, url, image, year, imdb, genre, plot, show):
        try:
            season = re.sub("[^0-9]", "", name)
            season = season.encode('utf-8')
            result = getUrl(url.replace(link().imdb_base, link().imdb_akas)).result
            result = result.decode('iso-8859-1').encode('utf-8')
            episodes = common.parseDOM(result, "div", attrs = { "class": "list_item.+?" })
        except:
            return

        for episode in episodes:
            try:
                title = common.parseDOM(episode, "a", ret="title")[0]
                title = common.replaceHTMLCodes(title)
                title = title.encode('utf-8')

                num = common.parseDOM(episode, "meta", ret="content", attrs = { "itemprop": "episodeNumber" })[0]
                num = re.sub("[^0-9]", "", '%01d' % int(num))
                num = num.encode('utf-8')

                name = show + ' S' + '%02d' % int(season) + 'E' + '%02d' % int(num)
                name = common.replaceHTMLCodes(name)
                name = name.encode('utf-8')

                desc = common.parseDOM(episode, "div", attrs = { "class": "item_description" })[0]
                if 'update=tt' in desc: desc = plot
                desc = common.replaceHTMLCodes(desc)
                desc = desc.encode('utf-8')

                try:
                    date = common.parseDOM(episode, "div", attrs = { "class": "airdate" })[0]
                    d1 = re.compile('(\d{4})').findall(date)[0]
                    date = date.replace(d1,'').strip()
                    d3 = re.sub("[^0-9]", "", date)
                    date = date.replace(d3,'').strip()
                    d3 = '%02d' % int(d3)
                    date = date.replace('Jan','01').replace('Feb','02').replace('Mar','03').replace('Apr','04').replace('May','05').replace('Jun','06').replace('Jul','07').replace('Aug','08').replace('Sep','09').replace('Oct','10').replace('Nov','11').replace('Dec','12').strip()
                    d2 = re.sub("[^0-9]", "", date)
                    d2 = '%02d' % int(d2)
                    date = '%s-%s-%s' % (d1, d2, d3)
                    date = date.encode('utf-8')
                except:
                    date = metaget.get_episode_meta(show, imdb, season, num)['premiered']
                    date = date.encode('utf-8')

                if int(date.replace('-','')) > int((datetime.datetime.utcnow() - datetime.timedelta(hours = 5)).strftime("%Y%m%d")): raise Exception()

                self.list.append({'name': name, 'url': name, 'image': image, 'date': date, 'year': year, 'imdb': imdb, 'genre': genre, 'plot': desc, 'title': title, 'show': show, 'season': season, 'episode': num})
            except:
                pass

        return self.list

class resolver:
    def __init__(self):
        self.sources_dict()
        self.sources = []

    def run(self, name, title, imdb, year, url):
        try:
            if player().status() is True: return

            show = name.rsplit(' ', 1)[0]
            season = '%01d' % int(name.rsplit(' ', 1)[-1].split('S')[-1].split('E')[0])
            episode = '%01d' % int(name.rsplit(' ', 1)[-1].split('E')[-1])

            self.sources = self.sources_get(show, season, episode, name, title, imdb, year, self.hostDict)
            self.sources = self.sources_filter()


            autoplay = getSetting("autoplay")
            if not xbmc.getInfoLabel('Container.FolderPath').startswith(sys.argv[0]):
                autoplay = getSetting("autoplay_library")

            if url == 'sources://' or url == 'download://' or not autoplay == 'true':
                url = self.sources_dialog()
            else:
                url = self.sources_direct()


            if url is None: raise Exception()
            if url == 'download://': return url
            if url == 'close://': return

            player().run(name, url)
            return url
        except:
            index().infoDialog(language(30318).encode("utf-8"))
            return

    def sources_get(self, show, season, episode, name, title, imdb, year, hostDict):
        threads = []

        global watchseries_sources
        watchseries_sources = []
        threads.append(Thread(watchseries().get, show, season, episode, name, title, imdb, year, hostDict))

        global simplymovies_sources
        simplymovies_sources = []
        if getSetting("simplymovies") == 'true':
            threads.append(Thread(simplymovies().get, show, season, episode, name, title, imdb, year, hostDict))

        global watchmoviesonline_sources
        watchmoviesonline_sources = []
        if getSetting("watchonline") == 'true':
            threads.append(Thread(watchmoviesonline().get, show, season, episode, name, title, imdb, year, hostDict))

        global tvonline_sources
        tvonline_sources = []
        if getSetting("tvonline") == 'true':
            threads.append(Thread(tvonline().get, show, season, episode, name, title, imdb, year, hostDict))

        global moviestorm_sources
        moviestorm_sources = []
        if getSetting("moviestorm") == 'true':
            threads.append(Thread(moviestorm().get, show, season, episode, name, title, imdb, year, hostDict))

        global istreamhd_sources
        istreamhd_sources = []
        if getSetting("istreamhd") == 'true':
            threads.append(Thread(istreamhd().get, show, season, episode, name, title, imdb, year, hostDict))

        [i.start() for i in threads]
        [i.join() for i in threads]

        self.sources = watchseries_sources + simplymovies_sources + watchmoviesonline_sources + tvonline_sources + moviestorm_sources + istreamhd_sources

        return self.sources

    def sources_resolve(self, url, provider):
        try:
            if provider == 'Watchseries': url = watchseries().resolve(url)
            elif provider == 'Watchonline': url = watchmoviesonline().resolve(url)
            elif provider == 'Simplymovies': url = simplymovies().resolve(url)
            elif provider == 'TVonline': url = tvonline().resolve(url)
            elif provider == 'Moviestorm': url = moviestorm().resolve(url)
            elif provider == 'iStreamHD': url = istreamhd().resolve(url)
            return url
        except:
            return

    def sources_filter(self):
        filter = []
        #host_rank = ['VKHD', 'WatchfreeinHD', 'TVonline', 'VK', 'Movreel', 'iShared', 'Putlocker', 'Sockshare', 'Flashx', 'Played', 'Vidx', 'Streamcloud']
        host_rank = [getSetting("hosthd1"), getSetting("hosthd2"), getSetting("host1"), getSetting("host2"), getSetting("host3"), getSetting("host4"), getSetting("host5"), getSetting("host6"), getSetting("host7"), getSetting("host8"), getSetting("host9"), getSetting("host10")]
        host_rank = uniqueList(host_rank + sorted(self.hostDict.keys())).list
        for host in host_rank: filter += [i for i in self.sources if i['source'] == host]
        self.sources = filter

        if not getSetting("quality") == 'true':
            self.sources = [i for i in self.sources if not i['quality'] == 'HD']
        if not getSetting("hosthd1") == 'VKHD':
            self.sources = [i for i in self.sources if not i['source'] == 'VKHD']
        if not getSetting("hosthd2") == 'WatchfreeinHD':
            self.sources = [i for i in self.sources if not i['source'] == 'WatchfreeinHD']

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
        'Youwatch' : 'youwatch.org',
        'Zalaa' : 'zalaa.com'
        }


class watchseries:
    def __init__(self):
        self.watchseries_base = 'http://watchseries.lt'
        self.watchseries_search = 'http://watchseries.lt/search/%s'
        self.watchseries_episodes = 'http://watchseries.lt/episode/%s_s%s_e%s.html'

    def get(self, show, season, episode, name, title, imdb, year, hostDict):
        try:
            global watchseries_sources
            watchseries_sources = []

            url = None
            query = self.watchseries_search % urllib.quote_plus(show)
            result = getUrl(query).result
            result = result.replace(' (%s)' % str(int(year) - 1), ' (%s)' % year)
            shows = re.compile('href="(/serie/.+?)".+?[(]%s[)]' % year).findall(result)
            shows = uniqueList(shows).list

            for show in shows[:5]:
                try:
                    showsUrl = '%s%s' % (self.watchseries_base, show)
                    result = getUrl(showsUrl).result
                    if str('tt' + imdb) in result:
                        url = show.split('/')[-1]
                        break
                except:
                    pass

            if url == None: return
            url = self.watchseries_episodes % (url, season, episode)
            result = getUrl(url).result

            for host in sorted(hostDict.keys()):
                try:
                    match = hostDict[host]
                    sources = re.compile('<span>%s</span>.+?href="(.+?)"' % match).findall(result)
                    for url in sources:
                        url = '%s%s' % (self.watchseries_base, url)
                        watchseries_sources.append({'source': host, 'quality': 'SD', 'provider': 'Watchseries', 'url': url})
                except:
                    pass
        except:
            return

    def resolve(self, url):
        try:
            result = getUrl(url).result
            url = common.parseDOM(result, "a", ret="href", attrs = { "class": "myButton" })[0]

            host = urlresolver.HostedMediaFile(url)
            if host: resolver = urlresolver.resolve(url)
            if not resolver.startswith('http://'): return
            if not resolver == url: return resolver
        except:
            return

class simplymovies:
    def __init__(self):
        self.simplymovies_base = 'http://simplymovies.net'
        self.simplymovies_search = 'http://simplymovies.net/tv_shows.php?searchTerm='

    def get(self, show, season, episode, name, title, imdb, year, hostDict):
        try:
            global simplymovies_sources
            simplymovies_sources = []

            query = self.simplymovies_search + urllib.quote_plus(show.replace(' ', '-'))

            result = getUrl(query).result
            url = common.parseDOM(result, "div", attrs = { "class": "movieInfoHolder" })
            try: match = [i for i in url if str('>' + show.lower() + '<') in i.lower()][0]
            except: pass
            try: match = [i for i in url if str('tt' + imdb) in i][0]
            except: pass
            url = common.parseDOM(match, "a", ret="href")[0]
            url = '%s/%s' % (self.simplymovies_base, url)
            url = common.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            result = getUrl(url).result
            url = result.split("<h3>Season %s" % season)[-1]
            url = url.split("<h3>")[0]
            url = url.rsplit('">Episode %s' % episode)[0].split('"')[-1]
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

class watchmoviesonline:
    def __init__(self):
        self.watchmoviesonline_base = 'http://watchmoviesonline.mobi'
        self.watchmoviesonline_search = 'http://watchmoviesonline.mobi/?movieorserie=1&search='
        self.watchmoviesonline_episodes = 'http://watchmoviesonline.mobi/title/%s?m=%s&s=%s&e=%s'

    def get(self, show, season, episode, name, title, imdb, year, hostDict):
        try:
            global watchmoviesonline_sources
            watchmoviesonline_sources = []

            url = None
            query = self.watchmoviesonline_search + urllib.quote_plus(show)
            result = getUrl(query).result
            shows = re.compile('(/title/.+?)/').findall(result)
            shows = uniqueList(shows).list

            for show in shows[:5]:
                try:
                    showsUrl = '%s%s' % (self.watchmoviesonline_base, show)
                    result = getUrl(showsUrl).result
                    if str('tt' + imdb) in result:
                        url = showsUrl.split('/')[-1]
                        break
                except:
                    pass

            if url == None: return
            url = self.watchmoviesonline_episodes % (url, url, season, episode)
            result = getUrl(url).result
            result = result.decode('iso-8859-1').encode('utf-8')
            result = result.replace('\n','')

            for v1, v2  in re.compile("return p}[(]'(.+?);',.+?,.+?,'(.+?)'.split").findall(result):
                try:
                    v2 = v2.split('|')
                    for i in range(len(v2)):
                        if v2[i]: v1 = re.sub('\\b%s\\b' % self.base36encode(i), v2[i], v1)
                    url = base64.b64decode(v1.split('"')[1])
                    url = common.parseDOM(url, "a")[0]
                    for host in sorted(hostDict.keys()):
                        if 'watchfreeinhd.com' in url:
                            watchmoviesonline_sources.append({'source': 'WatchfreeinHD', 'quality': 'HD', 'provider': 'Watchonline', 'url': url})
                            break
                        elif hostDict[host] in url:
                            watchmoviesonline_sources.append({'source': host, 'quality': 'SD', 'provider': 'Watchonline', 'url': url})
                except:
                    pass
        except:
            return

    def base36encode(self, number):
        if not isinstance(number, (int, long)):
            raise TypeError('number must be an integer')
        if number < 0:
            raise ValueError('number must be positive')

        alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        base36 = ''
        while number:
            number, i = divmod(number, 36)
            base36 = alphabet[i] + base36

        return base36 or alphabet[0]

    def resolve(self, url):
        try:
            host = urlresolver.HostedMediaFile(url)
            if host: resolver = urlresolver.resolve(url)
            if not resolver.startswith('http://'): return
            if not resolver == url: return resolver
        except:
            return

class tvonline:
    def __init__(self):
        self.tvonline_base = 'http://tvonline.cc'
        self.tvonline_search = 'https://www.google.com/search?as_q=%s+%s&as_sitesearch=%s&num=1'
        self.tvonline_login = 'http://www.tvonline.cc/reg.php'

    def get(self, show, season, episode, name, title, imdb, year, hostDict):
        try:
            global tvonline_sources
            tvonline_sources = []

            query = self.tvonline_search % (urllib.quote_plus(show), urllib.quote_plus(year), urllib.quote_plus(self.tvonline_base))

            result = getUrl(query).result
            match = common.parseDOM(result, "h3", attrs = { "class": "r" })[0]
            if not str(show.lower()) in match.lower(): raise Exception()
            url = common.parseDOM(match, "a", ret="href")[0]
            url = common.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            result = getUrl(url).result
            try: match = re.compile('S%01d, Ep%02d:.+?href="(.+?)"' % (int(season), int(episode))).findall(result)[-1]
            except: pass
            try: match = re.compile('href="(.+?)">%s<' % title.lower()).findall(result.lower())[-1]
            except: pass
            url = '%s%s' % (self.tvonline_base, match)
            url = common.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            tvonline_sources.append({'source': 'TVonline', 'quality': 'SD', 'provider': 'TVonline', 'url': url})
        except:
            return

    def resolve(self, url):
        for i in range(0, 2):
            try:
                tvonline_user = getSetting("tvonline_user")
                tvonline_password = getSetting("tvonline_password")

                result = getUrl(self.tvonline_login, close=False, cookie=True).result
                token = re.compile('name="(Token.+?)" value=".+?"').findall(result)[0]

                POST = '_method=POST&%s=login&UserUsername=gotv&subscriptionsPass=gotv' % (token)

                if not (tvonline_user == '' and tvonline_password == ''):
                    post = '_method=POST&%s=login&UserUsername=%s&subscriptionsPass=%s' % (token, urllib.quote_plus(tvonline_user), urllib.quote_plus(tvonline_password))
                    result = getUrl(self.tvonline_login, post=post, close=False, cookie=True).result
                    if 'Invalid Username' in result:
                        result = getUrl(self.tvonline_login, post=POST, close=False, cookie=True).result
                else:
                    result = getUrl(self.tvonline_login, post=POST, close=False, cookie=True).result

                result = getUrl(url).result

                url = common.parseDOM(result, "video", ret="src", attrs = { "id": "ipadvideo" })[0]
                url = common.replaceHTMLCodes(url)
                url = url.encode('utf-8')

                return url
            except:
                pass

class moviestorm:
    def __init__(self):
        self.moviestorm_base = 'http://moviestorm.eu'
        self.moviestorm_search = 'http://moviestorm.eu/search?q=%s'

    def get(self, show, season, episode, name, title, imdb, year, hostDict):
        try:
            global moviestorm_sources
            moviestorm_sources = []

            query = self.moviestorm_search % (urllib.quote_plus(show))
            result = getUrl(query).result

            url = common.parseDOM(result, "div", attrs = { "class": "movie_box" })
            url = [i for i in url if str('tt' + imdb) in i][0]
            url = common.parseDOM(url, "a", ret="href")[0]
            url = common.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            url = '%s?season=%s&episode=%s' % (url, season, episode)
            result = getUrl(url).result
            result = common.parseDOM(result, "div", attrs = { "id": "searialinks" })[0]
            links = re.compile('"(http://ishared.eu/.+?)"').findall(result)

            for url in links:
                moviestorm_sources.append({'source': 'iShared', 'quality': 'SD', 'provider': 'Moviestorm', 'url': url})

        except:
            return

    def resolve(self, url):
        try:
            result = getUrl(url).result
            url = re.compile('var xxxx = "(.+?)"').findall(result)[0]
            return url
        except:
            return

class istreamhd:
    def __init__(self):
        self.istreamhd_base = 'http://istreamhd.org'
        self.istreamhd_get = 'http://istreamhd.org/get'
        self.istreamhd_search = 'http://istreamhd.org/get/mini_search.php?&count=10&q=%s'
        self.istreamhd_watch = 'http://istreamhd.org//lib/get_embed.php?%s'

    def get(self, show, season, episode, name, title, imdb, year, hostDict):
        try:
            global istreamhd_sources
            istreamhd_sources = []

            query = self.istreamhd_search % (urllib.quote_plus(show))
            result = getUrl(query).result

            url = common.parseDOM(result, "div", attrs = { "class": "ui-block.+?" })
            url = [i for i in url if str('tt' + imdb) in i][0]
            url = common.parseDOM(url, "a", ret="href")[0]
            url = '%s%s' % (self.istreamhd_base, url)
            url = common.replaceHTMLCodes(url)
            url = url.encode('utf-8')

            result = getUrl(url).result
            url = result.split(">Season %s<" % season, 1)[-1]
            url = url.split(">Season %s<" % str(int(season) - 1), 1)[0]
            url = url.split(" E%s</a>" % episode, 1)[0]
            url = common.parseDOM(url, "a", ret="href")[-1]
            if not url.startswith('item.php'): raise Exception()
            url = '%s/%s' % (self.istreamhd_get, url)
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


main()