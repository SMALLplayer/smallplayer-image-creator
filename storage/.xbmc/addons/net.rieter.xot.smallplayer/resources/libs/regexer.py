#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons 
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a 
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/ 
# or send a letter to Creative Commons, 171 Second Street, Suite 300, 
# San Francisco, California 94105, USA.
#===============================================================================
import re

#===============================================================================
# Import the default modules
#===============================================================================
from logger import Logger

class Regexer:
    """ Main regexer class """
    
    def __init__(self):
        raise Exception("Static only class")
    
    @staticmethod
    def DoRegexFindAllOld(regex, data):
        """Performs a regular expression
        
        Arguments:
        regex : string - the regex to perform on the data.
        data  : string - the data to perform the regex on.
        
        Returns:
        A list of matches that came from the regex.findall method.
        
        Performs a regular expression findall on the <data> and returns the results
        that came from the method.     
        
        From the sre.py library:
        If one or more groups are present in the pattern, return a
        list of groups; this will be a list of tuples if the pattern
        has more than one group.
    
        Empty matches are included in the result.
        
        """
        
        try:
            result = re.compile(regex, re.DOTALL + re.IGNORECASE)
            if "?P<" in regex:        
                it = result.finditer(data)    
                return map(lambda x : x.groupdict(), it)
            else:
                return result.findall(data)
        except:
            Logger.Critical('error regexing', exc_info=True)
        
    @staticmethod
    def DoRegex(regex, data):
        """Performs a regular expression
        
        Arguments:
        regex : string - the regex to perform on the data.
        data  : string - the data to perform the regex on.
        
        Returns:
        A list of matches that came from the regex.findall method.
        
        Performs a regular expression findall on the <data> and returns the results
        that came from the method.     
        
        From the sre.py library:
        If one or more groups are present in the pattern, return a
        list of groups; this will be a list of tuples if the pattern
        has more than one group.
    
        Empty matches are included in the result.
        
        """
                
        try:
            
            if not isinstance(regex, (tuple, list)):
                if ("?P<" in regex):
                    return Regexer.__DoDictionaryRegex(regex, data)
                else:
                    return Regexer.__DoRegex(regex, data)
            else:
                Logger.Debug("Performing multi-regex find on '%s'", regex)
                results = []
                count = 0
                for r in regex:
                    if ("?P<" in r):
                        regexResults = Regexer.__DoDictionaryRegex(r, data)
                        # add to the results with a count in front of the results
                        results = results + map(lambda x: (count, x), regexResults)
                    else:
                        regexResults = Regexer.__DoRegex(r, data)
                        if (len(regexResults) > 0):
                            if isinstance(regexResults[0], (tuple,list)):
                                # is a tupe/list was returned, prepend it with the count
                                results = results + map(lambda x: (count,) + x, regexResults)
                            else:
                                # create a tuple with the results
                                results = results + map(lambda x: (count, x), regexResults)
                    # increase count
                    count = count + 1
                Logger.Debug("Returning %s results", len(results))
                return results

#                finalRegex = "(?:"
#                for r in regex:
#                    if r is None or r == "":
#                        continue                    
#                    finalRegex = "%s%s|" % (finalRegex, r)
#                    
#                finalRegex = "%s)" % (finalRegex.rstrip("|"))
#                Logger.Debug(finalRegex)
#                if ("?P<" in finalRegex):
#                    return __DoDictionaryRegex(finalRegex, data)
#                else:
#                    return __DoRegex(finalRegex, data)
        except:
            Logger.Critical('error regexing', exc_info=True)
            return []

    @staticmethod
    def __DoRegex(regex, data):
        """ does the actual regex for non-dictionary regexes 
        
        Arguments:
        regex : string - the regex to perform on the data.
        data  : string - the data to perform the regex on.
        
        Returns:
        A list of matches that came from the regex.findall method.
       
        """
        
        #result = re.compile(regex, re.DOTALL + re.IGNORECASE)
        #return result.findall(data)
        
        return re.findall(regex, data, flags = re.DOTALL + re.IGNORECASE)
    
    @staticmethod
    def __DoDictionaryRegex(regex, data):
        """ does the actual regex for dictionary regexes 
        
        Arguments:
        regex : string - the regex to perform on the data.
        data  : string - the data to perform the regex on.
        
        Returns:
        A list of matches that came from the regex..finditer method.
       
        """
        
        result = re.compile(regex, re.DOTALL + re.IGNORECASE)
        it = result.finditer(data)    
        return map(lambda x : x.groupdict(), it)

# testing facilities
if __name__ == "__main__":
    class DummyLogger:
        """ Just a dummy logger class that can be used to test"""
        
        def __init__(self):
            pass
        
        def Error(self, message, *args, **kwargs):
            message = "Dummy ERROR >> %s" % (message,)
            print message % args
        
        def Debug(self, message, *args, **kwargs):
            message = "Dummy>> %s" % (message,)
            print message % args
            
        def Critical(self, message, *args, **kwargs):
            message = "Dummy>> %s" % (message,)
            print message % args
    
    # create a dummy logger
    Logger = DummyLogger()
        
    regex = ('(\w+) (?P<value1>\w+) (?P<value2>\w+)', '(?P<value1>\w+ \w+)', '\w+', '(\w+)', '(\w+) (\w+)')
    for r in regex:
        print "=================== REGEX"
        print r
        data = 'test1 test2 test3 test4 test5 test6'
        print "===================== OLD"
        print Regexer.DoRegexFindAllOld(r, data)
        print "===================== NEW"
        print Regexer.DoRegex(r, data)
        print Regexer.DoRegex((r,'(.{4}) (.{3})', '(test[13]|test[56])'), data)
        print ""
