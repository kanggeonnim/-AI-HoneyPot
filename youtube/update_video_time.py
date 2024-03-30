import json
import mysql.connector

from s3 import connect_to_mysql


def find_videos_no_time():
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


if __name__ == '__main__':
    connection = connect_to_mysql()
    video_list = find_videos_no_time()
    for video in video_list:
        print(video)
