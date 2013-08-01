import urllib,urllib2,sys,re,xbmcplugin,xbmcgui,xbmcaddon,xbmc,os
#below you can add anything here just to keep your typing down to a minimum(shortcuts)
import datetime
import time
# i.e 
icon = 'http://a0.twimg.com/profile_images/1880386140/logo-square.jpg'
#now look at the first addDir where i have written icon then look at second listed item i have put the url for image directly makes no odds how you do it !!


ADDON = xbmcaddon.Addon(id='plugin.video.simplymovies')
if ADDON.getSetting('visitor_ga')=='':
    from random import randint
    ADDON.setSetting('visitor_ga',str(randint(0, 0x7fffffff)))
    
library=xbmc.translatePath(ADDON.getAddonInfo('profile'))
versionNumber = int(xbmc.getInfoLabel("System.BuildVersion" )[0:2])
VERSION = "1.0.7"
PATH = "Simply Movies"            
UATRACK="UA-35537758-1"    

ORDERBY = ['releaseDate', 'rating', 'views']
URL     = 'http://simplymovies.net/'


#addDir('name','url','mode','iconimage','triler') mode is where it tells the plugin where to go scroll to bottom to see where mode is
def CATEGORIES():
        addDir('Main Page',     URL, 1, icon)
        addDir('Search Movies', URL, 5, icon)
        addDir('Search TV',     URL, 4, icon)
        addDir('Movie Genre',   URL, 6, icon)
        addDir('TV Genre',      URL, 7, icon)

        setView('movies', 'default') 
        #setView is setting the automatic view.....first is what section "movies"......second is what you called it in the settings xml  
       
       
                                                                      
def main(page = 0):#  cause mode is empty in this one it will go back to first directory
    link = doSearch('movies', '', page = page).replace('\n','').replace('\r','').replace('\t','')

    link      = link.split('<div class="movieInfoOverlay">')
    url       = '<a href="movie.php(.+?)">'
    name      = '<h3 class="overlayMovieTitle">(.+?)</h3>'
    iconimage = '<img src="(.+?)"'
    trailer   = 'href="http://youtube.com/embed/(.+?)"'

    ignore = True

    for p in link:
        if ignore:
            ignore = False
            continue

        match = re.compile(url).findall(p)
        myUrl = match[0]

        match  = re.compile(name).findall(p)
        myName = match[0]

        if 'img src' in p:
            match       = re.compile(iconimage).findall(p)
            myIconimage = match[0]
        else:
            myIconimage = ''

        if 'Trailer' in p:
            match     = re.compile(trailer).findall(p)
            myTrailer = match[0]
        else:
            myTrailer = ''        

        addDir(myName, URL+'movie.php'+myUrl, 200, myIconimage, myTrailer)
    setView('tvshows', 'movies')
    
    addMore(len(link), mode = 1, page = page+1)
    
    
    
def genre_movie(page = 0, genre = None):#  cause mode is empty in this one it will go back to first directory
    if not genre:
        link=OPEN_URL(URL)#.replace('\n','').replace('\r','').replace('\t','')
        link=link.split('onchange="submitForm(\'movies\');">')[2]
        link=link.split('</select>')[0]
        r='<option value=".+?">(.+?)</option>'
        genreSelect=[]
        match=re.compile(r).findall(link)
        for genre in match: 
            if genre not in genreSelect:
                genreSelect.append(genre)

        genre = genreSelect[xbmcgui.Dialog().select('Please Select Genre', genreSelect)]

    link = doSearch('movies', '', page = page, genre = genre).replace('\n','').replace('\r','').replace('\t','')

    link      = link.split('<div class="movieInfoOverlay">')
    url       = '<a href="movie.php(.+?)">'
    name      = '<h3 class="overlayMovieTitle">(.+?)</h3>'
    iconimage = '<img src="(.+?)"'
    trailer   = 'href="http://youtube.com/embed/(.+?)"'

    ignore = True

    for p in link:
        if ignore:
            ignore = False
            continue

        match = re.compile(url).findall(p)
        myUrl = match[0]

        match  = re.compile(name).findall(p)
        myName = match[0]

        if 'img src' in p:
            match       = re.compile(iconimage).findall(p)
            myIconimage = match[0]
        else:
            myIconimage = ''

        if 'Trailer' in p:
            match   = re.compile(trailer).findall(p)
            myTrailer = match[0]
        else:
            myTrailer = ''        
        addDir(myName, URL+'/movie.php'+myUrl, 200, myIconimage, myTrailer)
    setView('tvshows', 'movies')

    addMore(len(link), mode = 6, page = page+1, genre = genre)
    
    
def genre_tv(page = 0, genre = None):#  cause mode is empty in this one it will go back to first directory
    if not genre:
        link=OPEN_URL(URL)#.replace('\n','').replace('\r','').replace('\t','')
        link=link.split('onchange="submitForm(\'movies\');">')[2]
        link=link.split('</select>')[0]
        r='<option value=".+?">(.+?)</option>'
        genreSelect=[]
        match=re.compile(r).findall(link)
        for genre in match: 
            if genre not in genreSelect:
                genreSelect.append(genre)

        genre = genreSelect[xbmcgui.Dialog().select('Please Select Genre', genreSelect)]

    link = doSearch('tv_shows', '', page = page, genre = genre).replace('\n','').replace('\r','').replace('\t','')

    link      = link.split('<div class="movieInfoOverlay">')
    url       = '<a href="tv_show.php(.+?)">'
    name      = '<h3 class="overlayMovieTitle">(.+?)</h3>'
    iconimage = '<img src="(.+?)"'
    trailer   = 'href="http://youtube.com/embed/(.+?)"'

    ignore = True

    for p in link:
        if ignore:
            ignore = False
            continue

        match = re.compile(url).findall(p)
        myUrl = match[0]

        match  = re.compile(name).findall(p)
        myName = match[0]

        if 'img src' in p:
            match       = re.compile(iconimage).findall(p)
            myIconimage = match[0]
        else:
            myIconimage = ''

        if 'Trailer' in p:
            match   = re.compile(trailer).findall(p)
            myTrailer = match[0]
        else:
            myTrailer = ''        
        addDir(myName, URL+'tv_show.php'+myUrl, 3, myIconimage, myTrailer)
    setView('tvshows', 'movies')

    addMore(len(link), mode = 7, page = page+1, genre = genre)
    
    
def search_tv(page = 0, _search = None):#  cause mode is empty in this one it will go back to first directory
    if not _search:
        _search = getSearch()  
        if not _search:
            return

    link = doSearch('tv_shows', _search, page = page).replace('\n','').replace('\r','').replace('\t','')

    r='<h3 class="overlayMovieTitle">(.+?)</h3>.+?<a href="(.+?)"><img src="(.+?)"'
    match=re.compile(r).findall(link)
    for name,url,iconimage in match: 
        addDir(name, URL+url, 3, iconimage)
    setView('tvshows', 'default') 

    addMore(len(match), mode = 4, page = page+1, search = _search)


def search_movies(page = 0, _search = None):#  cause mode is empty in this one it will go back to first directory+)
    if not _search:
        _search = getSearch()  
        if not _search:
            return

    link = doSearch('movies', _search, page = page).replace('\n','').replace('\r','').replace('\t','')

    GA('Movie',_search.replace('+',''))

    link      = link.split('<div class="movieInfoOverlay">')
    url       = '<a href="(.+?)">'
    name      = '<h3 class="overlayMovieTitle">(.+?)</h3>'
    iconimage = '<img src="(.+?)"'
    trailer   = 'href="http://youtube.com/embed/(.+?)"'

    ignore = True

    for p in link:
        if ignore:
            ignore = False
            continue

        match = re.compile(url).findall(p)
        myUrl = match[0]

        match  = re.compile(name).findall(p)
        myName = match[0]

        if 'img src' in p:
            match       = re.compile(iconimage).findall(p)
            myIconimage = match[0]
        else:
            myIconimage = ''

        if 'Trailer' in p:
            match   = re.compile(trailer).findall(p)
            myTrailer = match[0]
        else:
            myTrailer = ''  

        addDir(myName, URL+myUrl, 200, myIconimage, myTrailer)

    setView('tvshows', 'movies') 

    addMore(len(link), mode = 5, page = page+1, search = _search)
    

def get_episodes(name,url,iconimage):#  cause mode is empty in this one it will go back to first directory
    GA('Tv Show',name)
    link=OPEN_URL(url)
    r='<h3>(.+?)</h3>'
    match=re.compile(r).findall(link)
    urlselect=[]
    nameselect=[]
    for season in match:
        urlselect.append(season)
        nameselect.append(season)
    season=nameselect[xbmcgui.Dialog().select('Please Select Season', urlselect)]
    r='<h3>%s</h3>'% season
    link=link.split(r)[1]
    link=link.split('<h3>')[0]
    r='<a href="(.+?)">(.+?)</a>'
    match=re.compile(r).findall(link)
    for url,name in match: 
        addDir(name, URL+url, 200, iconimage)
    setView('tvshows', 'episodes') 
    
    
def getSearch():
        search_entered = ''
        keyboard = xbmc.Keyboard(search_entered, 'Search Simply Movies')
        keyboard.doModal()
        if keyboard.isConfirmed():
            search_entered = keyboard.getText() .replace(' ','+')  # sometimes you need to replace spaces with + or %20            
        return search_entered


def doSearch(category, search, page = 0, genre = ''):
    limit      = int(ADDON.getSetting('results'))
    lastRecord = page * limit

    data = dict()
    data['table']      = category
    data['lastRecord'] = lastRecord
    data['limit']      = limit
    data['where']      = '1 && title LIKE \'%' + search +'%\' && genres LIKE \'%' + genre +'%\''
    data['orderBy']    = ORDERBY[int(ADDON.getSetting('sort'))] + ' DESC'

    url = 'loadMore.php'
    if category == 'tv_shows':     
        url = 'loadMoreTvShows.php'
        if data['orderBy'] == 'releaseDate DESC':
            data['orderBy'] = 'rating DESC'    

    data     = urllib.urlencode(data)
    response = urllib.urlopen(URL+url, data).read()

    if response == '0' or response == '1':
        if page == 0:
            return oldSearch(category, search)
      
    if response == '0': 
        return 'error'
    if response == '1':
        return 'finished'

    return response     

def oldSearch(category, search):
    url = 'index.php'
    if category == 'tv_shows':  
        url = 'tv_shows.php'    

    url += '?searchTerm=' + urllib.quote_plus(search)

    return urllib.urlopen(URL+url).read()
     
    
def downloadPath(title):        		
    downloadFolder = ADDON.getSetting('download_folder')

    if ADDON.getSetting('ask_folder') == 'true':
        dialog = xbmcgui.Dialog()
	downloadFolder = dialog.browse(3, 'Save to folder...', 'files', '', False, False, downloadFolder)
	if downloadFolder == '' :
	    return None

    if downloadFolder is '':
        d = xbmcgui.Dialog()
	d.ok('Simply Movies','You have not set the default download folder.\nPlease update the addon settings and try again.','','')
	ADDON.openSettings(sys.argv[0])
	downloadFolder = ADDON.getSetting('download_folder')

    if downloadFolder == '' and ADDON.getSetting('ask_folder') == 'true':
        dialog = xbmcgui.Dialog()
	downloadFolder = dialog.browse(3, 'Save to folder...', 'files', '', False, False, downloadFolder)	

    if downloadFolder == '' :
        return None

    filename = title
    ext      = 'mp4'
   
    if ADDON.getSetting('ask_filename') == 'true':
        kb = xbmc.Keyboard(title, 'Save movie as...' )
	kb.doModal()
	if kb.isConfirmed():
	    filename = kb.getText()
	else:
	    return None
    else:
        filename = title

    filename = re.sub('[:\\/*?\<>|"]+', '', filename)
    filename = filename + '.' + ext

    return os.path.join(downloadFolder, filename)


def DOWNLOAD(name, url, iconimage):
    GA('Download', name)
    url = getUrl(url, ADDON.getSetting('download_best'))

    savePath = downloadPath(name)

    if savePath:
        t = str(200*len(savePath))
        xbmc.executebuiltin('XBMC.Notification(' + 'Simply Movies' + ', Downloading: ' + savePath + ',' + t + ')')
        print "Saving %s to %s" % (url, savePath)
        urllib.urlretrieve(url, savePath)


def cleanFilename(filename):
    return re.sub('[:\\/*?\<>|"]+', '', filename)
    
        
def LIBRARY_TV(name,url,iconimage):#  cause mode is empty in this one it will go back to first directory
    link=OPEN_URL(url)
    r='<h3>(.+?)</h3>'
    match=re.compile(r).findall(link)

    foldermain = os.path.join(library, 'TV')
    if not os.path.exists(foldermain):
        os.mkdir(foldermain)

    foldername = os.path.join(foldermain, name)
    if not os.path.exists(foldername):
        os.mkdir(foldername)

    for season in match:
        seasonfolder = os.path.join(foldername, season)
        if not os.path.exists(seasonfolder):
            os.mkdir(seasonfolder)

        _r='<h3>%s</h3>'% season
        print season
        firstsplit=link.split(season)[1]
        secondsplit=firstsplit.split('<h3>')[0]
        r_='<a href="(.+?)">(.+?)</a>'
        match1=re.compile(r_).findall(secondsplit)
        for _url,name_ in match1:
            Theurl = URL+_url
            _name=name_.replace(':','-')

            strm     = '%s?mode=1200&name=%s&url=%s&iconimage=None&trailer=None'% (sys.argv[0], _name,urllib.quote_plus(Theurl))
            _name    = name_.replace(':','-')
            filename = '%sx%s.strm'%(season.replace('Season ',''),_name.replace('Episode ',''))
            filename = cleanFilename(filename)
            file     = os.path.join(seasonfolder,filename)
            print file

            a = open(file, "w")
            a.write(strm)
            a.close()

    
def LIBRARY_MOVIE(name,url,iconimage,trailer):#  cause mode is empty in this one it will go back to first directory
    strm='%s?mode=1200&url=%s&name=%s&iconimage=%s&trailer=%s'% (sys.argv[0],urllib.quote_plus(url), name,iconimage,trailer)
    foldername=os.path.join(library, 'Movies')
    if os.path.exists(foldername)==False:
        os.mkdir(os.path.join(library, 'Movies'))

    filename = str(name) + '.strm'
    filename = cleanFilename(filename)
    file     = os.path.join(foldername,filename)
    print file

    a = open(file, "w")
    a.write(strm)
    a.close()


def validateStream(url):
    try:
        req = urllib2.Request(url)
        req.add_header('Referer', URL)
        resp    = urllib2.urlopen(req)
        #content = int(resp.headers['Content-Length'])
        #type    = resp.headers['Content-Type'] #expect to be 'video/mp4'
        return True
    except Exception, e:
        print "ERROR IN SIMPLY MOVIES: " + str(e)
        return False

def getUrl(url, setting):
    maxQuality = 0
    maxUrl     = ''

    link   = OPEN_URL(url)
    r      = '<iframe class="videoPlayerIframe" src="(.+?)"></iframe>'
    match  = re.compile(r).findall(link)

    link   = OPEN_URL(match[0])
    r      ='url(.+?)=(.+?)&amp'
    match  = re.compile(r).findall(link)

    urlselect  = []
    resolution = []

    for res, url in match:
        if url not in urlselect:
            urlselect.append(url)
        if res not in resolution:
            resolution.append(res)
            value = int(res)
            if value > maxQuality:
                maxQuality = value
                maxUrl     = url

    if setting == 'true':
        url = maxUrl
    else:
        url = urlselect[xbmcgui.Dialog().select('Please Select Resolution', resolution)]    

    print  url
    return url
        
def PLAY_STREAM(name, url, iconimage, strm = False):
    GA('Playing', name)

    url = getUrl(url, ADDON.getSetting('play_best'))
    
    if not validateStream(url):
        dlg = xbmcgui.Dialog()
        dlg.ok('Simply Movies', 'There was a problem trying to play %s' % name, '', 'Please note, some ISPs appear to block Simply Movies :-(')
        return

    req = urllib2.Request(url)
    req.add_header('Referer', URL)
    resp    = urllib2.urlopen(req)
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name} )
    liz.setProperty("IsPlayable","true")
    if not strm:
        pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
        pl.clear()
        pl.add(url, liz)
        xbmc.Player().play(pl)
        return

    liz.setPath(url)
    xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)
    
    
def PLAY_TRAILER(name, url, iconimage, trailer):    
    if not iconimage:
        iconimage = "DefaultVideo.png"
    GA('Trailer',name)
    url = 'plugin://plugin.video.youtube/?path=root/video&action=play_video&videoid=%s' % trailer
    liz=xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name} )
    liz.setProperty("IsPlayable","true")
    pl = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
    pl.clear()
    pl.add(url, liz)
    xbmc.Player().play(pl)

 
def OPEN_URL(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    response = urllib2.urlopen(req)
    link = response.read()
    response.close()
    return link
    
    
def parseDate(dateString):
    try:
        return datetime.datetime.fromtimestamp(time.mktime(time.strptime(dateString.encode('utf-8', 'replace'), "%Y-%m-%d %H:%M:%S")))
    except:
        return datetime.datetime.today() - datetime.timedelta(days = 1) #force update


def checkGA():
    secsInHour = 60 * 60
    threshold  = 2 * secsInHour

    now   = datetime.datetime.today()
    prev  = parseDate(ADDON.getSetting('ga_time'))
    delta = now - prev
    nDays = delta.days
    nSecs = delta.seconds

    doUpdate = (nDays > 0) or (nSecs > threshold)
    if not doUpdate:
        return

    ADDON.setSetting('ga_time', str(now).split('.')[0])
    APP_LAUNCH()    
    
                    
def send_request_to_google_analytics(utm_url):
    ua='Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3'
    import urllib2
    try:
        req = urllib2.Request(utm_url, None,
                                    {'User-Agent':ua}
                                     )
        response = urllib2.urlopen(req).read()
    except:
        print ("GA fail: %s" % utm_url)         
    return response
       

def GA(group,name):
        try:
            try:
                from hashlib import md5
            except:
                from md5 import md5
            from random import randint
            import time
            from urllib import unquote, quote
            from os import environ
            from hashlib import sha1
            VISITOR = ADDON.getSetting('visitor_ga')
            utm_gif_location = "http://www.google-analytics.com/__utm.gif"
            if not group=="None":
                    utm_track = utm_gif_location + "?" + \
                            "utmwv=" + VERSION + \
                            "&utmn=" + str(randint(0, 0x7fffffff)) + \
                            "&utmt=" + "event" + \
                            "&utme="+ quote("5("+PATH+"*"+group+"*"+name+")")+\
                            "&utmp=" + quote(PATH) + \
                            "&utmac=" + UATRACK + \
                            "&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR,VISITOR,"2"])
                    try:
                        print "============================ POSTING TRACK EVENT ============================"
                        send_request_to_google_analytics(utm_track)
                    except:
                        print "============================  CANNOT POST TRACK EVENT ============================" 
            if name=="None":
                    utm_url = utm_gif_location + "?" + \
                            "utmwv=" + VERSION + \
                            "&utmn=" + str(randint(0, 0x7fffffff)) + \
                            "&utmp=" + quote(PATH) + \
                            "&utmac=" + UATRACK + \
                            "&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR, VISITOR,"2"])
            else:
                if group=="None":
                       utm_url = utm_gif_location + "?" + \
                                "utmwv=" + VERSION + \
                                "&utmn=" + str(randint(0, 0x7fffffff)) + \
                                "&utmp=" + quote(PATH+"/"+name) + \
                                "&utmac=" + UATRACK + \
                                "&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR, VISITOR,"2"])
                else:
                       utm_url = utm_gif_location + "?" + \
                                "utmwv=" + VERSION + \
                                "&utmn=" + str(randint(0, 0x7fffffff)) + \
                                "&utmp=" + quote(PATH+"/"+group+"/"+name) + \
                                "&utmac=" + UATRACK + \
                                "&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR, VISITOR,"2"])
                                
            print "============================ POSTING ANALYTICS ============================"
            send_request_to_google_analytics(utm_url)
            
        except:
            print "================  CANNOT POST TO ANALYTICS  ================" 
            
            
def APP_LAUNCH():
        versionNumber = int(xbmc.getInfoLabel("System.BuildVersion" )[0:2])
        if versionNumber < 12:
            if xbmc.getCondVisibility('system.platform.osx'):
                if xbmc.getCondVisibility('system.platform.atv2'):
                    log_path = '/var/mobile/Library/Preferences'
                else:
                    log_path = os.path.join(os.path.expanduser('~'), 'Library/Logs')
            elif xbmc.getCondVisibility('system.platform.ios'):
                log_path = '/var/mobile/Library/Preferences'
            elif xbmc.getCondVisibility('system.platform.windows'):
                log_path = xbmc.translatePath('special://home')
                log = os.path.join(log_path, 'xbmc.log')
                logfile = open(log, 'r').read()
            elif xbmc.getCondVisibility('system.platform.linux'):
                log_path = xbmc.translatePath('special://home/temp')
            else:
                log_path = xbmc.translatePath('special://logpath')
            log = os.path.join(log_path, 'xbmc.log')
            logfile = open(log, 'r').read()
            match=re.compile('Starting XBMC \((.+?) Git:.+?Platform: (.+?)\. Built.+?').findall(logfile)
        elif versionNumber > 11:
            print '======================= more than ===================='
            log_path = xbmc.translatePath('special://logpath')
            log = os.path.join(log_path, 'xbmc.log')
            logfile = open(log, 'r').read()
            match=re.compile('Starting XBMC \((.+?) Git:.+?Platform: (.+?)\. Built.+?').findall(logfile)
        else:
            logfile='Starting XBMC (Unknown Git:.+?Platform: Unknown. Built.+?'
            match=re.compile('Starting XBMC \((.+?) Git:.+?Platform: (.+?)\. Built.+?').findall(logfile)
        print '==========================   '+PATH+' '+VERSION+'  =========================='
        try:
            from hashlib import md5
        except:
            from md5 import md5
        from random import randint
        import time
        from urllib import unquote, quote
        from os import environ
        from hashlib import sha1
        import platform
        VISITOR = ADDON.getSetting('visitor_ga')
        for build, PLATFORM in match:
            if re.search('12',build[0:2],re.IGNORECASE): 
                build="Frodo" 
            if re.search('11',build[0:2],re.IGNORECASE): 
                build="Eden" 
            if re.search('13',build[0:2],re.IGNORECASE): 
                build="Gotham" 
            print build
            print PLATFORM
            utm_gif_location = "http://www.google-analytics.com/__utm.gif"
            utm_track = utm_gif_location + "?" + \
                    "utmwv=" + VERSION + \
                    "&utmn=" + str(randint(0, 0x7fffffff)) + \
                    "&utmt=" + "event" + \
                    "&utme="+ quote("5(APP LAUNCH*"+build+"*"+PLATFORM+")")+\
                    "&utmp=" + quote(PATH) + \
                    "&utmac=" + UATRACK + \
                    "&utmcc=__utma=%s" % ".".join(["1", VISITOR, VISITOR, VISITOR,VISITOR,"2"])
            try:
                print "============================ POSTING APP LAUNCH TRACK EVENT ============================"
                send_request_to_google_analytics(utm_track)
            except:
                print "============================  CANNOT POST APP LAUNCH TRACK EVENT ============================" 
             
   
class HUB( xbmcgui.WindowXMLDialog ): # The call MUST be below the xbmcplugin.endOfDirectory(int(sys.argv[1])) or the dialog box will be visible over the pop-up.
    def __init__( self, *args, **kwargs ):
        self.shut = kwargs['close_time'] 
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        xbmc.executebuiltin( "Skin.SetBool(AnimeWindowXMLDialogClose)" )
                                       
    def onInit( self ):
        xbmc.Player().play('%s/resources/skins/DefaultSkin/media/xbmchub.mp3'%ADDON.getAddonInfo('path'))# Music.
        while self.shut > 0:
            xbmc.sleep(1000)
            self.shut -= 1
        xbmc.Player().stop()
        self._close_dialog()
                
    def onFocus( self, controlID ): pass
    
    def onClick( self, controlID ): 
        if controlID==12:
            xbmc.Player().stop()
            self._close_dialog()

    def onAction( self, action ):
        if action in [ 5, 6, 7, 9, 10, 92, 117 ] or action.getButtonCode() in [ 275, 257, 261 ]:
            xbmc.Player().stop()
            self._close_dialog()

    def _close_dialog( self ):
        xbmc.executebuiltin( "Skin.Reset(AnimeWindowXMLDialogClose)" )
        time.sleep( .4 )
        self.close()

             
def pop():# Added Close_time for window auto-close length.....
    if xbmc.getCondVisibility('system.platform.ios'):
        if not xbmc.getCondVisibility('system.platform.atv'):
            popup = HUB('hub1.xml',ADDON.getAddonInfo('path'),'DefaultSkin',close_time=34,logo_path='%s/resources/skins/DefaultSkin/media/Logo/'%ADDON.getAddonInfo('path'))
    elif xbmc.getCondVisibility('system.platform.android'):
        popup = HUB('hub1.xml',ADDON.getAddonInfo('path'),'DefaultSkin',close_time=34,logo_path='%s/resources/skins/DefaultSkin/media/Logo/'%ADDON.getAddonInfo('path'))
    else:
        popup = HUB('hub.xml',ADDON.getAddonInfo('path'),'DefaultSkin',close_time=34,logo_path='%s/resources/skins/DefaultSkin/media/Logo/'%ADDON.getAddonInfo('path'))
    
    popup.doModal()
    del popup
                
def checkdate(dateString):
    try:
        return datetime.datetime.fromtimestamp(time.mktime(time.strptime(dateString.encode('utf-8', 'replace'), "%Y-%m-%d %H:%M:%S")))
    except:
        return datetime.datetime.today() - datetime.timedelta(days = 1000) #force update


def check_popup():

    threshold  = 120

    now   = datetime.datetime.today()
    prev  = checkdate(ADDON.getSetting('pop_time'))
    delta = now - prev
    nDays = delta.days

    doUpdate = (nDays > threshold)
    if not doUpdate:
        return

    ADDON.setSetting('pop_time', str(now).split('.')[0])
    pop()
     
checkGA()
    
    
def get_params():
        param=[]
        paramstring=sys.argv[2]
        if len(paramstring)>=2:
                params=sys.argv[2]
                cleanedparams=params.replace('?','')
                if (params[len(params)-1]=='/'):
                        params=params[0:len(params)-2]
                pairsofparams=cleanedparams.split('&')
                param={}
                for i in range(len(pairsofparams)):
                        splitparams={}
                        splitparams=pairsofparams[i].split('=')
                        if (len(splitparams))==2:
                                param[splitparams[0]]=splitparams[1]
                                
        return param

# this is the listing of the items        
def addDir(name, url, mode, iconimage, trailer=''):
        u  = sys.argv[0]
        u += "?url="       + urllib.quote_plus(url)
        u += "&mode="      + str(mode)
        u += "&name="      + urllib.quote_plus(name)
        u += "&iconimage=" + urllib.quote_plus(iconimage)
        u += "&trailer="   + urllib.quote_plus(trailer)

        liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
        liz.setInfo( type="Video", infoLabels={ "Title": name} )

        menu=[]
        if mode==200 or mode==201:
            if trailer != '':
                menu.append(('Play Trailer','XBMC.RunPlugin(%s?mode=201&url=None&name=%s&iconimage=%s&trailer=%s)'% (sys.argv[0], name,iconimage,trailer)))
            menu.append(('Download','XBMC.RunPlugin(%s?mode=1000&url=%s&name=%s&iconimage=%s&trailer=%s)'% (sys.argv[0], urllib.quote_plus(url), name, iconimage, trailer)))
            if 'movie.php' in url:
                menu.append(('Add To Library','XBMC.RunPlugin(%s?mode=2000&name=%s&url=%s&iconimage=%s&trailer=%s)'% (sys.argv[0], name,urllib.quote_plus(url), iconimage, trailer)))
            liz.addContextMenuItems(items=menu, replaceItems=False)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz, isFolder=False)
        else:
            if mode==3:
                menu.append(('Add To Library','XBMC.RunPlugin(%s?mode=2001&name=%s&url=%s&iconimage=%s)'% (sys.argv[0], name,urllib.quote_plus(url),  iconimage)))
                liz.addContextMenuItems(items=menu, replaceItems=False)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]),url=u,listitem=liz, isFolder=True)

        
#same as above but this is addlink this is where you pass your playable content so you dont use addDir you use addLink "url" is always the playable content         
def addLink(name, url, iconimage, trailer):
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo( type="Video", infoLabels={ "Title": name} )
    liz.setProperty("IsPlayable","true")
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz, isFolder=False)


def addMore(more, mode, page, search = '', genre = ''):
    if more < int(ADDON.getSetting('results')):
        return

    u =  sys.argv[0]

    u += "?url="  + str('url')
    u += "&mode=" + str(mode)
    u += "&page=" + str(page)

    if search != '':
        u += "&search=" + urllib.quote_plus(search)

    if genre != '':
        u += "&genre=" + urllib.quote_plus(genre)    

    liz = xbmcgui.ListItem(' More...', iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")

    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
 
        
#below tells plugin about the views                
def setView(content, viewType):
    # set content type so library shows more views and info
    if content:
        xbmcplugin.setContent(int(sys.argv[1]), content)
    if ADDON.getSetting('auto-view') == 'true':#<<<----see here if auto-view is enabled(true) 
        xbmc.executebuiltin("Container.SetViewMode(%s)" % ADDON.getSetting(viewType) )#<<<-----then get the view type
                      
               
params=get_params()
url       = None
name      = None
mode      = None
iconimage = None
trailer   = None

genre     = None
search    = None
page      = 0


try:
        url=urllib.unquote_plus(params["url"])
except:
        pass
try:
        name=urllib.unquote_plus(params["name"])
except:
        pass
try:
        iconimage=urllib.unquote_plus(params["iconimage"])
except:
        pass
try:        
        mode=int(params["mode"])
except:
        pass
try:        
        trailer=urllib.unquote_plus(params["trailer"])
except:
        pass
try:        
        page=int(params["page"])
except:
        pass
try:        
        genre=urllib.unquote_plus(params["genre"])
except:
        pass
try:        
        search=urllib.unquote_plus(params["search"])
except:
        pass

print "Mode: "      + str(mode)
print "URL: "       + str(url)
print "Name: "      + str(name)
print "IconImage: " + str(iconimage)
   
        
#these are the modes which tells the plugin where to go
if mode==None or url==None or len(url)<1:
        print ""
        CATEGORIES()
        
elif mode==2:
        choose_search()
       
elif mode==1:
        print page
        main(page)
        
elif mode==3:
        get_episodes(name,url,iconimage)
        
elif mode==4:
        search_tv(page, search)
        
elif mode==5:
        search_movies(page, search)
        
elif mode==6:
        genre_movie(page, genre)
        
elif mode==7:
        genre_tv(page, genre)
        
elif mode==200:
        PLAY_STREAM(name,url,iconimage,False)

elif mode==1200:
        PLAY_STREAM(name,url,iconimage,True)
        
elif mode==201:
        PLAY_TRAILER(name,url,iconimage,trailer)
        
elif mode==1000:
        DOWNLOAD(name,url,iconimage)
        
elif mode==2000:
        LIBRARY_MOVIE(name,url,iconimage,trailer)
elif mode==2001:
        LIBRARY_TV(name,url,iconimage)
        
xbmcplugin.endOfDirectory(int(sys.argv[1]))
check_popup()
