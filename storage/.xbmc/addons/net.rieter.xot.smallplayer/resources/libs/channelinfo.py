#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================

#===============================================================================
# Import the default modules
#===============================================================================
import os
# import xml.dom.minidom
import sys
import re

import xbmcgui

from environments import Environments
from helpers.htmlentityhelper import HtmlEntityHelper
from config import Config
from logger import Logger


class ChannelInfo:
    __channelInfoRegex = re.compile('<channel>\W+<guid>(?P<guid>[^<]+)</guid>\W+<name>(?P<name>[^<]+)</name>\W+<description>(?P<description>[^<]+)</description>\W+<icon>(?P<icon>[^<]+)</icon>\W+<iconlarge>(?P<iconlarge>[^<]+)</iconlarge>\W+(?:<category>(?P<category>[^<]+)</category>)?\W+(?:<channelcode>(?P<channelcode>[^<]+)</channelcode>)?\W+(?:<sortorder>(?P<sortorder>[^<]+)</sortorder>)?\W+(?:<language>(?P<language>[^<]+)</language>)?\W+(?:<compatible>(?P<compatible>[^<]+)</compatible>)?\W+(?:<message>(?P<message>[^<]+)</message>)?\W+<', re.DOTALL + re.IGNORECASE)

    def __init__(self, guid, name, description, icon, iconLarge, category, path, channelCode=None, sortOrder=255, language=None, compatiblePlatforms=Environments.All):
        """ Creates a ChannelInfo object with basic information for a channel

        Arguments:
        guid        : String - A unique GUID
        name        : String - The channel name
        description : String - The channel description
        icon        : String - Name of the icon
        iconLarge   : String - Name of the high resolution icon
        path        : String - Path of the channel

        Keyword Arguments:
        channelCode         : String       - A code that distinguishes a channel
                                             within a module. Default is None
        sortOrder           : Int          - The sortorder (0-255). Default is 255
        language            : String       - The language of the channel. Default is None
        compatiblePlatforms : Environments - The supported platforms. Default is Environments.All

        """

        # create method shortcuts for common used methods
        self.ospathjoin = os.path.join

        # set the path info
        self.path = os.path.dirname(path)
        self.moduleName = os.path.splitext(os.path.basename(path))[0]

        self.guid = guid

        self.icon = self.__GetImagePath(icon)
        self.iconLarge = self.__GetImagePath(iconLarge)
        self.category = category

        self.channelName = name
        self.channelCode = channelCode
        self.channelDescription = description

        self.compatiblePlatforms = compatiblePlatforms
        self.sortOrder = sortOrder  # max 255 channels

        self.language = language

        self.firstTimeMessage = None

        return

    def GetChannel(self):
        """ Instantiates a channel from a ChannelInfo object """

        Logger.Trace("Importing module %s from path %s", self.moduleName, self.path)

        sys.path.append(self.path)
        exec ("import %s" % (self.moduleName,))

        channelCommand = '%s.Channel(self)' % (self.moduleName,)
        try:
            Logger.Trace("Running command: %s", channelCommand)
            channel = eval(channelCommand)
        except:
            Logger.Error("Cannot Create channel for %s", self, exc_info=True)
            return None
        return channel

    def GetXBMCItem(self):
        """ Creates an Xbmc ListItem object for this channel """

        name = HtmlEntityHelper.ConvertHTMLEntities(self.channelName)
        description = HtmlEntityHelper.ConvertHTMLEntities(self.channelDescription)

        item = xbmcgui.ListItem(name, description, self.icon, self.iconLarge)
        item.setInfo("video", {"tracknumber": self.sortOrder, "Tagline": description, "Plot": description})
        return item

    def __str__(self):
        """Returns a string representation of the current channel."""

        if self.channelCode is None:
            return "%s [%s, %s, %s] (Order: %s)" % (self.channelName, self.language, self.category, self.guid, self.sortOrder)
        else:
            return "%s (%s) [%s, %s, %s] (Order: %s)" % (self.channelName, self.channelCode, self.language, self.category, self.guid, self.sortOrder)

    def __repr__(self):
        """ Technical representation """

        return "%s @ %s\nmoduleName: %s\nicon: %s\ncompatiblePlatforms: %s" % (self, self.path, self.moduleName, self.icon, self.compatiblePlatforms)

    def __eq__(self, other):
        """Compares to channel objects for equality

        Arguments:
        other : Channel - the other channel to compare to

        The comparison is based only on the self.guid of the channels.

        """

        if other is None:
            return False

        return self.guid == other.guid

    def __cmp__(self, other):
        """Compares to channels

        Arguments:
        other : Channel - the other channel to compare to

        Returns:
        The return value is negative if self < other, zero if self == other and strictly positive if self > other

        """

        if other is None:
            return 1

        compVal = cmp(self.sortOrder, other.sortOrder)
        if compVal == 0:
            compVal = cmp(self.channelName, other.channelName)

        return compVal

    def __GetImagePath(self, image):
        """ Tries to determine the path of an image

        Arguments:
        image : String - The filename (not path) of the image

        Returns the path of the image. In case of a XBMC skin image it will
        return just the filename, else the full path.

        Duplicate code for GuiController.GetImageLocation, but we need to travel
        light here due to speed, so no unwanted imports.

        """

        skinPath = self.ospathjoin(Config.rootDir, "resources", "skins", Config.skinFolder, "media", image)
        if os.path.exists(skinPath):
            return image
        else:
            return self.ospathjoin(self.path, image)

    @staticmethod
    def FromFile(path):
        """ reads the ChannelInfo from a XML file

        Arguments:
        path : String - The path of the XML file.

        """

        xmlFile = open(path)
        xmlData = xmlFile.read()
        xmlFile.close()

        # we re-use the compile Regex from the constant, much faster
        # than re-doing it each time.
        it = ChannelInfo.__channelInfoRegex.finditer(xmlData)
        channels = map(lambda x: x.groupdict(), it)

        # double check
        channelTagCount = xmlData.count("<channel>")
        if channelTagCount != len(channels):
            Logger.Warning("Inconsistant ChannelInfo Regex match with <channel> tags")

        channelInfos = []
        for channel in channels:
            # retrieve the base info
            guid = ChannelInfo.__GetText(channel, "guid")
            name = ChannelInfo.__GetText(channel, "name")
            description = ChannelInfo.__GetText(channel, "description")
            icon = ChannelInfo.__GetText(channel, "icon")
            iconLarge = ChannelInfo.__GetText(channel, "iconlarge")
            channelCode = ChannelInfo.__GetText(channel, "channelcode")
            if channelCode == "None":
                channelCode = None

            category = ChannelInfo.__GetText(channel, "category")
            if not category:
                category = "None"

            sortOrder = ChannelInfo.__GetText(channel, "sortorder")
            if sortOrder:
                sortOrder = int(sortOrder)
            else:
                sortOrder = 255

            # convert the language
            language = ChannelInfo.__GetText(channel, "language")
            if language == "None":
                language = None

            # get the compatible platforms
            compatiblePlatforms = ChannelInfo.__GetText(channel, "compatible")
            if not compatiblePlatforms:
                compatiblePlatforms = Environments.All
            else:
                compatiblePlatforms = eval(compatiblePlatforms)

            channelInfo = ChannelInfo(guid, name, description, icon, iconLarge, category, path, channelCode, sortOrder, language, compatiblePlatforms)
            channelInfo.firstTimeMessage = ChannelInfo.__GetText(channel, "message")

            channelInfos.append(channelInfo)

        return channelInfos

    @staticmethod
    def __GetText(channel, name):
        """ retrieves the text from a XML node with a specific Name

        Arguments:
        parent : XML Element - The element to search
        name   : String      - The name to search for

        Returns an Byte Encoded string

        """
        text = channel[name]
        if not text:
            return text

        return text

if __name__ == "__main__":
    ci = ChannelInfo("",
                     "",
                     "",
                     "offloneicon.png",
                     "offlinelarge.png",
                     "Geen",
                     __file__,
                     None,
                     - 1,
                     None,
                     Environments.All)
    print ci
    print repr(ci)
