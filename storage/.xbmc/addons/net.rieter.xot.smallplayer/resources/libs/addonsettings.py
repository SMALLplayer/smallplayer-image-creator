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

#===============================================================================
# Make global object available
#===============================================================================
from logger import Logger        # this has not further references
from proxyinfo import ProxyInfo  # this has not further references
from config import Config        # this has not further references


class AddonSettings:
    """Class for retrieving XBMC Addon settings"""

    # these are static properties that store the settings. Creating them each time is causing major slow-down
    __settings = None
    __isPlugin = False

    def __init__(self, *args, **kwargs):  # @UnusedVariables
        """Initialisation of the AddonSettings class.

        Arguments:
        args   : list - List of arguments

        Keyword Arguments:
        kwargs : list - List of keyword arguments

        """

        #===============================================================================
        # Configuration ID's
        #===============================================================================
        self.STREAM_QUALITY = "stream_quality"
        self.NUMBER_OF_PAGES = "number_of_first_pages"
        self.SORTING_ALGORITHM = "sorting_algorithm"
        self.STREAM_BITRATE = "stream_bitrate"
        self.SUBTITLE_MODE = "subtitle_mode"
        self.CACHE_ENABLED = "http_cache"
        self.BACKGROUND_CHANNELS = "background_channels"
        self.BACKGROUND_PROGRAMS = "background_programs"
        self.CHANNEL_SETTINGS_PATTERN = "channel_%s_visible"
        self.FOLDER_PREFIX = "folder_prefix"
        self.HIDE_GEOLOCKED = "hide_geolocked"
        self.LOG_LEVEL = "log_level"
        self.UZG_CACHE = "uzg_cache"
        self.UZG_CACHE_PATH = "uzg_cache_path"
        self.SEND_STATISTICS = "send_statistics"

        if AddonSettings.__settings == None:
            self.__LoadSettings()

        return

    @staticmethod
    def ClearCachedAddonSettingsObject():
        """ Clears the cached add-on settings. This will force a reload for the next INSTANCE
        of an AddonSettings class. """

        AddonSettings.__settings = None

    @staticmethod
    def SetPluginMode(pluginMode):
        """ Sets PluginMode to "pluginMode" and makes this value
        available via the GetPluginMode() methode

        Arguments:
        pluginMode : Boolean - Set to true for plugins

        """

        AddonSettings.__isPlugin = pluginMode

    @staticmethod
    def GetPluginMode():
        """ returns True if in pluginmode """

        return AddonSettings.__isPlugin

    def HideGeoLocked(self):
        """ Returs the config value that indicates of GeoLocked
        items should be hidden.

        """
        return self.__GetBooleanSetting(self.HIDE_GEOLOCKED)

    def GetLocalizedString(self, stringId):
        """ returns a localized string for this id

        Arguments:
        stringId - int - The ID for the string

        """

        return AddonSettings.__settings.getLocalizedString(stringId)

    def SendUsageStatistics(self):
        """ returns true if the user allows usage statistics sending """

        return self.__GetBooleanSetting(self.SEND_STATISTICS)

    def UpdateAddOnSettingsWithChannels(self, channels, config):
        """ updats the settings.xml to include all the channels


        Arguments:
        channels : List<channels> - The channels to add to the settings.xml
        config   : Config         - The configuration object

        """

        # First we create a new bit of settings file.
        newXml = '    <!-- start of channel selection -->\n    <category label="30040">\n'
        channels.sort(lambda x, y: self.__SortChannels(x, y))

        relativeCount = 2   # used to refer to the main language setting
        lastLanguage = ""
        for channel in channels:
            name = channel.channelName
            if not lastLanguage == channel.language:
                # add the first items, that disables the complet language and some seperators
                lastLanguage = channel.language
                (settingsId, label) = self.__GetLanguageSettingsIdAndLabel(channel.language)
                relativeCount = 2

                # add the items
                newXml = '%s        <setting type="lsep" label="%s" />\n' % (newXml, label)
                newXml = '%s        <setting id="%s" type="bool" label="30042" default="true" />\n' % (newXml, settingsId)
                newXml = '%s        <setting type="sep" />\n' % (newXml,)
            else:
                relativeCount = relativeCount + 1

            # bugfix for XBMC commit 423b972
#            if name[0] in "0123456789":
#                name = "-%s" % (name,)

            newXml = '%s        <setting id="%s" type="bool" label="- %s" default="true" visible="eq(-%s,True)" />\n' % (newXml, self.CHANNEL_SETTINGS_PATTERN % (channel.guid,), name, relativeCount)

        newXml = '%s    </category>' % (newXml)

        # Then we read the original file
        filenameTemplate = os.path.join(config.rootDir, "resources", "settings_template.xml")
        settingsXml = open(filenameTemplate, "r")
        contents = settingsXml.read()
        # Logger.Trace(contents)
        settingsXml.close()

        if ("<!-- start of channel selection -->" not in contents):
            Logger.Error("No '<!-- start of channel selection -->' found in settings.xml. Stopping updating.")
            return

        # Finally we insert the new XML into the old one
        try:
            begin = contents[:contents.find('<!-- start of channel selection -->')].strip()
            end = contents[contents.find('<!-- end of channel selection -->'):].strip()
            newContents = "%s\n    \n%s\n    %s" % (begin, newXml, end)
            Logger.Trace(newContents)
            filename = os.path.join(config.rootDir, "resources", "settings.xml")
            settingsXml = open(filename, "w+")
            settingsXml.write(newContents)
            settingsXml.close()
        except:
            Logger.Error("Something went wrong trying to update the settings.xml", exc_info=True)
            try:
                settingsXml.close()
            except:
                pass
            # restore original settings
            settingsXml = open(filename, "w+")
            settingsXml.write(contents)
            settingsXml.close()
            return

        Logger.Info("Settings.xml updated succesfully. Reloading settings.")
        self.__LoadSettings()
        return

    def CacheHttpResponses(self):
        """ Returns True if the HTTP responses need to be cached """

        return self.__GetBooleanSetting(self.CACHE_ENABLED)

    def GetDimPercentage(self):
        """ Returns the colordiffuse setting for the background dimmer"""

        try:
            setting = self.__GetSetting("dim_background")

            decValue = int(setting)
            decValue = int(decValue * 1.0 / 100 * 254) + 1
            if decValue == 1:
                decValue = 0
        except:
            decValue = 0

        hexValue = hex(decValue)
        return "%sffffff" % (hexValue[2:])

    def GetMaxStreamBitrate(self):
        """Returns the maximum bitrate (kbps) for streams specified by the user"""

        setting = self.__GetSetting(self.STREAM_BITRATE)
        return int(setting)

    def GetFolderPrefix(self):
        """ returns the folder prefix """

        setting = self.__GetSetting(self.FOLDER_PREFIX)
        return setting

    def UseSubtitle(self):
        """Returns whether to show subtitles or not"""

        setting = self.__GetSetting(self.SUBTITLE_MODE)

        if setting == "0":
            return True
        else:
            return False

    def BackgroundImageChannels(self):
        """Returns the filename or path for the background of the
        program overview.
        """

        setting = self.__GetSetting(self.BACKGROUND_CHANNELS)
        return setting

    def BackgroundImageProgram(self):
        """Returns the filename or path for the background of the
        channel overview
        """

        setting = self.__GetSetting(self.BACKGROUND_PROGRAMS)
        return setting

    def GetSortAlgorithm(self):
        """Retrieves the sorting mechanism from the settings

        Returns:
         * date - If sorting should be based on timestamps
         * name - If sorting should be based on names

        """

        setting = self.__GetSetting(self.SORTING_ALGORITHM)
        if setting == "0":
            return "name"
        elif setting == "1":
            return "date"
        else:
            return "none"

    def GetIPlayerProxy(self):
        """Returns the proxy server and port for iPlayer access"""

        server = self.__GetSetting("uk_proxy_server")
        if server == "":
            return None

        port = self.__GetSetting("uk_proxy_port")

        username = self.__GetSetting("uk_proxy_username")
        password = self.__GetSetting("uk_proxy_password")
        return ProxyInfo(server, port, username=username, password=password)

    def GetUzgCacheDuration(self):
        """ Returns the UZG cache duration """

        cacheTime = self.__GetSetting(self.UZG_CACHE)
        if (cacheTime.lower() == "true"):
            # kept for backwards compatibility
            cacheTime = 5
        elif (cacheTime.lower() == "false"):
            # kept for backwards compatibility
            cacheTime = 0
        else:
            cacheTime = int(cacheTime)

        return cacheTime

    def GetUzgCachePath(self):
        """ returns the cachepath for UZG or None if not set """

        path = self.__GetSetting(self.UZG_CACHE_PATH)
        if path.startswith("smb://"):
            path = path.replace("smb://", "\\\\").replace("/", "\\")
        return path

    def GetLogLevel(self):
        """ Returns True if the add-on should do trace logging """

        level = self.__GetSetting(self.LOG_LEVEL)
        if level == "":
            return 10

        # the return value is zero based. 0 -> Trace , 1=Debug (10), 2 -> Info (20)
        return int(self.__GetSetting(self.LOG_LEVEL)) * 10

    def ShowChannel(self, channel):
        """Check if the channel should be shown

        Arguments:
        channel : Channel - The channel to check.

        """

        settingId = self.CHANNEL_SETTINGS_PATTERN % (channel.guid)
        setting = self.__GetSetting(settingId)

        if setting == "":
            return True
        else:
            return setting == "true"

        return

    def GetMaxNumberOfPages(self):
        """Returns the configured maximum number for pages to parse for
        the mainlist.

        """

        return int(self.__GetSetting(self.NUMBER_OF_PAGES))

    def ShowSettings(self):
        """Shows the settings dialog"""

        # __language__ = __settings__.getLocalizedString
        # __language__(30204)              # this will return localized string from resources/language/<name_of_language>/strings.xml
        # __settings__.getSetting( "foo" ) # this will return "foo" setting value
        # __settings__.setSetting( "foo" ) # this will set "foo" setting value
        AddonSettings.__settings.openSettings()      # this will open settings window
        self.GetMaxStreamBitrate()
        self.GetMaxNumberOfPages()

        # clear the cache because stuff might have chanced
        Logger.Info("Clearing Settings cache because settings dialog was shown.")
        return

    def ShowChannelWithLanguage(self, languageCode):
        """Checks if the channel with a certain languageCode should be loaded.

        Arguments:
        languageCode : string - one of these language strings:
                                 * nl    - Dutch
                                 * se    - Swedish
                                 * lt    - Lithuanian
                                 * lv    - Latvian
                                 * ca-fr - French Canadian
                                 * ca-en - English Canadian
                                 * be    - Belgium
                                 * en-gb - British
                                 * ee    - Estonia
                                 * dk    - Danish
                                 * None  - Other languages

        Returns:
        True if the channels should be shown. If the lookup does not match
        a NotImplementedError is thrown.

        """
        (settingsId, settingsLabel) = self.__GetLanguageSettingsIdAndLabel(languageCode)  # @UnusedVariables
        return self.__GetSetting(settingsId) == "true"

    def __GetLanguageSettingsIdAndLabel(self, languageCode):
        """ returns the settings xml part for this language

        Arguments:
        languageCode - String - The language string

        Returns:
        A tupple with the label and the settingsId.

        """

        if languageCode == "nl":
            return ("show_dutch", 30005)
        elif languageCode == "se":
            return ("show_swedish", 30006)
        elif languageCode == "lt":
            return ("show_lithuanian", 30007)
        elif languageCode == "lv":
            return ("show_latvian", 30008)
        elif languageCode == "ca-fr":
            return ("show_cafr", 30013)
        elif languageCode == "ca-en":
            return ("show_caen", 30014)
        elif languageCode == "en-gb":
            return ("show_engb", 30027)
        elif languageCode == "no":
            return ("show_norwegian", 30015)
        elif languageCode == "be":
            return ("show_belgium", 30024)
        elif languageCode == "ee":
            return ("show_estonia", 30044)
        elif languageCode == "dk":
            return ("show_danish", 30045)
        elif languageCode == "de":
            return ("show_german", 30047)
        elif languageCode == None:
            return ("show_other", 30012)
        else:
            raise NotImplementedError("Language code not supported")

    def __LoadSettings(self):
        # the settings object
        # AddonSettings.__settings = xbmcaddon.Addon(id=self.ADDON_ID)
        Logger.Info("Loading Settings into static object")
        try:
            import xbmcaddon  # @Reimport
            try:
                # first try the version without the ID
                AddonSettings.__settings = xbmcaddon.Addon()
            except:
                Logger.Warning("Settings :: Cannot use xbmcaddon.Addon() as settings. Falling back to  xbmcaddon.Addon(id)")
                AddonSettings.__settings = xbmcaddon.Addon(id=Config.addonId)
        except:
            Logger.Error("Settings :: Cannot use xbmcaddon.Addon() as settings. Falling back to xbmc.Settings(path)", exc_info=True)
            import xbmc  # @Reimport
            AddonSettings.__settings = xbmc.Settings(path=Config.rootDir)

    def __GetSetting(self, settingId):
        """Returns the setting for the requested ID, from the cached settings.

        Arguments:
        settingId - string - the ID of the settings

        Returns:
        The configured XBMC add-on values for that <id>.

        """

        value = AddonSettings.__settings.getSetting(settingId)

        # Logger.Trace("Settings: %s = %s", settingId, value)
        return value

    def __SortChannels(self, x, y):
        """ compares 2 channels based on language and then sortorder """

        value = cmp(x.language, y.language)
        if value == 0:
            return cmp(x.sortOrder, y.sortOrder)
        else:
            return value

    def __GetBooleanSetting(self, settingId):
        """ Arguments:
        id - string - the ID of the settings

        Returns:
        The configured XBMC add-on values for that <id>.

        """

        setting = self.__GetSetting(settingId)
        return setting == "true"

    def __str__(self):
        """Prints the settings"""

        pattern = "%s\n%s: %s"
        value = "%s: %s" % ("MaxNumberOfPages", self.GetMaxNumberOfPages())
        value = pattern % (value, "MaxStreamBitrate", self.GetMaxStreamBitrate())
        value = pattern % (value, "SortingAlgorithm", self.GetSortAlgorithm())
        value = pattern % (value, "DimPercentage", self.GetDimPercentage())
        value = pattern % (value, "UseSubtitle", self.UseSubtitle())
        value = pattern % (value, "CacheHttpResponses", self.CacheHttpResponses())
        value = pattern % (value, "IPlayerProxy", self.GetIPlayerProxy())
        value = pattern % (value, "Folder Prefx", "'%s'" % self.GetFolderPrefix())
        value = pattern % (value, "Loglevel", self.GetLogLevel())
        value = pattern % (value, "Hide GeoLocked", self.HideGeoLocked())
        value = pattern % (value, "Show Dutch", self.ShowChannelWithLanguage("nl"))
        value = pattern % (value, "Show Swedish", self.ShowChannelWithLanguage("se"))
        value = pattern % (value, "Show Lithuanian", self.ShowChannelWithLanguage("lt"))
        value = pattern % (value, "Show Latvian", self.ShowChannelWithLanguage("lv"))
        value = pattern % (value, "Show French Canadian", self.ShowChannelWithLanguage("ca-fr"))
        value = pattern % (value, "Show English Canadian", self.ShowChannelWithLanguage("ca-en"))
        value = pattern % (value, "Show British", self.ShowChannelWithLanguage("en-gb"))
        value = pattern % (value, "Show German", self.ShowChannelWithLanguage("de"))
        value = pattern % (value, "Show Other languages", self.ShowChannelWithLanguage(None))
        value = pattern % (value, "UZG Cache Path", self.GetUzgCachePath())
        value = pattern % (value, "UZG Cache Time", self.GetUzgCacheDuration())
        return value
