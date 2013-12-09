# coding:Cp1252
from datetime import datetime

import mediaitem
import chn_class
from logger import Logger


class Channel(chn_class.Channel):
    """
    main class from which all channels inherit
    """

    def InitialiseVariables(self, channelInfo):
        """Used for the initialisation of user defined parameters.

        All should be present, but can be adjusted. If overridden by derived class
        first call chn_class.Channel.InitialiseVariables(self, channelInfo) to make sure all
        variables are initialised.

        Arguments:
        channelInfo : ChannelInfo - The channel meta data.

        Returns:
        True if OK

        """

        # call base function first to ensure all variables are there
        chn_class.Channel.InitialiseVariables(self, channelInfo)

        self.noImage = "vtmimage.png"
        self.mainListUri = "http://nieuws.vtm.be/herbekijk"
        self.baseUrl = "http://nieuws.vtm.be"

        self.episodeItemRegex = '<li class="menu[^"]*"><a href="/([^l4"][^"]+)"[^>]+>([^>]+)</a></li>'
        self.videoItemRegex = 'is-video">\W+<a[^>]+>(?:<img src="([^"]+/videocms/image/)(\d+)([^"]+)"[^>]+></a>\W+</div>\W+){0,1}<div[^>]+>([^<]+)</div>\W+<h3 class="pagemanager-item-title">\W*<span>\W*<a href="/([^"]+)">([^<]+)'
        self.mediaUrlRegex = '<meta itemprop="embedURL" content="([^"]+)" />'
        self.pageNavigationRegex = ''
        self.pageNavigationRegexIndex = 0

        self.contextMenuItems = []
        # self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using Mplayer", "CtMnPlayMplayer", itemTypes="video", completeStatus=True))
        # self.contextMenuItems.append(contextmenu.ContextMenuItem("Play using DVDPlayer", "CtMnPlayDVDPlayer", itemTypes="video", completeStatus=True))
        return True

    def CreateEpisodeItem(self, resultSet):
        """Creates a new MediaItem for an episode

        Arguments:
        resultSet : list[string] - the resultSet of the self.episodeItemRegex

        Returns:
        A new MediaItem of type 'folder'

        This method creates a new MediaItem from the Regular Expression or Json
        results <resultSet>. The method should be implemented by derived classes
        and are specific to the channel.

        """

        # dummy class
        item = mediaitem.MediaItem(resultSet[1], "%s/%s" % (self.baseUrl, resultSet[0]))
        item.complete = True
        item.icon = self.icon
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
        thumbUrl = "%s%s%s" % (resultSet[0], resultSet[1], resultSet[2])
        year = resultSet[1]
        dayOrTime = resultSet[3]
        url = resultSet[4]
        title = resultSet[5]

        item = mediaitem.MediaItem(title, "%s/%s" % (self.baseUrl, url))
        item.type = 'video'

        item.thumb = self.noImage
        if thumbUrl:
            item.thumbUrl = thumbUrl
        item.icon = self.icon

        if "/" in dayOrTime and year:
            # date found
            (day, month) = dayOrTime.split("/")
            item.SetDate(year, month, day, 0, 0, 0)
        elif "." in dayOrTime:
            # time found for today
            date = datetime.now()
            day = date.day
            month = date.month
            year = date.year
            (hour, minutes) = dayOrTime.split(".")
            item.SetDate(year, month, day, hour, minutes, 0)
        else:
            Logger.Warning("Could not determine date for item '%s' with datestring='%s'", title, dayOrTime)

        item.complete = False
        return item

#     def ParseMainList(self, returnData=False):
#         """Parses the mainlist of the channel and returns a list of MediaItems
#
#         This method creates a list of MediaItems that represent all the different
#         programs that are available in the online source. The list is used to fill
#         the ProgWindow.
#
#         Keyword parameters:
#         returnData : [opt] boolean - If set to true, it will return the retrieved
#                                      data as well
#
#         Returns a list of MediaItems that were retrieved.
#
#         """
#
#         if len(self.mainListItems) == 0:
#             # create the items
#             items = []
#             for days in range(0, 3):
#                 date = datetime.now() - timedelta(days=days)
#                 streamPath = date.strftime("%Y%m%d")
#                 if days == 0:
#                     name = date.strftime("Vandaag")
#                 elif days == 1:
#                     name = date.strftime("Gisteren")
#                 else:
#                     name = date.strftime("Eergisteren")
#                 item = mediaitem.MediaItem(name, streamPath)
#                 item.thumb = self.noImage
#                 item.icon = self.icon
#                 item.complete = True
#                 item.SetDate(date.year, date.month, date.day)
#
#                 # now add the subitems
#                 for episode in (13, 19):
#                     title = "Nieuws van %s:00 uur" % (episode,)
#
#                     # only add if it is available
#                     broadCastDateTime = date - timedelta(hours=date.hour, minutes=date.minute, seconds=date.second, microseconds=date.microsecond) + timedelta(hours=episode)
#                     if broadCastDateTime > datetime.now():
#                         # future broadcast
#                         Logger.Debug("Future broadcast found: %s @ %s", title, broadCastDateTime)
#                         continue
#
#                     url = "http://streaming.vtm.be/VTM/agility/%s_hn%s.wmv" % (streamPath, episode)
#                     episodeItem = mediaitem.MediaItem(title, url, type='video')
#                     episodeItem.icon = self.icon
#                     episodeItem.thumb = self.noImage
#                     episodeItem.complete = False
#                     # episodeItem.AppendSingleStream(url)
#                     episodeItem.SetDate(date.year, date.month, date.day, episode, 0, 0)
#                     item.items.append(episodeItem)
#
#                 if len(item.items) > 0:
#                     items.append(item)
#                 else:
#                     Logger.Info("No items found for: '%s'", name)
#
#             # set the mainlist items and then call the chn_class ParseMainlist for
#             # sorting and stuff
#             self.mainListItems = items
#
#         return chn_class.Channel.ParseMainList(self, returnData=returnData)
