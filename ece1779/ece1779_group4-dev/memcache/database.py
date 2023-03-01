from typing import Union
from memcache.logging_config import logger
import mysql.connector
import configparser

from mysql.connector import errorcode, MySQLConnection, CMySQLConnection
from mysql.connector.pooling import PooledMySQLConnection

# SQL for creating table in initialization
TABLES = [
    (
        "CREATE TABLE IF NOT EXISTS memcacheconfig ("
        "id INT(1) NOT NULL,"
        "capacity smallint NOT NULL,"
        "policy enum('LRU', 'RANDOM') NOT NULL,"
        "PRIMARY KEY (id)"
        ") ENGINE=InnoDB"
    ),
    (
        "CREATE TABLE IF NOT EXISTS keypath ("
        "img_key varchar(100) NOT NULL,"
        "img_path text NOT NULL,"
        "PRIMARY KEY (img_key)"
        ") ENGINE=InnoDB"
    ),
    (
        "CREATE TABLE IF NOT EXISTS statistics ("
        "id INT(1) NOT NULL,"
        "hit_rate float NOT NULL,"
        "miss_rate float NOT NULL,"
        "item_num int NOT NULL,"
        "item_size float NOT NULL,"
        "request_num int NOT NULL,"
        "PRIMARY KEY (id)"
        ") ENGINE=InnoDB"
    )
]


def create_db():
    """
    Factory function, create a Database instance used for operating db
    :return: Database
    """
    config = configparser.ConfigParser()
    config.read('memcache/dbconfig.ini')
    db = Database(config.get('db', 'username'),
                  config.get('db', 'password'),
                  config.get('db', 'host'),
                  config.get('db', 'database'))
    db.initialize()
    return db


class Database:
    def __init__(self, username: str, password: str, host: str, database: str) -> None:
        self._username = username
        self._password = password
        self._host = host
        self._database = database

    def initialize(self) -> bool:
        """
        Initialize Database Connection:
        1. Verify username and passwd
        2. Test if DB exists, if not, create one
        3. Test if all tables exist, if not, create
        4. Test if the db connection can be established successfully
        :return: None
        """
        try:
            cnx = None
            cnx = mysql.connector.connect(user=self._username,
                                          password=self._password,
                                          host=self._host,
                                          database=self._database)
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logger.error("Something is wrong with your user name or password")
                exit(1)
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logger.info("Database does not exist. \nCreating now!")
                self._create_db()

            else:
                logger.error(err)
                exit(1)
        finally:
            self._create_tables()
            if cnx:
                self._disconnect_db(cnx)

    def _create_db(self):
        """
        Create a database in MySQL
        :return: None
        """
        cnx = mysql.connector.connect(user=self._username,
                                      password=self._password,
                                      host=self._host)
        cursor = cnx.cursor()
        try:
            cursor.execute(
                "CREATE DATABASE {} DEFAULT CHARACTER SET 'utf8'".format(self._database))
        except mysql.connector.Error as err:
            logger.error("Failed creating database: {}".format(err))
            exit(1)
        else:
            self._disconnect_db(cnx, cursor)

    def _create_tables(self):
        """
        Create all tables required by this project in database
        :return: None
        """
        cnx = self._connect_db()
        cursor = cnx.cursor()
        try:
            cursor.execute('USE ' + self._database)

            for table in TABLES:
                cursor.execute(table)
            cnx.commit()

            # insert a row if empty in statistics or memcacheconfig
            if not self.query_statistics():
                cursor.execute("INSERT INTO statistics "
                               "VALUES (%s, %s, %s, %s, %s, %s)", (0, 0., 0., 0, 0., 0))
                cnx.commit()
            if not self.query_memcacheconfig():
                cursor.execute("INSERT INTO memcacheconfig "
                               "VALUES (%s, %s, %s)", (0, 100, 'RANDOM'))
                cnx.commit()

        except mysql.connector.Error as err:
            logger.error(err.msg)
        else:
            logger.info("Creating Tables Successfully!")
        self._disconnect_db(cnx, cursor)

    def _connect_db(self) -> Union[PooledMySQLConnection, MySQLConnection, CMySQLConnection]:
        """
        Establish Database connection
        :return: Union[PooledMySQLConnection, MySQLConnection, CMySQLConnection]
        """
        try:
            return mysql.connector.connect(user=self._username,
                                           password=self._password,
                                           host=self._host,
                                           database=self._database)
        except mysql.connector.Error as err:
            logger.error(err)
            exit(1)

    def _disconnect_db(self, cnx, cursor=None):
        """
        Disconnect a Database connection and cursor connection
        :param cnx: Union[PooledMySQLConnection, MySQLConnection, CMySQLConnection]
        :param cursor: MySQLCursor
        :return: None
        """
        try:
            if cursor:
                cursor.close()
            if cnx:
                cnx.close()

        except Exception as e:
            logger.error('Disconnect Fail: ', str(e))

    def add_keypath(self, key: str, path: str) -> bool:
        """
        Add a key/path pair to keypath table. If the key exists, modify
        existing row, else, add new row
        :param key: key: str
        :param path: image path: str
        :return: bool
        """
        cnx = self._connect_db()
        cursor = cnx.cursor()
        command = ("INSERT INTO keypath "
                   "VALUES (%s, %s)")
        data = (key, path)
        try:
            cursor.execute(command, data)
            cnx.commit()
            self._disconnect_db(cnx, cursor)
        except Exception as e:
            logger.error("Insert Fail: ", str(e))
            return False
        else:
            return True

    def query_keypath(self, key=None):
        """
        Query the corresponding image path by a key. If not exist, return []
        :param key: image key
        :return: List[str]
        """
        cnx = self._connect_db()
        cursor = cnx.cursor()

        if key:
            query = ("SELECT * FROM keypath WHERE img_key = '{}'".format(key))
            cursor.execute(query)
        else:
            cursor.execute('SELECT * FROM keypath')

        ret = list(cursor)
        self._disconnect_db(cnx, cursor)
        return ret

    def update_keypath(self, key, path):
        """
        Modify the path column in keypath table with a key
        :param key: image_key
        :param path: new path
        :return: None
        """
        cnx = self._connect_db()
        cursor = cnx.cursor()
        try:
            query = "UPDATE keypath SET img_path = '{}' WHERE img_key = '{}'".format(path, key)
            logger.info(query)
            cursor.execute(query)
            cnx.commit()
            self._disconnect_db(cnx, cursor)
        except Exception as e:
            logger.error("Update Fail: ", str(e))

    def clear_keypath(self):
        """
        Clear keypath table means delete all keys and paths
        :return: None
        """
        cnx = self._connect_db()
        cursor = cnx.cursor()
        try:
            cursor.execute('DELETE FROM keypath')
            cnx.commit()
            self._disconnect_db(cnx, cursor)
        except Exception as e:
            logger.error("Clear Fail: ", str(e))

    def update_statistics(self, data):
        """
        Update stats data in table statistics
        :param data: A list of stats result
        :return:
        """
        cnx = self._connect_db()
        cursor = cnx.cursor()
        try:
            query = "UPDATE statistics " \
                    "SET hit_rate = %s," \
                    "    miss_rate = %s," \
                    "    item_num = %s," \
                    "    item_size = %s," \
                    "    request_num = %s WHERE id = 0"

            cursor.execute(query, tuple(data))
            cnx.commit()
            self._disconnect_db(cnx, cursor)
        except Exception as e:
            logger.error("Update Fail: ", str(e))

    def query_statistics(self):
        """
        Get stats from db
        :return: List
        """
        cnx = self._connect_db()
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM statistics")
        ret = list(cursor)
        self._disconnect_db(cnx, cursor)
        return ret

    def update_memcacheconfig(self, data):
        """
        Update memcache config  in table memcacheconfig
        :param data: List
        :return: None
        """
        cnx = self._connect_db()
        cursor = cnx.cursor()
        try:
            query = "UPDATE memcacheconfig " \
                    "SET capacity = %s," \
                    "    policy = %s WHERE id = 0"

            cursor.execute(query, tuple(data))
            cnx.commit()
            self._disconnect_db(cnx, cursor)
        except Exception as e:
            logger.error("Update Fail: ", str(e))

    def query_memcacheconfig(self):
        """
        Get memcache config
        :return: List
        """
        cnx = self._connect_db()
        cursor = cnx.cursor()
        cursor.execute("SELECT * FROM memcacheconfig")
        ret = list(cursor)
        self._disconnect_db(cnx, cursor)
        return ret


