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
# Make global object available
#===============================================================================
from logger import Logger

class PrefixHelper:
    """Class used to De-Prefix titles. 
    
    Changes: "The A-Team" into "A-Team, the"
    
    """
    
    def __init__(self, test = False):
        """Initializes the class and defines the prefixes.
        
        Keyword Arguments:
        test : boolean - If set to True, it will call some test cases
        
        """
        
        self.prefixes = ("de", "het", "the", "een", "a", "an")
        self.Test = test
        
        if (self.Test):
            self.GetDePrefixedName("De Naam")
            self.GetDePrefixedName("De naam")
            self.GetDePrefixedName("de Naam")
            self.GetDePrefixedName("de naam")
        return
    
    def GetDePrefixedName(self, name):
        """Actually deprefixes a title:
        
        Arguments:
        name : string - the name/title to process
        
        Returns:
        A de-prefixed representation of the original <name>:
        "The A-Team" -> "A-Team, the"
        
        """
        
        oldName = name
        for prefix in self.prefixes:
            if name.lower().startswith(prefix.lower() + " "):                
                newPrefix = name[0:len(prefix)]
                newName = name[len(prefix)+1:]                   
                if newPrefix[0].upper() == newPrefix[0]:
                    newName = newName[0].upper() + newName[1:]
                name = "%s, %s" % (newName, newPrefix)
                
                if (self.Test):
                    Logger.Debug("De-Prefixed: '%s' into '%s'", oldName, name)
                break
        return name