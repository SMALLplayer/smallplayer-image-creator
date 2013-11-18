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

# some trick to load sqlite3 as default provider but fallback to pysqlite2 if
# sqlite3 is not available.
try:
    from sqlite3 import dbapi2 as sqlite  # @Reimport @UnresolvedImport @UnusedImport
    Logger.Info("Loading sqlite3 as DB engine")
except:
    from pysqlite2 import dbapi2 as sqlite  # @Reimport
    Logger.Info("Loading pysqlite2 as DB engine")

from config import Config
import mediaitem


#===============================================================================
# Database Handler class
#===============================================================================
class DatabaseHandler:
    """Database handler class. Handles SQLLite database actions"""

    def __init__(self):
        """initialize the DB connection"""

        # SQL lite explorer tool:
        # http://www.sqliteexpert.com/

        # get the user profile folder
        Logger.Info("Opening %s as DB", Config.xotDbFile)
        self.xotDatabase = sqlite.connect(Config.xotDbFile)
        self.__CheckDatabaseExistence()
        self.__Encoding = 'utf-8'
        pass

    def __del__(self):
        """ Closes the connection """

        Logger.Info("Closing database connection")
        self.xotDatabase.close()
        pass

    def AddFavorite(self, name, url, channel):
        """Adds a favorite to the favorites table

        Arguments:
        name    : string - Name of the item
        url     : string - Url of the item
        channel : Channel - Channel to which the item belongs.

        Stores the favorites to the favorites list an uses the channel GUID as
        the identifier for the channel.

        """

        Logger.Debug("Adding favorite '%s' for channel '%s' with GUID '%s' and url '%s'", name, channel.channelName, channel.guid, url)

        # we only insert if it really is a new item
        sql = u"INSERT INTO favorites (name, url, guid) SELECT ?, ?, ? WHERE NOT EXISTS (SELECT 1 FROM favorites WHERE name=? AND url=? AND guid=?)"
        params = (name, url, channel.guid, name, url, channel.guid)

        # sql = u"INSERT INTO favorites (name, url, guid) VALUES(?, ?, ?)"
        # params = (name, url, channel.guid)

        self.__ExecuteNonQuery(sql, params=params)

    def LoadFavorites(self, channel):
        """Loads the favorites for the specific channel.

        Arguments:
        channel : Channel - Channel to which the item belongs.

        Looks up the favorite items for the specified channel. The channel is
        identified using it GUID.

        Returns:
        a list of MediaItems that are favorites to the specified channel.

        """

        Logger.Debug("Loading favorites")
        items = []

        self.__UpgradeFrom310(channel)

        sql = "SELECT name, url FROM favorites WHERE guid='%s'" % (channel.guid)
        rows = self.__ExecuteQuery(sql)

        for row in rows:
            item = mediaitem.MediaItem(row[0], row[1])
            items.append(item)

        return items

    def DeleteFavorites(self, name, url, channel):
        """Deletes a favorite belonging to the specified channel.

        Arguments:
        name    : string - Name of the item
        url     : string - Url of the item
        channel : Channel - Channel to which the item belongs.

        """

        Logger.Debug("Deleting favorite %s (%s)", name, url)
        query = "DELETE FROM favorites WHERE name=? AND url=? AND guid=?"
        self.__ExecuteNonQuery(query, commit=True, params=(name, url, channel.guid))
        return

    def __CheckDatabaseExistence(self):
        """Checks if the database exists, if not, it will be created."""

        sql = "PRAGMA table_info('favorites')"
        results = self.__ExecuteQuery(sql)

        # check if DB exists
        if len(results) < 1:
            self.__CreateDatabase()
            # reload the query
            results = self.__ExecuteQuery(sql)

        # Check for GUID column
        columnGuidExists = False
        for result in results:
            if result[1] == "guid":
                Logger.Debug("Database: Guid column already present in favorites table.")
                columnGuidExists = True
                break
        if not (columnGuidExists):
            Logger.Info("Database: Creating column guid")
            sql = "ALTER TABLE favorites ADD COLUMN guid"
            self.__ExecuteNonQuery(sql, commit=True)

    #==============================================================================
    def __CreateDatabase(self):
        """Creates a functional database"""

        Logger.Info("Creating Database")
        sql = 'PRAGMA encoding = "UTF-16"'
        self.__ExecuteNonQuery(sql, True)
        sql = "CREATE TABLE favorites (channel string, name string, url string)"
        self.__ExecuteNonQuery(sql)
        sql = "CREATE TABLE settings (setting string, value string)"
        self.__ExecuteNonQuery(sql)

    #==============================================================================
    def __UpgradeFrom310(self, channel):
        """Upgrades an old database to a more recent one.

        Arguments:
        channel : Channel - the specified channel.

        In this case it updates the favorite items with the channel GUID column.

        """

        sql = "UPDATE favorites SET guid='%s' where channel='%s'" % (channel.guid, channel.channelName)
        self.__ExecuteNonQuery(sql, commit=True)

    def __ExecuteNonQuery(self, query, commit=True, params=[]):
        """Executes and commits (if true) a sql statement to the database.

        Arguments:
        query  : string - the query to execute

        Keyword Arguments:
        commit : boolean        - indicates whether the transaction should be
                                  committed or not.
        params : tupple(string) - the parameters to substitute into the query

        Returns nothing, as it does not expect any results

        """

        # decode to unicode
        uParams = []
        for param in params:
            uParams.append(param.decode(self.__Encoding))

        cursor = self.xotDatabase.cursor()
        if len(params) > 0:
            cursor.execute(query, uParams)
        else:
            cursor.execute(query)

        if commit:
            self.xotDatabase.commit()

        cursor.close()

    def __ExecuteQuery(self, query, commit=False, params=[]):
        """Executs and commits (if true) a sql statement to the database.

        Arguments:
        query  : string - the query to execute

        Keyword Arguments:
        commit : boolean        - indicates whether the transaction should be
                                  committed or not.
        params : tupple(string) - the parameters to substitute into the query

        Returns a row-set.

        """

        # decode to unicode
        uParams = []
        for param in params:
            # uParams.append(param.decode('iso-8859-1'))
            uParams.append(param.decode(self.__Encoding))

        cursor = self.xotDatabase.cursor()
        if len(params) > 0:
            cursor.execute(query, uParams)
        else:
            cursor.execute(query)

        if commit:
            self.xotDatabase.commit()

        results = cursor.fetchall()
        cursor.close()

        return results
