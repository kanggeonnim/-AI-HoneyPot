import mysql

from app.config.config import settings

CATEGORY_LIST = settings.CATEGORY_LIST


def init_keyword_category_table(connection):
    if connection:
        create_keyword_category_table(connection)
        category_list = eval(CATEGORY_LIST)
        for category_name in category_list:
            insert_keyword_category(connection, category_name)
        connection.close()
        print("MySQL connection closed.")


def create_keyword_category_table(connection):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS keyword_category (
                keyword_category_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                category_name VARCHAR(255) NOT NULL
            )
        """)
        connection.commit()
        print("Table 'keyword_category' created successfully!")
    except mysql.connector.Error as e:
        print(f"Error creating video_keyword table: {e}")


def insert_keyword_category(connection, category_name):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("""
            INSERT INTO keyword_category (category_name) VALUES (%s)
        """, (category_name,))
        connection.commit()
        print("Category inserted into keyword_category table successfully!")
    except mysql.connector.Error as e:
        print(f"Error inserting keyword_category: {e}")


def find_category_id_by_category_name(connection, category_name):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("SELECT keyword_category_id FROM keyword_category WHERE category_name = %s", (category_name,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            print("No record found with the given video name.")
            return None
    except mysql.connector.Error as e:
        print(f"Error finding id by video name: {e}")
        return None
