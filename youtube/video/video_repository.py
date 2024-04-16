import mysql


def create_video_table(connection):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video (
                video_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                video_name VARCHAR(255) NOT NULL,
                video_summary VARCHAR(500) NOT NULL,
                video_time VarCHAR(255) NOT NULL,
                video_url VARCHAR(255) NOT NULL,
                image_url VARCHAR(255) NOT NULL,
                hits BIGINT DEFAULT 0 NOT NULL,
                created_at TIMESTAMP DEFAULT NOW() NOT NULL
            )
        """)
        connection.commit()
        print("Table 'video' created successfully!")
    except mysql.connector.Error as e:
        print(f"Error creating table: {e}")


def find_video_id_by_video_name(connection, video_name):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("SELECT video_id FROM video WHERE video_name = %s", (video_name,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            print("No record found with the given video name.")
            return None
    except mysql.connector.Error as e:
        print(f"Error finding id by video name: {e}")
        return None


def insert_file_metadata(connection, video_name, video_summary, video_time, video_url, image_url, created_at):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("""
            INSERT INTO video (video_name, video_summary, video_time, video_url, image_url, created_at) VALUES (%s, %s, %s, %s, %s, %s)
        """, (video_name, video_summary, video_time, video_url, image_url, created_at))
        connection.commit()
        print("File metadata inserted into MySQL database successfully!")
    except mysql.connector.Error as e:
        print(f"Error inserting file metadata: {e}")


def delete_video_no_keywords(connection, video_name):
    try:
        cursor = connection.cursor(buffered=True)
        # cursor.execute("SELECT keyword_category_id FROM keyword_category WHERE category_name = %s", (category_name,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            print("No record found with the given video name.")
            return None
    except mysql.connector.Error as e:
        print(f"Error finding id by video name: {e}")
        return None


def update_videos_time(connection, video_id, video_time):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("""UPDATE video SET video_time = %s WHERE video_id = %s""", (video_time, video_id))
        connection.commit()
    except mysql.connector.Error as e:
        print(f"Error finding id by video name: {e}")
        return None


def find_videos_no_time(connection, video_id):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("SELECT * FROM video WHERE video_time = ''")
        result = cursor.fetchall()
        if result:
            return result
        else:
            print("No record found with the given video name.")
            return None
    except mysql.connector.Error as e:
        print(f"Error finding id by video name: {e}")
        return None
