#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================

class Event:
    """Event class that implements .NET like event handling"""
    def __init__(self):
        """Initialises a new Event Class object"""
        
        self.eventHandlers = set()

    def AddEventHandler(self, handler):
        """Adds an eventhandler to the collection of events
        
        Arguments:
        handler : method - The Eventhandler to add
        
        Returns:
        the current event object. 
        
        When the event is triggered, it will 
        be called with the *args and **kwargs arguments.
        
        """
        
        self.eventHandlers.add(handler)
        return self

    def RemoveEventHandler(self, handler):
        """Removes an eventhandler from the eventhandler collection
        
        Arguments:
        handler : method - The handler that should be removed
        
        Returns:
        the current event object.
        
        """
        try:
            self.eventHandlers.remove(handler)
        except:
            raise ValueError("This event is not handled by the eventhandler (handler).")
        return self
    
    def TriggerEvent(self, *args, **kargs):
        """Triggers all eventhandlers with the given arguments:
        
        Arguments:
        args   : list - List of arguments
        
        Keyword Arguments:
        kwargs : list - List of keyword arguments 
        
        """
        
        for handler in self.eventHandlers:
            handler(*args, **kargs)

    def GetNumberOfRegisteredHandlers(self):
        """Returns the number of registered handlers"""
        
        return len(self.eventHandlers)

    # define the short-hand methods. Only these are needed for the rest of the code
    __iadd__ = AddEventHandler                  #: Implements the Event += EventHandler
    __isub__ = RemoveEventHandler               #: Implements for Event -= EventHandler
    __call__ = TriggerEvent                     #: Trigger the Event by calling it.
    __len__  = GetNumberOfRegisteredHandlers    #: Implements len(Event)
