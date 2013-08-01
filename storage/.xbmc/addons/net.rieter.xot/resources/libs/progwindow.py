#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================
from datetime import datetime

import xbmcgui

import controls
import contextmenu
import channelgui
import settings
import addonsettings
import guicontroller
import envcontroller
import update
import updater

from config import Config
from environments import Environments
from helpers.stopwatch import StopWatch
from helpers.channelimporter import ChannelImporter
from helpers.languagehelper import LanguageHelper
from helpers.statistics import Statistics
from logger import Logger


class GUI(xbmcgui.WindowXML):
    """This class is the GUI representation of the window that shows the channels
    and the related programs for that channel.

    """

    def __init__(self, strXMLname, strFallbackPath, strDefaultName, bforeFallback=0):
        """Initialisation of the class. All class variables should be instantiated here

        WindowXMLDialog(self, xmlFilename, scriptPath[, defaultSkin, defaultRes]) -- Create a new WindowXMLDialog script.

        xmlFilename     : string - the name of the xml file to look for.
        scriptPath      : string - path to script. used to fallback to if the xml doesn't exist in the current skin. (eg os.getcwd())
        defaultSkin     : [opt] string - name of the folder in the skins path to look in for the xml. (default='Default')
        defaultRes      : [opt] string - default skins resolution. (default='720p')

        *Note, skin folder structure is eg(resources/skins/Default/720p)

        """

        try:
            self.mainlistItems = []
            self.initialised = False
            self.contextMenu = True
            self.channelGUIs = []
            self.channelButtonRegister = []
            self.activeChannelGUI = None
            self.selectedChannelIndex = 0
            self.listMode = ProgListModes.Normal  # 1 # 1=normal, 2=favorites
            self.combinedScreen = False

            # create the main episode window
            self.episodeWindow = channelgui.ChannelGui(Config.appChannelSkin, Config.rootDir, Config.skinFolder)

            # get the channels
            self.channelGUIs = ChannelImporter.GetRegister().GetChannels()

            # now that they are ordered: get the buttoncodes. So the order in the buttoncode
            # list is the same!
            for channel in self.channelGUIs:
                if channel.buttonID > 0:
                    self.channelButtonRegister.append(channel.buttonID)
            self.panelViewEnabled = self.channelButtonRegister == []

            # gui controller
            self.guiController = guicontroller.GuiController(self)

            # set the background
            self.guiController.SetBackground(addonsettings.AddonSettings().BackgroundImageChannels())

            Logger.Info("Starting %s ProgWindow with Fallback=%s and DefaultName=%s", Config.appName, strFallbackPath, strDefaultName)
        except:
            Logger.Debug("Error in __init__ of ProgWindow", exc_info=True)

    def onInit(self):
        """Initialisation of class after the GUI has been loaded."""

        try:
            Logger.Debug("ProgWindow :: OnInit")
            # check, if there are buttons registerd, and if there are, if
            # the buttoncount is the same as the channelcount
            if self.channelButtonRegister != []:
                if len(self.channelButtonRegister) != len(ChannelImporter.GetRegister().GetChannels()):
                    Logger.Critical("The number of buttons that were registered is not the same as the number of channels")
                    self.close()

            if not self.initialised:
                Logger.Debug("Doing first initialisation of ProgWindow")
                # hide programlist
                self.ChannelListVisible(True)
                self.combinedScreen = self.DetectDualMode()

                # set initialvalues
                # self.DisplayGUIs()

                # Check if the selected index is still valid?
                self.selectedChannelIndex = self.getCurrentListPosition()
                # Logger.Debug("Current ChannelIndex: %s", self.selectedChannelIndex)
                if (self.selectedChannelIndex >= len(self.channelGUIs)):
                    Logger.Warning("Current ChannelIndex is too large (index %s >= len %s). Resetting to 0", self.selectedChannelIndex, len(self.channelGUIs))
                    self.selectedChannelIndex = 0

                self.activeChannelGUI = self.channelGUIs[self.selectedChannelIndex]
                if self.selectedChannelIndex > 0:
                    self.guiController.SetChannelProperties(self.activeChannelGUI)
                # else:
                    # colorDiff = settings.AddonSettings().GetDimPercentage()
                    # Logger.Debug("Setting DimBackground to %s", colorDiff)
                    # self.setProperty("XOT_DimBackground", colorDiff)

                self.initialised = True

            # this is a work around for a recent bug that was introduced
            if self.getControl(controls.CH_LIST).size() < 1:
                Logger.Debug("Somehow the list was cleared...filling it again")
                self.DisplayGUIs()

            self.setCurrentListPosition(self.selectedChannelIndex)
        except:
            Logger.Error("Error Initializing Progwindow", exc_info=True)

    def onAction(self, action):
        """Handles the user <action> for the channelGUI.

        Arguments:
        action : Action - The action that was done.

        Action Method for handling all <action>s except the clicking. This one should only
        be inherited, not overwritten.

        """

        try:
            # get the FocusID
            try:
                controlID = self.getFocusId()
            except:
                Logger.Error("Unknown focusID for action ID: %s and ButtonCode: %s", action.getId(), action.getButtonCode())
                return

            #===============================================================================
            # Handle Back actions
            #===============================================================================
            if action in controls.ACTION_BACK_CONTROLS or action in controls.ACTION_EXIT_CONTROLS:
                Logger.Debug("Going back a level")
                if self.mainlistItems == [] or not self.panelViewEnabled or self.combinedScreen:
                    Logger.Debug("Closing ProgWindow")
                    self.close()
                else:
                    # hide programlist and show channelpannel
                    Logger.Debug("Switching ProgWindow Mode")
                    self.activeChannelGUI = None
                    self.mainlistItems = []
                    self.ChannelListVisible(True)
                    self.listMode = ProgListModes.Normal

            elif action in controls.ACTION_CONTEXT_MENU_CONTROLS:
                Logger.Debug("Showing contextmenu")
                self.onActionFromContextMenu(controlID)

            #===============================================================================
            # Handle UP/Down on mainlist
            #===============================================================================
            # elif (action in controls.ACTION_UPDOWN or action in controls.ACTION_LEFTRIGHT or action in controls.ACTION_MOUSE_MOVEMENT) and controlID == controls.CH_LIST and (self.mainlistItems == [] or self.combinedScreen):
            elif (action in controls.ACTION_UPDOWN or action in controls.ACTION_LEFTRIGHT) and controlID == controls.CH_LIST and (self.mainlistItems == [] or self.combinedScreen):
                # Determine the active channel only when EP_LIST is in focus
                # self.selectedChannelIndex = self.getCurrentListPosition()
                # self.activeChannelGUI = self.channelGUIs[self.selectedChannelIndex]

                if not self.combinedScreen:
                    self.guiController.SetChannelProperties(self.activeChannelGUI)

                # self.ShowChannelInfo()

            #===============================================================================
            # Handle onClicks
            #===============================================================================
            # elif action == controls.ACTION_SELECT_ITEM:
            #    Logger.Debug("Progwindow :: Performing a SelectItem")
            #    # handle the onClicks. Because we use a WrapList the onClick also triggers
            #    # an onAction, causing some problems. That is why we handle onclicks here now.
            #    # normally the onClick occurs and then the onAction
            #    #self.onSelect(controlID)

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

        #===============================================================================
        # Handle main lists
        #===============================================================================
        if controls.EP_LIST <= controlID <= controls.EP_LIST + 9:  # and self.mainlistItems==[]:
            startTime = datetime.now()

            # set the active channel in case no up/down was done!
            self.mainlistItems = []
            self.listMode = ProgListModes.Normal

            self.selectedChannelIndex = self.getCurrentListPosition()
            self.activeChannelGUI = self.channelGUIs[self.selectedChannelIndex]
            self.guiController.SetChannelProperties(self.activeChannelGUI)

            # Get MainlistItems
            didWeStartEmpty = len(self.activeChannelGUI.mainListItems) == 0
            try:
                self.mainlistItems = self.activeChannelGUI.ParseMainList()
            except:
                Logger.Error("Error fetching mainlist", exc_info=True)
                self.mainlistItems = []

            self.ShowListItems(self.mainlistItems)

            # hide Main ChannelList and show ProgramList
            self.ChannelListVisible(False)

            # call for statistics
            if didWeStartEmpty:
                Statistics.RegisterChannelOpen(self.activeChannelGUI, startTime)

        # if mainlist is not empty, then the episodewindow should be dispalyed
        elif controlID == controls.PR_LIST and self.mainlistItems != []:
            selectedPosition = self.getControl(controls.PR_LIST).getSelectedPosition()
            if self.listMode == ProgListModes.Favorites:
                if selectedPosition > len(self.favoriteItems):
                    Logger.Error("Favorites list does not have %s items, so item %s cannot be selected", selectedPosition, selectedPosition)
                    return
                selectedItem = self.favoriteItems[selectedPosition]
            else:
                selectedItem = self.mainlistItems[selectedPosition]

            Logger.Info('opening episode list GUI with item = %s', selectedItem)

            self.episodeWindow.ShowChannelWithUrl(self.activeChannelGUI, selectedItem)

        #===============================================================================
        # check if a button that was registered was pressed!
        #===============================================================================
        elif controlID in self.channelButtonRegister:
            # set the active channel in case no up/down was done!
            self.selectedChannelIndex = self.channelButtonRegister.index(controlID)
            self.activeChannelGUI = self.channelGUIs[self.selectedChannelIndex]

            self.getControl(controls.PR_LIST).reset()
            self.ChannelListVisible(False)

            # Get MainlistItems
            self.mainlistItems = self.activeChannelGUI.ParseMainList()

            for m in self.mainlistItems:
                self.getControl(controls.PR_LIST).addItem(xbmcgui.ListItem(m.name, "", m.icon, m.icon))

    def onClick(self, controlID):
        """Handles the clicking of an item in control with <controlID>.

        Arguments:
        controlID : integer - the ID of the control that got the click.

        This method is used to catch the clicking (Select/OK) in the lists. It then
        calls the correct methods.

        """

        try:
            Logger.Debug("Progwindow :: onClick ControlID=%s", controlID)
            self.onSelect(controlID)
        except:
            Logger.Critical("Error handling onClick on controlID=%s", controlID, exc_info=True)

    def onFocus(self, controlID):
        """Handles focus changes to a control with <controlID>.

        Arguments:
        controlID : integer - the ID of the control that got the focus.

        """

        try:
            # Logger.Debug("onFocus :: Control %s has focus now", controlID)
            pass
        except:
            Logger.Critical("Error handling onFocus on ControlID=%s", controlID, exc_info=True)

    def close(self):
        """close(self) -- Closes this window.

        Closes this window by activating the old window.
        The window is not deleted with this method.

        Also the logfile is closed here.

        """

        Logger.Instance().CloseLog()
        xbmcgui.WindowXML.close(self)

    def getCurrentListPosition(self):
        """overload method to get stuff working in some rare x64 cases

        There are some issues with the return value -1 from the xbmcgui method
        xbmcgui.WindowXML.getCurrentListPosition(). In some x64 cases it returns
        the value 4294967295 (0xFFFFFFFF) instead of -1. This method catches
        this issue and returns "value - 0x100000000" is >= -1.

        Otherwise it just returns xbmcgui.WindowXML.getCurrentListPosition()

        """

        position = xbmcgui.WindowXML.getCurrentListPosition(self)
        possiblePosition = position - 0x100000000

        if possiblePosition >= -1:
            Logger.Warning("CurrentListPosition is too large (%s). New value determined: %s", position, possiblePosition)
            return possiblePosition

        return position

    #===============================================================================
    #    Contextmenu stuff
    #===============================================================================
    def onActionFromContextMenu(self, controlID):
        """Handles the actions that were chosen from the contectmenu."""

        if self.contextMenu is False:
            return None

        contextMenuItems = []

        # determine who called the menu
        if controlID != controls.CH_LIST:
            selectedIndex = self.getControl(controls.PR_LIST).getSelectedPosition()
            parentControl = self.getFocus()
            # determine if favorites are enabled
            favs = LanguageHelper.GetLocalizedString(LanguageHelper.FavouritesId)

            if (self.listMode == ProgListModes.Normal):
                show = LanguageHelper.GetLocalizedString(LanguageHelper.ShowId)
                add = LanguageHelper.GetLocalizedString(LanguageHelper.AddToId)

                contextMenuItems.append(contextmenu.ContextMenuItem("%s %s" % (show, favs), "CtMnShowFavorites"))
                contextMenuItems.append(contextmenu.ContextMenuItem("%s %s" % (add, favs), "CtMnAddToFavorites"))

                # add the refresh button
                contextMenuItems.append(contextmenu.ContextMenuItem(LanguageHelper.GetLocalizedString(LanguageHelper.RefreshListId), "CtMnRefresh"))
            else:
                hide = LanguageHelper.GetLocalizedString(LanguageHelper.HideId)
                remove = LanguageHelper.GetLocalizedString(LanguageHelper.RemoveId)
                fav = LanguageHelper.GetLocalizedString(LanguageHelper.FavouriteId)

                contextMenuItems.append(contextmenu.ContextMenuItem("%s %s" % (hide, favs), "CtMnHideFavorites"))
                contextMenuItems.append(contextmenu.ContextMenuItem("%s %s" % (remove, fav), "CtMnRemoveFromFavorites"))

                # add the refresh button for favorites
                contextMenuItems.append(contextmenu.ContextMenuItem(LanguageHelper.GetLocalizedString(LanguageHelper.RefreshListId), "CtMnShowFavorites"))

        if controlID == controls.CH_LIST or self.combinedScreen:
            if controlID == controls.CH_LIST:
                # channel list, so pass the channelindex
                selectedIndex = self.getCurrentListPosition()
            else:
                # combined screen, pass the index of the program
                selectedIndex = self.getControl(controls.PR_LIST).getSelectedPosition()

            parentControl = self.getFocus()  # self.getControl(controls.CH_LIST_WRAPPER)

            if envcontroller.EnvController.IsPlatform(Environments.Xbox):
                langChannel = LanguageHelper.GetLocalizedString(LanguageHelper.ChannelsId)
                contextMenuItems.append(contextmenu.ContextMenuItem("Update %s" % (langChannel,), "CtMnUpdateChannels"))

            contextMenuItems.append(contextmenu.ContextMenuItem(LanguageHelper.GetLocalizedString(LanguageHelper.CheckUpdatesId), "CtMnUpdateXOT"))
            contextMenuItems.append(contextmenu.ContextMenuItem(LanguageHelper.GetLocalizedString(LanguageHelper.AddOnSettingsId), "CtMnSettingsXOT"))

        # build menuitems
        contextMenu = contextmenu.GUI(Config.contextMenuSkin, Config.rootDir, Config.skinFolder, parent=parentControl, menuItems=contextMenuItems)
        selectedItem = contextMenu.selectedItem
        del contextMenu

        # handle function from items
        if (selectedItem is not None and selectedItem > -1):
            selectedMenuItem = contextMenuItems[selectedItem]
            functionString = "self.%s(%s)" % (selectedMenuItem.functionName, selectedIndex)
            Logger.Debug("Calling %s", functionString)
            try:
                exec(functionString)
            except:
                Logger.Error("onActionFromContextMenu :: Cannot execute '%s'.", functionString, exc_info=True)

        return None

    def CtMnShowFavorites(self, selectedIndex):
        """Shows the favorites for the selected channel

        Arguments:
        selectedIndex : integer - the index of the currently selected item
                                  for the channel. Not used here.

        """

        self.listMode = ProgListModes.Favorites
        # Get Favorites
        self.favoriteItems = settings.LoadFavorites(self.activeChannelGUI)
        self.ShowListItems(self.favoriteItems)

    def CtMnHideFavorites(self, selectedIndex):
        """Hides the favorites for the selected channel

        Arguments:
        selectedIndex : integer - the index of the currently selected item
                                  for the channel. Not used here.

        """

        self.listMode = ProgListModes.Normal
        self.ShowListItems(self.mainlistItems)

    def CtMnAddToFavorites(self, selectedIndex):
        """Add the selected item to the the favorites for the selected channel

        Arguments:
        selectedIndex : integer - the index of the currently selected item

        """

        settings.AddToFavorites(self.mainlistItems[selectedIndex], self.activeChannelGUI)

    def CtMnRemoveFromFavorites(self, selectedIndex):
        """Remove the selected item from the the favorites for the selected channel

        Arguments:
        selectedIndex : integer - the index of the currently selected item

        """
        settings.RemoveFromFavorites(self.favoriteItems[selectedIndex], self.activeChannelGUI)
        # reload the items
        self.favoriteItems = settings.LoadFavorites(self.activeChannelGUI)
        self.ShowListItems(self.favoriteItems)

    def CtMnUpdateXOT(self, selectedIndex):
        """Checks for new XOT framework updates.

        Shows a popup if a new version is available.

        Arguments:
        selectedIndex : integer - the index of the currently selected item this
                                  one is not used here.

        """

        update.CheckVersion(Config.Version, Config.updateUrl, verbose=True)

    def CtMnRefresh(self, selectedIndex):
        """Refreshes the currenlty shown list

        Arguments:
        selectedIndex : integer - the index of the currently selected item this
                                  one is not used here.

        """

        Logger.Debug("Refreshing current list")

        if not self.activeChannelGUI is None:
            self.activeChannelGUI.mainListItems = []
            try:
                self.mainlistItems = self.activeChannelGUI.ParseMainList()
            except:
                Logger.Error("Error fetching mainlist", exc_info=True)
                self.mainlistItems = []

            self.ShowListItems(self.mainlistItems)
        else:
            Logger.Debug("Cannot refresh a list without a channel.")

    def CtMnSettingsXOT(self, selectedIndex):
        """Shows the Add-On Settings dialog.

        Arguments:
        selectedIndex : integer - the index of the currently selected item this
                                  one is not used here.

        """

        addonsettings.AddonSettings().ShowSettings()

        # set the background, in case it changed
        self.guiController.SetBackground(addonsettings.AddonSettings().BackgroundImageChannels())
        return

    def CtMnUpdateChannels(self, selectedIndex):
        """Shows the XOT Channel update dialog (only for XBMC4Xbox).

        Arguments:
        selectedIndex : integer - the index of the currently selected item this
                                  one is not used here.

        """

        updaterWindow = updater.Updater(Config.updaterSkin, Config.rootDir, Config.skinFolder)
        updaterWindow .doModal()
        del updaterWindow

    #===============================================================================
    # Fill the channels
    #===============================================================================
    def DisplayGUIs(self):
        """Shows the channels for that are available in XOT."""

        timer = StopWatch("Progwindow :: showing channels", Logger.Instance())
        self.clearList()
        xbmcgui.lock()
        try:
            for channelGUI in self.channelGUIs:
                tmp = xbmcgui.ListItem(channelGUI.channelName, "", channelGUI.icon, channelGUI.iconLarge)
                tmp.setProperty("XOT_ChannelDescription", channelGUI.channelDescription)
                Logger.Trace("Adding %s", channelGUI.channelName)
                self.addItem(tmp)
        finally:
            xbmcgui.unlock()
        timer.Stop()

    def ShowListItems(self, items):
        """Displays a list of items in the Program list.

        Arguments:
        items : list[MediaItem] - the MediaItems to show in the list.

        """

        guiController = guicontroller.GuiController(self)
        guiController.DisplayProgramList(items)

    #===============================================================================

    def DetectDualMode(self):
        """Detects if there are 2 lists to show/hide or just a combined screen

        XOT 3.2.4 introduced a combined Channel/Program window. This method
        detects the old situation (seperated lists) or the new situation
        (combined screen).

        Returns:
        True if a combination screen is available.

        """

        try:
            self.getControl(controls.CH_LIST_WRAPPER).getId()
            self.getControl(controls.PR_LIST_WRAPPER).getId()
            Logger.Debug("Progwindow :: seperate lists are available")
            return False
        except (TypeError, RuntimeError):
            Logger.Debug("Progwindow :: combined screen is available")
            return True

    def ChannelListVisible(self, visibility):
        """Shows or hides the channels

        Arguments:
        visibility : boolean - Whether the channels should be visible or not.

        If the <visibility> is set to True, then the channels are shown and the
        program list is hidden.

        """

        try:
            if visibility:
                Logger.Debug("Showing Channels")
                self.getControl(controls.CH_LIST_WRAPPER).setVisible(True)
                # self.getControl(controls.PR_LIST_WRAPPER).setVisible(False)
                self.setFocusId(controls.CH_LIST_WRAPPER)
            else:
                Logger.Debug("Hiding Channels")
                self.getControl(controls.CH_LIST_WRAPPER).setVisible(False)
                # self.getControl(controls.PR_LIST_WRAPPER).setVisible(True)
        except (TypeError, RuntimeError):
            # is no wrappers are available, don't do anything
            pass

        if visibility:
            self.setFocusId(controls.CH_LIST)
        else:
            self.setFocusId(controls.PR_LIST)

        return


#===============================================================================
# Progwindow Enumeration
#===============================================================================
class ProgListModes:
    """The class is used to create a ProgListModesEnum object that behaves
    like a real Enumeration (like the C# kind).

    """

    Normal = 1
    Favorites = 2
