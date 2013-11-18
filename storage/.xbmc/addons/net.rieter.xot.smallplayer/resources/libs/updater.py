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
import time
import shutil
import zipfile

import xbmcgui

import controls
import mediaitem
import guicontroller

from regexer import Regexer
from xbmcwrapper import XbmcWrapper
from config import Config
from helpers import htmlentityhelper
from helpers import channelimporter
from helpers.languagehelper import LanguageHelper

#===============================================================================
# Make global object available
#===============================================================================
from logger import Logger
from urihandler import UriHandler


class Updater(xbmcgui.WindowXMLDialog):
    """Update WindowXMLDialog class"""

    def __init__(self, strXMLname, strFallbackPath, strDefaultName, bforeFallback=0):  # @UnusedVariable
        """Initialisation of the class. All class variables should be instantiated here

        WindowXMLDialog(self, xmlFilename, scriptPath[, defaultSkin, defaultRes]) -- Create a new WindowXMLDialog script.

        xmlFilename     : string - the name of the xml file to look for.
        scriptPath      : string - path to script. used to fallback to if the xml doesn't exist in the current skin. (eg os.getcwd())
        defaultSkin     : [opt] string - name of the folder in the skins path to look in for the xml. (default='Default')
        defaultRes      : [opt] string - default skins resolution. (default='720p')

        *Note, skin folder structure is eg(resources/skins/Default/720p)

        """

        Logger.Debug("Updater started")
        self.updateItems = []

    def onInit(self):
        """Initialisation of class after the GUI has been loaded."""

        try:
            self.LoadRepoChannels()
            if len(self.updateItems) > 0:
                self.DisplayInfo(0)
            else:
                XbmcWrapper.ShowDialog(LanguageHelper.GetLocalizedString(LanguageHelper.NoUpdatesId), LanguageHelper.GetLocalizedString(LanguageHelper.NoUpdatedChannelsId))
                self.close()
        except:
            Logger.Error("Error initializing the Updater GUI", exc_info=True)

    def onAction(self, action):
        """Handles the user <action> for the channelGUI.

        Arguments:
        action : Action - The action that was done.

        Action Method for handling all <action>s except the clicking. This one should only
        be inherited, not overwritten.

        """

        try:
            # Logger.Debug("OnAction")
            try:
                # controlID = self.getFocusId()
                if not action.getId() in controls.ACTION_MOUSE_MOVEMENT:
                    # if it was no mousemovement, reset the clicked
                    Logger.Debug("Resetting self.click")
                    self.clicked = False
            except:
                Logger.Error("updater::onAction exception determining controlID", exc_info=True)
                return

            #===============================================================================
            # Handle Back actions
            #===============================================================================
            if action in controls.ACTION_EXIT_CONTROLS or action in controls.ACTION_BACK_CONTROLS:
                Logger.Debug("Closing updater")
                self.close()
                pass

            elif action in controls.ACTION_UPDOWN:
                self.DisplayInfo(self.getCurrentListPosition())

            else:
                if not action.getId() in controls.ACTION_MOUSE_MOVEMENT:
                    Logger.Critical("OnAction::unknow action (id=%s). Do not know what to do", action.getId())
        except:
            Logger.Critical("OnAction Error", exc_info=True)
            self.close()

    def onSelect(self, controlID):
        """Handles the onSelect from the GUI

        Arguments:
        controlID : integer - the ID of the control that got the focus.

        """

        Logger.Debug("onSelect on ControlID=%s", controlID)

    def onClick(self, controlID):
        """Handles the clicking of an item in control with <controlID>.

        Arguments:
        controlID : integer - the ID of the control that got the click.

        This method is used to catch the clicking (Select/OK) in the lists. It then
        calls the correct methods.

        """

        try:
            Logger.Debug("onClick ControlID=%s", controlID)
            if controlID == controls.UD_EXIT:
                time.sleep(0.1)
                self.close()

            elif controlID == controls.UD_LIST:
                updateItem = self.updateItems[self.getCurrentListPosition()]
                yesNoDialog = xbmcgui.Dialog()
                go = yesNoDialog.yesno('Confirm update', 'Are you sure you want to update %s? \nIf the channel already exists it will be deleted!' % (updateItem.name))
                if go:
                    self.UpdateChannel(updateItem)
            pass
        except:
            Logger.Critical("Error handling onClick on controlID=%s", controlID, exc_info=True)

    def onFocus(self, controlID):
        """Handles focus changes to a control with <controlID>.

        Arguments:
        controlID : integer - the ID of the control that got the focus.

        """
        pass

    def LoadRepoChannels(self):
        """Loads the channels of the new repo location"""

        data = UriHandler.Open("http://www.rieter.net/net.rieter.xot.repository/addons.xml", pb=False)
        channels = Regexer.DoRegex('(<addon id="(net.rieter.xot.channel.[^"]+)\W+version="([^"]+)"\W+name="([^"]+)")|(<description>([^<]+)</description>)', data)
        guiController = guicontroller.GuiController(self)

        # skip the first part
        updateItem = None
        for channel in channels[1:]:
            if not channel[0] == "":
                # create item
                updateItem = mediaitem.MediaItem(channel[3], "http://www.rieter.net/net.rieter.xot.repository/%s/%s-%s.zip" % (channel[1], channel[1], channel[2]))
                updateItem.SetDate(2011, 1, 1, text=channel[2])

                # set the zipfile name here, but check in the next loop!
                zipFile = "%s-%s.zip" % (channel[1], channel[2])
                if channelimporter.ChannelImporter.GetRegister().IsChannelInstalled(zipFile):
                    # already installed, continue as if
                    Logger.Info("Update already installed: %s", zipFile)
                    updateItem = None
                    continue
                else:
                    Logger.Info("New update found: %s", zipFile)
            elif not updateItem == None:
                # update description
                updateItem.description = htmlentityhelper.HtmlEntityHelper.ConvertHTMLEntities(channel[5])
                updateItem.icon = guiController.GetImageLocation("xot_updateicon.png")
                self.updateItems.append(updateItem)
                item = updateItem.GetXBMCItem()
                Logger.Debug("Adding update item: %s", updateItem)
                updateItem = None
                self.addItem(item)
        pass

    def DisplayInfo(self, position):
        """Displays the info of the currently selected position

        Arguments:
        position : integer - the currently selected position

        """

        item = self.updateItems[position]
        self.getControl(controls.UD_DESCRIPTION).reset()
        self.getControl(controls.UD_DESCRIPTION).setText(item.description)
        pass

    def UpdateChannel(self, item):
        """Updates the channel that is represented by item

        Arguments:
        item : MediaItem - The item that represents a channel update.

        This method downloads the channel update and puts it in the deploy
        folder. The next XOT start it will be automatically deployed.

        """

        Logger.Info("Starting update for channel %s from %s", item.name, item.url)
        try:
            fileName = UriHandler.Download(item.url, item.name, UriHandler.Instance().defaultLocation)
            Logger.Debug("Download succeeded: %s", fileName)

            # we extract to the deploy folder, so with the first start of XOT, the new channel is deployed
            deployDir = os.path.abspath(os.path.join(Config.rootDir, "deploy"))
            zipFile = zipfile.ZipFile(fileName, 'r')

            # now extract
            first = True
            for name in zipFile.namelist():
                if first:
                    folder = os.path.split(name)[0]
                    if os.path.exists(os.path.join(deployDir, folder)):
                        shutil.rmtree(os.path.join(deployDir, folder))
                    first = False

                if not name.endswith("/") and not name.endswith("\\"):
                    fileName = os.path.join(deployDir, name)
                    path = os.path.dirname(fileName)
                    if not os.path.exists(path):
                        os.makedirs(path)
                    Logger.Debug("Updating %s", fileName)
                    outfile = open(fileName, 'wb')
                    outfile.write(zipFile.read(name))
                    outfile.close()

            zipFile.close()

            message = LanguageHelper.GetLocalizedString(LanguageHelper.UpdateCompleteId, splitOnPipes=False) % (item.name, )
            message = message.split("|")
            XbmcWrapper.ShowDialog(LanguageHelper.GetLocalizedString(LanguageHelper.RestartId), message)
        except:
            Logger.Error("Error handling zipfiles during update", exc_info=True)
            try:
                zipFile.close()
            except:
                pass
            message = LanguageHelper.GetLocalizedString(LanguageHelper.UpdateFailed2Id, splitOnPipes=False) % (item.name, )
            message = message.split("|")
            XbmcWrapper.ShowDialog(LanguageHelper.GetLocalizedString(LanguageHelper.UpdateFailedId), message)
