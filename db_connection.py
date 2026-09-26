import mysql.connector


def get_connection():

    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Viswa@1704",
        database="green_bloom_db"
    )

    return connection