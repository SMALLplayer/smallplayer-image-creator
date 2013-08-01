#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================
import os.path
import sys
from datetime import datetime


class Initializer:
    StartTime = datetime.now()  # : Used for duration determinination

    @staticmethod
    def SetUnicode():
        """Forces the environment to UTF-8"""

        reload(sys)
        sys.setdefaultencoding("utf-8")  # @UndefinedVariable
        return

    @staticmethod
    def SetupPythonPaths():

        # Get the path we are in
        try:
            import xbmcaddon
            addon = xbmcaddon.Addon()
            path = addon.getAddonInfo('path')
        except:
            path = os.getcwd()

        # the XBMC libs return unicode info, so we need to convert this
        path = path.decode('utf-8')  # .encode('latin-1')
        # insert the path at the start to prevent other lib-add-ons to steal our class names
        sys.path.insert(0, os.path.join(path.replace(";", ""), 'resources', 'libs'))

        # SHOULD ONLY BE ENABLED FOR REMOTE DEBUGGING PURPOSES
        # import remotedebugger
        # debugger = remotedebugger.RemoteDebugger()

        import envcontroller
        envController = envcontroller.EnvController()
        env = envController.GetEnvironmentFolder()

        # we do use append here, because it is better to use third party libs
        # instead of the included ones.
        sys.path.append(os.path.join(path.replace(";", ""), 'resources', 'libs', env))
        return path

if __name__ == "__main__":
    init = Initializer.SetupPaths()
