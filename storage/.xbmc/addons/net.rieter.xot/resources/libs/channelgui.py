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
from logging import thread
import threading
import inspect

import xbmcgui

import mediaitem
from config import Config
from helpers.languagehelper import LanguageHelper 
import controls
import contextmenu
import guicontroller
import addonsettings

#===============================================================================
# Make global object available
#===============================================================================
from logger import Logger

#===============================================================================
# main Channel User Interface Class
#===============================================================================
class ChannelGui(xbmcgui.WindowXML):
    """This class handles the GUI representation of the <chn_class> class.
    
    It uses one or more <chn_class> objects and displays them to the users.
    
    """
    
    #============================================================================== 
    def __init__(self, *args, **kwargs):
        """Initialisation of the class. All class variables should be instantiated here
        
        WindowXML(self, xmlFilename, scriptPath[, defaultSkin, defaultRes]) -- Create a new WindowXMLDialog script.
    
        xmlFilename     : string - the name of the xml file to look for.
        scriptPath      : string - path to script. used to fallback to if the xml doesn't exist in the current skin. (eg os.getcwd())
        defaultSkin     : [opt] string - name of the folder in the skins path to look in for the xml. (default='Default')
        defaultRes      : [opt] string - default skins resolution. (default='720p')
        
        *Note, skin folder structure is eg(resources/skins/Default/720p)
                
        """
        
        self.channel = None
        
        self.listItems = []    #holds the items in the list
        self.folderHistory = []                  # top one contains selected position in PREVIOUS Folder
        self.folderHistorySelectedPosition = []  # top one contains the url of the CURRENT Folder
        self.currentPosition = 0;
        self.parentItem = None
        
        self.windowInitialised = False
        
        # set timer timeout for keyupdown
        self.timerTimeOut = 0.5
        self.videoUpdateLock = threading.Lock()
        self.focusControlID = 0
        
        self.guiController = guicontroller.GuiController(self)        
        self.guiController.SetBackground(addonsettings.AddonSettings().BackgroundImageProgram())
                
    #==============================================================================
    # Set the active channel
    #==============================================================================
    def ShowChannelWithUrl(self, channel, item):
        """Shows a <channel> with a specific <item> as root item.
        
        Arguments:
        channel : Channel - The channel to show
        item    : MediaItem - The initial item to use to fill the channel list
        
        Uses this object to show the <channel> starting at a specific <item>. The 
        <item> is set as a rootitem and then calls the InitScript method on the 
        <channel>.
        
        """

        if channel == None:
            Logger.Error("Cannot start channel without a channel")
            return False
        self.channel = channel  
        
        if item == None:
            Logger.Error("Cannot start channel without start item")
            return False
        self.channel.SetRootItem(item)
        
        # Reset the current state
        self.windowInitialised = False
        
        # Intialise it as script
        if not self.channel.InitScript():
            return False
        self.doModal()
        self.onInit()
    
    #==============================================================================
    # Inherited from xbmcgui.WindowXML
    #==============================================================================
    def onInit(self):
        """Initialisation of class after the GUI has been loaded. 
        
        This happens every time. Triggered by doModal in the ShowEpisodeWindow Method. It
        should not be edited by users.
        
        """
        
        try:
            if self.channel == None:
                Logger.Info("onInit(): Window init attempt for window without channel")
                return
            
            Logger.Info("onInit(): Window Initalized for %s", self.channel.moduleName)
            
            if not self.windowInitialised:
                Logger.Debug("Initializing %s Gui for the first time", self.channel.channelName)
                #guiController = guicontroller.GuiController(self)
                    
                # make sure the history is cleared!
                Logger.Debug("Clearing Folder History")
                del self.folderHistory[:]
                del self.folderHistorySelectedPosition [:]
                
                # add initialItem to root and give it the default image and no description.
                # the latter two are used for clearing the fields while loading a new list
                tmpItem = mediaitem.MediaItem("", self.channel.initialItem.url)
                tmpItem.description = "Please wait while loading data"
                tmpItem.thumb = self.channel.noImage
                self.guiController.UpdateSelectedItem(tmpItem)
                self.folderHistory.append(tmpItem)
                self.folderHistorySelectedPosition.append(0)
            
                # create new rootItem and fetch it's items
                rootItem = self.channel.GetRootItem()
                
                # clear history and add the rootitem
                del self.folderHistory[:]
                self.folderHistory.append(rootItem)
                
                # now display the items.
                self.listItems = rootItem.items
                
                self.guiController.ClearEpisodeLists()
                self.guiController.DisplayPageNavigation(self.listItems)
                self.guiController.DisplayFolderList(self.listItems, 0)
                #guiController.ShowData(self.folderHistory[0])
                
                self.windowInitialised = True
                
                Logger.Debug("%s Gui has been initialised for the first time", self.channel.channelName)
            else:
                Logger.Debug("%s GUI window already Initialized", self.channel.channelName)
                
                if self.getControl(controls.EP_LIST).size() < 1:
                    Logger.Info("Somehow the list was cleared...filling it again")
                    self.guiController.DisplayPageNavigation(self.listItems)
                    self.guiController.DisplayFolderList(self.listItems, self.currentPosition)

        except:
            Logger.Critical("Error initialising the %s Window.", self.channel.channelName , exc_info=True)
    
    #============================================================================== 
    def onAction(self, action):
        """Handles the user <action> for the channelGUI. 

        Arguments:
        action : Action - The action that was done.
        
        Action Method for handling all <action>s except the clicking. This one should only 
        be inherited, not overwritten.
        
        """
        
        try:
            if not action.getId() in controls.ACTION_MOUSE_MOVEMENT:
                Logger.Debug("onAction (with buttonid=%s and id=%s) detected (ThrdID=%s)", action.getButtonCode(), action.getId(),thread.get_ident())
            
            if action in controls.ACTION_UPDOWN:
                if (self.getFocusId() == controls.EP_LIST):
                    try:
                        Logger.Debug("Cancelling and starting onKeyUpDown timer")
                        # cancel the timer is present
                        try:
                            self.timerUpDown.cancel()
                        except:
                            pass
                        # start a new one
                        self.timerUpDown = threading.Timer(self.timerTimeOut, self.onUpDown)
                        self.timerUpDown.start()
                    except:
                        Logger.Critical("Error in locking mechanism")

            elif action in controls.ACTION_EXIT_CONTROLS:
                Logger.Debug("Exiting to main progwindow")
                self.onExit()
            elif action in controls.ACTION_BACK_CONTROLS:
                try:
                    Logger.Debug("Removing items from historystack")
                    self.folderHistory.pop()
                    
                    # release the video update lock if present
                    try:
                        self.videoUpdateLock.release()
                    except:
                        # if it wasn't locked, pass the exception
                        pass
                    
                    if self.folderHistory == []:
                        Logger.Debug("No more items in history, exiting")
                        self.onExit()
                    else:
                        # go back an folder, clear list, process the folder and stuff the 
                        # content back in the list
                        self.listItems = self.folderHistory[-1].items
                        if len(self.listItems) < 1:
                            # the caching did not work. Start retrieving it
                            self.listItems = self.channel.ProcessFolderList(self.folderHistory[-1])

                        self.guiController.DisplayFolderList(self.listItems, self.folderHistorySelectedPosition.pop())
                        self.guiController.DisplayPageNavigation(self.listItems)
                    
                except:
                    Logger.Critical("Cannot perform a good BACK action. Closing!", exc_info=True)
                    self.onExit()
                    
#            elif action == controls.ACTION_SELECT_ITEM:
#                self.onClick(self.getFocusId())
            
            elif action in controls.ACTION_CONTEXT_MENU_CONTROLS: # and self.keysLocked < 1:
                Logger.Debug("showing contextmenu")
                self.onActionFromContextMenu()
            
            else:
                pass
                #Logger.Warning("Action %s on ControlID %s was not recognised! No action taken", action.getId(), self.getFocus())
        except:
            Logger.Warning('Action Failed, or could not determine action', exc_info=True)
        
    #===============================================================================
    # Customizable actions    
    #===============================================================================
    def onFocus(self, controlID):
        """Handles focus changes to a control with <controlID>.
        
        Arguments:
        controlID : integer - the ID of the control that got the focus.        
        
        """
        self.focusControlID = controlID
    
    #============================================================================== 
    def onClick(self, controlID):
        """Handles the clicking of an item in control with <controlID>. 
        
        Arguments:
        controlID : integer - the ID of the control that got the click.
        
        This method is used to catch the clicking (Select/OK) in the lists. It then
        calls the correct methods.
        
        """
        
        Logger.Debug("OnClick detected on controlID = %s", controlID)
        
        try:
            # check if the Episode List is active
            Logger.Debug("Trying to determine what to do with the onClick")
            #guiController = guicontroller.GuiController(self)
                
            if controlID == controls.EP_LIST or controlID == controls.PG_LIST:
                # get the episodelist position
                position = self.getCurrentListPosition()
                
                # store the position
                self.currentPosition = position
                    
                if controlID == controls.PG_LIST:
                    # a page was clicked! 
                    Logger.Debug("OnClick detected on pageList")
                    pagePos = self.getControl(controls.PG_LIST).getSelectedPosition()
                    
                
                    # get the item, therefore we need to filter the items for pageitems
                    pageItems = []
                    for item in self.listItems:
                        if item.type == "page":
                            pageItems.append(item)
                
                    item = pageItems[pagePos]
                else:
                    Logger.Debug("OnClick detected on EPList")
                    item = self.listItems[position]
                    xbmcItem = self.getListItem(position)
                    
                # Determine type of item
                if item.IsPlayable():
                    # if not complete, update
                    Logger.Debug("Detected a playable file: %s", item.type)
                    if not item.complete:
                        item = self.channel.UpdateVideoItem(item)
                        # if the mediaUrl is not filled: item is not complete
                        if not item.HasMediaItemParts():
                            item.SetErrorState("Update did not result in streams")
                        
                        # check if the list has not changed during upate:
                        #if item.guid == self.listItems[position].guid:
                        if item.Equals(self.listItems[position]):
                            Logger.Info("Updating item (GUIDs match)")                
                            self.listItems[position] = item
                        else:
                            Logger.Error("Aborting Update because of GUID mismatch")
                    Logger.Info("Starting playback of %s", item)
                    self.guiController.UpdateSelectedItem(item, xbmcItem)
                    self.channel.PlayVideoItem(item)
                elif item.type == 'folder' or item.type == 'page':
                    Logger.Debug("Detected Folder or Page\nAppending current selected position (%s) to history.", position)

                    # remember the selected position 
                    self.folderHistorySelectedPosition.append(position)
                    
                    # append the item to the history
                    self.folderHistory.append(item)
                    
                    # add content items to the selected item
                    item.items = self.channel.ProcessFolderList(item)
                    
                    # make those items the listItems
                    self.listItems = item.items
        
                    # display items
                    self.guiController.DisplayPageNavigation(self.listItems)
                    self.guiController.DisplayFolderList(self.listItems, 0)
                        
                elif item.type == 'append':
                    Logger.Debug("Detected Appendable Folder on position %s", position)
                    
                    #read the currently showing parentitem and it's childitems 
                    parentItem = self.folderHistory[-1]
                    
                    #get new items
                    items = self.channel.ProcessFolderList(item)
                    
                    #append them to the childitems of the parentitem
                    self.AppendItemsAt(parentItem.items, items, position)
                                        
                    #sort them or not
                    
                    #show them and highlight the current selection
                    self.listItems = parentItem.items
                    self.guiController.DisplayFolderList(self.listItems, position)
                    self.onUpDown(True)                
                else:
                    Logger.Warning("Error updating %s (%s) for %s", item.name, item.type, self.channel.channelName)
                        
            else:
                Logger.Warning("ControlID (%s) was not recognised! No action taken", controlID)
        except:
            Logger.Critical("On Click error showing episodes", exc_info=True)
     
    #============================================================================== 
    def onUpDown(self, ignoreDisabled = False):
        """Handles the Up and Down actions for the channels. 
        
        Keyword arguments:    
        ignoreDisable : boolean - ignores the channel property self.onUpDownUpdateEnabled
        
        Action Method for handling selecting. If the <ignoreDisable> is set to True
        it makes the script ignore self.onUpDownUpdateEnabled and update anyway! 
        
        """
        
        Logger.Debug("OnKeyUp/KeyDown Detected")
        try:
            # get the item that is focused
            position = self.getCurrentListPosition()
            item = self.listItems[position]
            xbmcItem = self.getListItem(position)
            #guiController = guicontroller.GuiController(self)
            
            if item.complete:
                #item is complete. Just show
                Logger.Debug("No OnKeyUp/KeyDown for a complete item")
                self.guiController.UpdateSelectedItem(item, xbmcItem) #, updateXBMC = True)
                return
            
            if item.type == "folder" or item.type == "append":
                #item is folder. 
                Logger.Debug("No OnKeyUp/KeyDown for a folder or append item")
                self.guiController.UpdateSelectedItem(item, xbmcItem)
                return
            
            if item.complete == False and item.IsPlayable() and (not self.channel.onUpDownUpdateEnabled and not ignoreDisabled):
                # item is not complete, but the onupdown is disabled and we don't have to ignore that
                # just show the data
                Logger.Debug("Item is not complete, but the onupdown is disabled and we don't have to ignore that. Only showing data")
                self.guiController.UpdateSelectedItem(item, xbmcItem)
                return
            
            if item.complete == False and item.IsPlayable() and (self.channel.onUpDownUpdateEnabled or ignoreDisabled):
                # if video item and not complete, do an update if not already busy
                
                #===============================================================================
                # Locking block 
                #===============================================================================
                # aquire lock so that all new timers in the keyUp/Down actions will
                # be blocked! A timer is set to call the onUpDown again after waiting
                Logger.Trace("1.==== Trying to acquire a lock")
                if (not self.videoUpdateLock.acquire(0)):
                    Logger.Trace("2.==== Lock was already active")
                    try:
                        self.timerUpDown.cancel()
                    except:
                        pass
                    Logger.Trace("Resetting the timer from within onUpDown")
                    self.timerUpDown = threading.Timer(self.timerTimeOut, self.onUpDown)
                    self.timerUpDown.start()
                    return
                Logger.Trace("2.==== Lock Acquired")
                #============================================================================== 
                # Actual action happens now:
                Logger.Debug("Item '%s' not completed yet. Updating Video", item.name)
                
                #display please wait:
                #guiController.UpdateSelectedItem(self.folderHistory[0])
                
                item = self.channel.UpdateVideoItem(item)
                # if the mediaUrl is not filled: item is not complete
                if not item.HasMediaItemParts():
                    item.SetErrorState("Update did not result in streams")
                
                # check if the list has not changed during upate:
                if item.Equals(self.listItems[position]):
                    Logger.Info("Updating item (GUIDs match)")                
                    self.listItems[position] = item                    
                else:
                    Logger.Error("Aborting Update because of GUID mismatch\n(%s and %s)", item.guid, self.listItems[position].guid)
                
                # release lock
                Logger.Trace("3.==== UnLocking the lock")
                
                self.guiController.UpdateSelectedItem(item, xbmcItem)
                self.videoUpdateLock.release()    
                #===============================================================================
                # Locking block End 
                #===============================================================================
            else:
                #if nothing matched
                Logger.Debug("OnUpDown: does not know what to do")
                return
        except:
            Logger.Error("Error in OnUpDown", exc_info=True)
            try:
                # release lock
                Logger.Trace("3.==== Unlocking the lock after an excpetion")
                self.videoUpdateLock.release()
            except:
                pass
                
            Logger.Critical("Cannot handle KeyUp/Down", exc_info=True)

    #==============================================================================
    def AppendItemsAt(self, source, appendix, position):
        """Appends a list of items at a certain position
        
        Arguments:
        source   : list[MediaItem] - original list of items
        appendix : list[MediaItem] - the list of items to append
        position : integer - the position in the source list were the items should be appended 
        
        """
        
        #reverse the 'appendix' items for easier insertion
        appendix.reverse()
        
        # remove the item which is replaced
        source.pop(position)
        
        for item in appendix:
            # do not add more pages or double items
            if source.count(item) == 0 and item.type != 'append':
                source.insert(position, item)
                    
        return
              
    #============================================================================== 
    def onExit(self):
        """Handles the exiting of the channelGUI. 
        
        It cleans up the listitems and reinitialises the channelGui.
        
        """
        
        self.listItems = []
        self.getControl(controls.EP_LIST).reset()
        self.channel = None
        self.close()

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
    
    #==============================================================================
    # ContextMenu functions
    #==============================================================================
    def onActionFromContextMenu(self):
        """Handles the actions that were chosen from the contectmenu."""
        
        try:
            position = self.getCurrentListPosition()
            item = self.listItems[position]
            contextMenuItems = []
            
            # add settings
            contextMenuItems.append(contextmenu.ContextMenuItem(LanguageHelper.GetLocalizedString(LanguageHelper.AddOnSettingsId), "CtMnSettings"))        
                        
            if item.type == 'folder':
                label = LanguageHelper.GetLocalizedString(LanguageHelper.FavouritesId)
                addTo = LanguageHelper.GetLocalizedString(LanguageHelper.AddToId)
                contextMenuItems.append(contextmenu.ContextMenuItem("%s %s" % (addTo, label), "CtMnAddToFavorites"))
            elif item.IsPlayable():
                pass
            else:
                return None
            
            Logger.Trace(self.channel.contextMenuItems)
            
            possibleMethods = inspect.getmembers(self.channel)
            Logger.Trace(possibleMethods)
            
            for menuItem in self.channel.contextMenuItems:
                Logger.Debug(menuItem)
                                
                if menuItem.itemTypes == None or item.type in menuItem.itemTypes:
                    if menuItem.completeStatus == None or menuItem.completeStatus == item.complete:
                        
                        # see if the method is available
                        methodAvailable = False
                        for method in possibleMethods:
                            if method[0] == menuItem.functionName:
                                methodAvailable = True
                                # break from the method loop
                                break                    
                        
                        if not methodAvailable:
                            Logger.Warning("No method for: %s", menuItem)
                            continue
        
                        contextMenuItems.append(menuItem)
                
            if len(contextMenuItems) == 0:
                return None 
            
            # build menuitems
            contextMenu = contextmenu.GUI(Config.contextMenuSkin, Config.rootDir, Config.skinFolder, parent=self.getFocus(), menuItems = contextMenuItems)
            selectedItem = contextMenu.selectedItem
            del contextMenu
            
            # handle function from items
            if (selectedItem is not None):    
                selectedMenuItem = contextMenuItems[selectedItem]
                functionString = "returnItem = self.channel.%s(item)" % (selectedMenuItem.functionName,)
                #functionString = "self.channel.%s(%s)" % (selectedMenuItem.functionName, position)
                Logger.Debug("Calling '%s'", functionString)
                try:
                    exec(functionString)
                except:
                    Logger.Error("onActionFromContextMenu :: Cannot execute '%s'.", functionString, exc_info = True)
            
            return None
        except:
            Logger.Error("onActionFromContextMenu :: Error on contextmenu action", exc_info = True)
            return None