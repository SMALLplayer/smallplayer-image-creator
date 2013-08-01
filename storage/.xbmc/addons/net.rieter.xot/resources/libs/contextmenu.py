#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

import xbmcgui
import time

#===============================================================================
# Make global object available
#===============================================================================
import controls
from logger import Logger

#------------------------------------------------------------------------------ 
NUM_BUTTONS = 9 #from skin file
#------------------------------------------------------------------------------ 

class ContextMenuItem:
    """Context menu item class that is used to pass on contextmenu items."""
    
    def __init__(self, label, functionName, itemTypes = None, completeStatus = None, plugin=False):
        """Instantiation of the class. 
        
        Arguments:
        label          : string - The label/name of the item
        functionName   : string - The name of the method that is called when the item is selcted
        
        Keyword Arguments:
        itemTypes      : list[string] - The MediaItem types for which the contextitem 
                                        should be shown [optional]
        completeStatus : boolean      - Indication whether the item should only 
                                        be shown if the MediaItem.status equals 
                                        this value.
        plugin         : boolean      - Indication whether the item should show
                                        in the plugin.
        
        """
        
        self.label = label
        self.functionName = functionName
        self.itemTypes = itemTypes
        self.completeStatus = completeStatus
        self.plugin = plugin

    def __str__(self):
        """Returns the string representation of the contextmenu item"""
        
        return "%s (%s), Types:%s CompleteStatus:%s, Plugin:%s" % (self.label, self.functionName, self.itemTypes, self.completeStatus, self.plugin)

class GUI(xbmcgui.WindowXMLDialog):
    """Main context menu GUI class. Inherits from xbmcgui.WindowXMLDialog"""
    
    def __init__( self, *args, **kwargs ):
        """Create a new WindowXMLDialog script.
    
        xmlFilename     : string - the name of the xml file to look for.
        scriptPath      : string - path to script. used to fallback to if the xml doesn't exist in the current skin. (eg os.getcwd())
        defaultSkin     : [opt] string - name of the folder in the skins path to look in for the xml. (default='Default')
        defaultRes      : [opt] string - default skins resolution. (default='720p')

        *Note, skin folder structure is eg (resources/skins/Default/720p)
        
        """
        
        Logger.Debug("contextmenu opening")
        xbmcgui.lock()
        self.parent = kwargs["parent"]
        self.menuItems = kwargs["menuItems"]
        self.selectedItem = None
        self.doModal()

    def onInit(self):
        """Initialisation of class after the GUI has been loaded. 
        
        This happens every time. Triggered by doModal in the ShowEpisodeWindow Method. It
        should not be edited by users.
        
        """
        try:
            Logger.Trace("Initialising ContextMenu")
            self.SetupContextMenu()
            xbmcgui.unlock()
        except:
            Logger.Critical("Error aligning the contexmenu", exc_info=True)
        
    def onAction(self, action):
        """Handles the user <action> for the channelGUI. 
        
        
        Arguments:
        action : Action - The action that was done.
        
        Action Method for handling all <action>s except the clicking. This one should only 
        be inherited, not overwritten.
        
        """
        
        try:
            if action in controls.ACTION_BACK_CONTROLS or action in controls.ACTION_EXIT_CONTROLS:
                self.close()
            elif action ==  controls.ACTION_SELECT_ITEM:
                #self.selectedItem = self.getFocusId()-1100 - 1 # -1 for correcting for array items
                #Logger.Info("Returning selected value '%s'", self.selectedItem)
                #self.close()
                pass
        except:
            Logger.Critical("Could not return selection value from onActions")
                          
    #------------------------------------------------------------------------------ 
    def onClick(self, controlId):
        """Handles the clicking of an item in control with <controlID>. 
        
        Arguments:
        controlID : integer - the ID of the control that got the click.
        
        This method is used to catch the clicking (Select/OK) in the lists. It then
        calls the correct methods.
        
        """
        
        try:
            Logger.Trace("onClick from controlid=%s", controlId)
            self.selectedItem = controlId-1100 - 1 # -1 for correcting for array items
            Logger.Info("Returning selected value '%s'", self.selectedItem)
            
            # sleep needed to prevent crash?
            time.sleep(0.1)
            self.close()
            pass
        except:
            Logger.Critical("Could not return selection value from onClick", exc_info=True)
        
    #------------------------------------------------------------------------------ 
    def onFocus(self, controlID):
        """"Handles focus changes to a control with <controlID>.
        
        Arguments:
        controlID : integer - the ID of the control that got the focus.        
        
        """
        
        pass
    
    #------------------------------------------------------------------------------ 
    def SetupContextMenu(self):
        """Generates the layout of the Contextmenu based on it's items"""
        
        Logger.Debug("Aligning the contextmenu")
        # get positions and dimensions
        _dialogTopHeight = self.getControl(1001).getHeight()
        _dialogWidth = self.getControl(1002).getWidth()
        _dialogBottomHeight = self.getControl(1003).getHeight()
        _dialogLeft = self.getControl(1001).getPosition()[0]
        _dialogTop = self.getControl(1001).getPosition()[1]
        
        _buttonHeight = self.getControl(1101).getHeight()
        _buttonWidth = self.getControl(1101).getWidth()
        _buttonLeft = self.getControl(1101).getPosition()[0]
        _buttonTop = self.getControl(1101).getPosition()[1]
        _buttonVerticalSpacing = 3
        #_buttonHorizontalSpacing = _buttonLeft + (_dialogWidth-_buttonWidth)/2
        
        _parentHeight = self.parent.getHeight()
        _parentWidth = self.parent.getWidth()
        _parentTop= self.parent.getPosition()[1]
        _parentLeft= self.parent.getPosition()[0]
        
        Logger.Debug("Window dim: %s, %s at pos %s, %s", _parentWidth, _parentHeight, _parentLeft, _parentTop)
                
        # now calculate other things
        _numberOfButtons = len(self.menuItems)
        
        _dialogMiddleHeight = (_buttonHeight+_buttonVerticalSpacing)*_numberOfButtons
        self.getControl(1003).setPosition(_dialogLeft, _dialogTop + _dialogTopHeight + _dialogMiddleHeight)
        self.getControl(1002).setHeight(_dialogMiddleHeight)
        
        # want to set it here, but that is not possible at the moment due to exception
        _dialogGroupTop = _parentTop + int((_parentHeight-_dialogMiddleHeight)/2)
        _dialogGroupLeft = _parentLeft + int((_parentWidth - _dialogWidth)/2)
        Logger.Debug("%s, %s",_dialogGroupLeft, _dialogGroupTop)
        #self.getControl(1000).setPosition(_dialogGroupLeft, _dialogGroupTop)
        
        # and setup the buttons
        for buttonNr in range(_numberOfButtons):
            Logger.Debug("Buttonnr: %s with label %s", 1101+buttonNr, self.menuItems[buttonNr].label)
            buttonControl = self.getControl(1101+buttonNr)
            buttonControl.setPosition(_buttonLeft, _buttonTop + (_buttonVerticalSpacing + _buttonHeight)*buttonNr)
            buttonControl.setLabel(self.menuItems[buttonNr].label)
            buttonControl.setVisible(True)
            buttonControl.setEnabled(True) 
        
        # now arrange the controlnavigation and remove redundant buttons
        self.getControl(1101).controlUp(self.getControl(1100+_numberOfButtons))
        self.getControl(1100+_numberOfButtons).controlDown(self.getControl(1101))
        
        for buttonNr in range(_numberOfButtons, NUM_BUTTONS):
            #Logger.Debug("Removing button: %s", buttonNr+1101)
            self.removeControl(self.getControl(1101+buttonNr))
        self.setFocusId(1101)
