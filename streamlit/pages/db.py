import mysql.connector


class DBConnection:
    _instance = None
    
    def __init__(self):
        if DBConnection._instance is not None:
            # Prevent multiple instances
            raise Exception("This class is a singleton!")
        
        # Initialize the connection
        self.connection = mysql.connector.connect(
            host='database-1.cdwumcckkqqt.us-east-1.rds.amazonaws.com',
            user='admin',
            password='amazonrds7245',
            database='gaia_benchmark_dataset_validation'
        )
        self.cursor = self.connection.cursor(buffered=True)  # Create a cursor for the connection
        DBConnection._instance = self
    
    @classmethod
    def get_instance(cls):
        # Create the singleton instance if it doesn't exist
        if cls._instance is None:
            cls._instance = DBConnection()
        return cls._instance

    def get_cursor(self):
        # Return the cursor object
        return self.cursor

    def get_connection(self):
        # Return the connection object if needed
        return self.connection
