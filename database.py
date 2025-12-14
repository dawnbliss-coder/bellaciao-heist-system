import pymysql
import os
from contextlib import contextmanager

class Database:
    def __init__(self, host='localhost', user='root', password='', database='bellaciao_db'):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        connection = None
        try:
            connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=False
            )
            yield connection
        except pymysql.Error as e:
            print(f"Database error: {e}")
            if connection:
                connection.rollback()
            raise
        finally:
            if connection:
                connection.close()
    
    def execute_query(self, query, params=None, fetch=True):
        """Execute a query and return results"""
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params or ())
                if fetch:
                    return cursor.fetchall()
                else:
                    conn.commit()
                    return cursor.rowcount
    
    def execute_insert(self, query, params=None):
        """Execute an insert query"""
        return self.execute_query(query, params, fetch=False)
    
    def execute_update(self, query, params=None):
        """Execute an update query"""
        return self.execute_query(query, params, fetch=False)
    
    def execute_delete(self, query, params=None):
        """Execute a delete query"""
        return self.execute_query(query, params, fetch=False)
