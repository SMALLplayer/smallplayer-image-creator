#===============================================================================
# LICENSE XOT-Framework - CC BY-NC-ND
#===============================================================================
# This work is licenced under the Creative Commons
# Attribution-Non-Commercial-No Derivative Works 3.0 Unported License. To view a
# copy of this licence, visit http://creativecommons.org/licenses/by-nc-nd/3.0/
# or send a letter to Creative Commons, 171 Second Street, Suite 300,
# San Francisco, California 94105, USA.
#===============================================================================

import urllib2


class ProxyInfo:
    def __init__(self, proxy, port, scheme="http", username="", password=""):
        """ Retrieves a new ProxyInfo object

        Arguments:
        proxy:    String - Name or IP of the Proxy server
        port:     Int    - The port of the proxy server

        Keyword Arguments:
        scheme:   String - [opt] The type of proxy (http is default)
        username: String - [opt] The username to use (if empty or ommitted no
                           authentication is done.
        password: String - [opt] The password to use.

        """

        self.Proxy = proxy
        self.Port = int(port)
        self.Scheme = scheme
        self.Username = username
        self.Password = password

    def GetSmartProxyHandler(self):
        """ Gets a Proxy Handler  based on the settings """

        if self.Proxy == "":
            proxyHandler = urllib2.ProxyHandler({})
        elif self.__IsSecure():
            proxyHandler = urllib2.ProxyHandler({self.Scheme: "%s://%s:%s@%s:%s" % (self.Scheme, self.Username, self.Password, self.Proxy, self.Port)})
        else:
            proxyHandler = urllib2.ProxyHandler({self.Scheme: "%s://%s:%s" % (self.Scheme, self.Proxy, self.Port)})
        return proxyHandler

    def __IsSecure(self):
        """ An easy way of determining if this server should use proxy authentication."""

        return not self.Username == ""

    def __str__(self):
        """ returns a string representation """

        if self.__IsSecure():
            if self.Password == "":
                password = self.Password
            else:
                password = "********"
            return "Proxy (%s): %s://%s:%s@%s:%s" % (self.Scheme, self.Scheme, self.Username, password, self.Proxy, self.Port)

        return "Proxy (%s): %s://%s:%s" % (self.Scheme, self.Scheme, self.Proxy, self.Port)
