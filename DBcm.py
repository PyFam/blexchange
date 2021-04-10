from mysql.connector import connect, errors

class ConnectionError(Exception): pass
class CredentialsError(Exception):pass
class SQLError(Exception): pass

class UseDB:
    def __init__(self, config):
        self.config = config

    def __enter__(self): # -> 'cursor' -> 'cursor'
        try:
            self.conn = connect(**self.config)
            self.cursor = self.conn.cursor()
            return self.cursor

        except errors.InterfaceError as err:
            return ConnectionError(err)
        except errors.ProgrammingError as err:
            return CredentialsError(err)

    def __exit__(self, exc_type, exc_value, exc_trace):
        self.conn.commit()
        self.conn.close()
        self.cursor.close()
        
        if exc_type is errors.ProgrammingError:
            return SQLError(exc_value)
        elif exc_type:
            return exc_type(exc_value)