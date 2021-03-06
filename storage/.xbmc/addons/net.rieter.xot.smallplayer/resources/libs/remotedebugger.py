#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================


# noinspection PyUnresolvedReferences
class RemoteDebugger:
    """Remote debugger class for PyDev"""

    def __init__(self):
        """Initialises a new remote debugger. If no server is listening, the
        script continues without any debugging.

        """

        print 'Starting RemoteDebugger'
        REMOTE_DBG = True
        # append pydev remote debugger
        if REMOTE_DBG:
            # Make pydev debugger works for auto reload.
            # Note pydevd module need to be copied in XBMC\system\python\Lib\pysrc
            try:
                # import pysrc.pydevd as pydevd  # : PyDev remote debugger
                from pydevd import pydevd  # : PyCharm remote debugger

                # stdoutToServer and stderrToServer redirect stdout and stderr to eclipse console
                pydevd.settrace('localhost', stdoutToServer=True, stderrToServer=True, suspend=False)

                # import ptvsd
                # ptvsd.enable_attach(secret='')
                # ptvsd.wait_for_attach(timeout=10)
            except ImportError:
                print ("Debugger: Error you must add org.python.pydev.debug.pysrc to your PYTHONPATH.")
                raise
            except SystemExit:
                print ("Debugger: exited with SystemExit error")
                raise
            except Exception:
                print ("Debugger: exited with Unknown error")
                raise
