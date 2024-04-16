import mysql.connector


def create_keyword_table(connection):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_keyword (
                video_keyword_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                video_id BIGINT NOT NULL,
                keyword_name VARCHAR(255) NOT NULL,
                keyword_category_id BIGINT NOT NULL,
                FOREIGN KEY (video_id) REFERENCES video(video_id),
                FOREIGN KEY (keyword_category_id) REFERENCES keyword_category(keyword_category_id)
            )
        """)
        connection.commit()
        print("Table 'video_keyword' created successfully!")
    except mysql.connector.Error as e:
        print(f"Error creating video_keyword table: {e}")


def insert_keyword(connection, video_id, keyword_name, keyword_category_id):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("""
            INSERT INTO video_keyword (video_id, keyword_name, keyword_category_id) VALUES (%s, %s, %s)
        """, (video_id, keyword_name, keyword_category_id))
        connection.commit()
        print("Keyword inserted into video_keyword table successfully!")
    except mysql.connector.Error as e:
        print(f"Error inserting video_keyword: {e}")
