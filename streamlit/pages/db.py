import snowflake.connector
import os

class DBConnection:
    _instance = None

    def __init__(self):
        if DBConnection._instance is not None:
            raise Exception("This class is a singleton!")

        # Initialize the Snowflake connection using environment variables
        self.connection = snowflake.connector.connect(
            user=os.getenv('SNOWFLAKE_USER'),
            password=os.getenv('SNOWFLAKE_PASSWORD'),
            account=os.getenv('SNOWFLAKE_ACCOUNT'),
            warehouse=os.getenv('SNOWFLAKE_WAREHOUSE'),
            database=os.getenv('SNOWFLAKE_DATABASE'),
            schema=os.getenv('SNOWFLAKE_SCHEMA')
        )
        DBConnection._instance = self

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = DBConnection()
        return cls._instance

    def get_cursor(self):
        # Create and return a new cursor each time it's called
        return self.connection.cursor()

    def get_connection(self):
        # Return the connection object if needed
        return self.connection

    def close(self):
        # Close the connection and release resources
        if self.connection:
            self.connection.close()
            DBConnection._instance = None
