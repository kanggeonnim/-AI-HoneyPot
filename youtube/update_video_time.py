import json
import subprocess

import boto3
import mysql.connector
from botocore.config import Config

from app.config.config import settings
from s3 import connect_to_mysql, s3_connection, get_video_time
from youtube import delete_file


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


def update_videos_time(video_id, video_time):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("""UPDATE video SET video_time = %s WHERE video_id = %s""", (video_time, video_id))
        connection.commit()
    except mysql.connector.Error as e:
        print(f"Error finding id by video name: {e}")
        return None


if __name__ == '__main__':
    connection = connect_to_mysql()
    s3 = s3_connection()

    video_list = find_videos_no_time()
    for video in video_list:
        # video_key = "videos/b547eefa-cb08-4c8c-9eef-267e8c0b44ce.mp4"
        video_key = video[3][video[3].find('videos'):]
        video_name = video[1]
        video_id = video[0]
        print(video_key)
        print(video_name)
        print(video_id)
        bucket = 'yeouido-honeypot'
        download_path = "s3/" + video_name + '.mp4'

        s3.download_file(bucket, video_key, download_path)
        video_time = get_video_time(download_path)
        print(video_time)

        delete_file(download_path)

        update_videos_time(video_id, video_time)
