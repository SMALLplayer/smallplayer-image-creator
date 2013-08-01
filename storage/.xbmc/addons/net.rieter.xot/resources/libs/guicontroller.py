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
import sys
import os

import xbmcgui

import mediaitem
from config import Config
import controls
from logger import Logger


class GuiController:
    """Controls all actions towards the GUI"""

    def __init__(self, *args, **kwargs):  # @UnusedVariable
        """Initialises the GUI for a specific window (args[0])

        Arguments:
        args      : list - list of arguments

        Keyword Arguments:
        kwargs    : list - list of keyword arguments

        The arguments are mapped in the following way:
        * args[0] : Window - The currently controlled XBMC Window object

        """

        if len(args) < 1:
            raise ReferenceError

        # set the to be controlled window
        self.window = args[0]
        self.progressBarItemLimit = 500

    #==============================================================================
    # Progwindow lists
    #==============================================================================
    def DisplayProgramList(self, items):
        """Displays a list of items in the current Program list (PR_LIST) control.

        Arguments:
        items : list[MediaItem] - the list of MediaItems to show

        The program list ID [PR_LIST] is retrieved from the controls.py file.

        """

        self.window.getControl(controls.PR_LIST).reset()

        if len(items) == 0:
            # add dummy item
            tmp = mediaitem.MediaItem("No playable files found", "")
            tmp.complete = True
            if hasattr(self.window, 'channel') and not self.window.channel is None:
                tmp.thumb = self.window.channel.noImage
            items.append(tmp)

        Logger.Debug("Locking ProgramList")
        xbmcgui.lock()

        xbmcItems = []
        try:
            for m in items:
                # self.window.getControl(controls.PR_LIST).addItem(m.GetXBMCItem())
                xbmcItems.append(m.GetXBMCItem())

            self.window.getControl(controls.PR_LIST).addItems(xbmcItems)

            Logger.Debug("Un-Locking ProgramList")
            xbmcgui.unlock()
        except:
            Logger.Error("Error displaying Episode list", exc_info=True)
            xbmcgui.unlock()

    #===============================================================================
    # Channel stuff
    #===============================================================================
    def SetChannelProperties(self, channel):
        """Set the channel properties on the episode window and program window

        Arguments:
        channel : Channel - The channel to show the information for

        """

        self.SetChannelWindowProperties(channel, self.window)
        self.SetChannelWindowProperties(channel, self.window.episodeWindow)
        pass

    def SetChannelWindowProperties(self, channel, window):
        """sets the channel properties on a window

        Arguments:
        channel : Channel - The channel to show the information for
        window  : Window - The window in which the information needs to be set.

        """

        Logger.Debug("SetChannelProperties :: Setting XOT_ChannelName property to %s", channel.channelName)
        window.setProperty("XOT_ChannelName", channel.channelName)
        window.setProperty("XOT_ChannelDescription", channel.channelDescription)
        window.setProperty("XOT_ChannelIcon", channel.iconLarge)

        background = channel.GetBackgroundImage(window.getResolution() in controls.RESOLUTION_4x3)
        Logger.Debug("SetChannelProperties :: Resolution=%s, %s", window.getResolution(), background)
        # window.setProperty("XOT_DimBackground", "true")
        window.setProperty("XOT_ChannelBackground", background)
        pass

    def SetBackground(self, path):
        """ Sets the background image """

        # just set both options to make sure it works in uzg-channelwindow.xml and uzg-progwindow.xml
        self.window.setProperty("XOT_ChannelBackground", path)
        self.window.setProperty("XOT_Background", path)
        return

    #===============================================================================
    # Episode List stuff
    #===============================================================================
    def ClearEpisodeLists(self):
        """Clears the current channel window of all items.

        This method both clears the actual items of the current windows by calling
        the .reset() method on it, but also clears the page items in the window.

        """
        self.window.clearList()

        try:
            self.window.getControl(controls.PG_LIST).reset()
        except (TypeError, RuntimeError):
            Logger.Debug("ClearEpisodeLists :: Non-Existing Control - controls.PG_LIST")
            pass

        return

    def DisplayFolderList(self, items, position=0):
        """Displays the channel items in the current channel window.

        Arguments:
        items    : list[MediaItem] - A sorted list of items to display
        position : [opt] integer - the position that needs to be displayed. Defaults to 0.

        The MediaItems can be of all types (folder, audio, video and page). The
        page items are ignored in this call (see DisplayPageNavigation). The
        items are expected to be correctly sorted.

        If the highlighted item is not completed, then the item is updated using
        the UpdateVideoItem method.

        """

        Logger.Debug("DisplayFolderList needs to display %s items. \nFocussed is on item %s", len(items), position)
        self.window.clearList()

        if len(items) == 0:
            Logger.Debug("Adding Dummy Item")
            tmp = mediaitem.MediaItem("No playable files found", "")
            tmp.complete = True
            tmp.thumb = self.window.channel.noImage
            tmp.icon = self.window.channel.icon
            items.append(tmp)

        # check if a progressbar is needed:
        pbEnabled = len(items) > self.progressBarItemLimit

        if pbEnabled:
            Logger.Info("Using Progressbar to display %s items", len(items))
            percentagePerItem = 100.0 / len(items)
            itemNr = 0
            progDialog = xbmcgui.DialogProgress()
            progDialog.create("Please Wait...", "Adding Items to list")

        for item in items:
            if not item.type == "page":
                tmp = item.GetXBMCItem()

                self.window.addItem(tmp)
                if pbEnabled:
                    itemNr = itemNr + 1
                    progDialog.update(int(percentagePerItem * itemNr), "Adding Items to list", "Adding item %s of %s" % (itemNr, len(items)))
                    if progDialog.iscanceled() == True:
                        break

        if pbEnabled:
            progDialog.close()

        self.window.setFocus(self.window.getControl(controls.EP_LIST))
        self.window.setCurrentListPosition(position)
        if not self.window.listItems[position].complete:
            item = self.window.channel.UpdateVideoItem(self.window.listItems[position])

            # if the mediaUrl is not filled: item is not complete (DOES NOT WORK WELL)
            if not item.HasMediaItemParts():
                item.SetErrorState("Update did not result in streams")

            # check if the list has not changed during upate:
            if self.window.listItems[position].Equals(item):
                Logger.Info("Updating item (GUIDs match)")
                self.window.listItems[position] = item
            else:
                Logger.Error("Aborting Update because of GUID mismatch")

        # if somehow the list focus was already changed, don't update
        if self.window.getCurrentListPosition() == position:
            Logger.Info("All items where shown. Now fetching focused item info for item number %s", position)
            self.UpdateSelectedItem(self.window.listItems[position])

    def DisplayPageNavigation(self, items):
        """Displays the pagenavigation using the items

        Arguments:
        items : list[MediaItem] - A sorted list of items to display

        The MediaItems can be of all types (folder, audio, video and page). Only
        the page items are used in this call (see DisplayFolderList). The items
        are expected to be correctly sorted.

        """

        Logger.Debug("DisplayPageNavigation starting")

        try:
            pageControl = self.window.getControl(controls.PG_LIST)
            pageControl.reset()

            for item in items:
                if item.type == "page":
                    tmp = item.GetXBMCItem()
                    pageControl.addItem(tmp)

        except (TypeError, RuntimeError):
            Logger.Info("DisplayPageNavigation :: Non-Existing Control - controls.PG_LIST")
            pass

        return

    #===========================================================================
    # Channel items stuff
    #===========================================================================
    def UpdateSelectedItem(self, item, xbmcItem=None):
        """Updates the currently selected item with more info labels.

        Arguments:
        item : MediaItem - the MediaItem used to get the info from

        Keyword Arguments:
        xbmcItem : [opt] ListItem - the XBMC Listitem that needs to be updated

        If xbmcItem is set, it will use that one to update, else it will get
        the item using getCurrentListPosition

        """

        if xbmcItem == None:
            index = self.window.getCurrentListPosition()
            if index < 0:
                Logger.Debug("UpdateSelectedItem :: Not Setting item property: index < 0 (%s)", index)
                return

            Logger.Debug("UpdateSelectedItem :: Setting item property on index %s", index)
            xbmcItem = self.window.getListItem(index)

        item.UpdateXBMCItem(xbmcItem)
        return

    #===========================================================================
    # Custom stuff for all windows
    #===========================================================================
    @staticmethod
    def GetImageLocation(image, channel=None):
        """returns the path for a specific image name.

        Arguments:
        image : string - the filename of the requested argument.

        Keyword Arguments:
        channel : [opt] Channel - the channel used to lookup the image

        Returns:
        The full local path to the requested image.

        This methods checks if the currently selected XOT skin has the requested
        filename. If so it will return the path to that file in the XOT skin. If
        not present, it will check the folder of the selected channel. If the
        file is present there. It will then return that path.

        The method is mainly used to allow skinners to include XOT images in their XOT
        skins. Those images will then be used instead of the default channel skin image.

        """

        if image == "":
            return ""

        if channel is None:
            # no channel is available, so just return the image
            # it should be in the skin
            return image

        skinPath = os.path.join(Config.rootDir, "resources", "skins", Config.skinFolder, "media", image)
        if not os.path.exists(skinPath):
            # if a channel is present and the image is not in the skin
            # return the image from the channel
            return os.path.join(os.path.dirname(sys.modules[channel.__module__].__file__), image)
        else:
            # the image is in the skin, so just return it.
            return image
