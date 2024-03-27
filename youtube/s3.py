import os
import uuid
import boto3
import mysql.connector
import cv2

from botocore.exceptions import ClientError  # boto3에서 발생하는 예외를 처리하기 위해 추가
from openai import OpenAI

from ai.app.config.config import settings

AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION = settings.AWS_DEFAULT_REGION
AWS_CLOUD_FRONT = settings.AWS_CLOUD_FRONT

DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_DATABASE = settings.DB_DATABASE

clip_path = settings.CLIP_FILE_PATH
script_path = settings.SCRIPT_FILE_PATH


def s3_connection():
    try:
        s3 = boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY_ID,
                          aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                          region_name=AWS_DEFAULT_REGION)
        print("S3 bucket connected!")
        return s3
    except Exception as e:
        print(f"Error connecting to S3 bucket: {e}")
        return None


def generate_unique_id():
    return str(uuid.uuid4())  # UUID를 문자열로 변환하여 반환


def check_id_duplicate(unique_id):
    # 중복 여부 확인 로직
    return False  # 중복되지 않은 경우


def upload_file_to_s3(file_name, bucket, key):
    try:
        s3 = s3_connection()
        if s3:
            s3.upload_file(file_name, bucket, key)  # 파일 저장
            print("File uploaded to S3 successfully!")
            return True
        else:
            return False
    except ClientError as e:
        print(f"Error uploading file to S3: {e}")
        return False


def connect_to_mysql():

    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            port=DB_PORT,
            password=DB_PASSWORD,
            database=DB_DATABASE
        )
        print("Connected to MySQL database!")
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None


def create_table(connection):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video (
                video_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                video_name VARCHAR(255) NOT NULL,
                video_url VARCHAR(255) NOT NULL,
                image_url VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT NOW() NOT NULL
            )
        """)
        connection.commit()
        print("Table 'video' created successfully!")
    except mysql.connector.Error as e:
        print(f"Error creating table: {e}")


def insert_file_metadata(connection, video_name, video_url, image_url):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("""
            INSERT INTO video (video_name, video_url, image_url) VALUES (%s, %s, %s)
        """, (video_name, video_url, image_url))
        connection.commit()
        print("File metadata inserted into MySQL database successfully!")
    except mysql.connector.Error as e:
        print(f"Error inserting file metadata: {e}")


def generate_thumbnail(video_path, thumbnail_path, time_in_seconds):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, time_in_seconds * 1000)
    success, image = cap.read()
    if success:
        cv2.imwrite(thumbnail_path, image)
        print("Thumbnail generated successfully.")
    else:
        print("Failed to generate thumbnail.")


def find_id_by_video_name(connection, video_name):
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


def create_keyword_table(connection):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS video_keyword (
                video_keyword_id BIGINT AUTO_INCREMENT PRIMARY KEY,
                video_id BIGINT NOT NULL,
                keyword VARCHAR(255) NOT NULL,
                FOREIGN KEY (video_id) REFERENCES video(video_id)
            )
        """)
        connection.commit()
        print("Table 'video_keyword' created successfully!")
    except mysql.connector.Error as e:
        print(f"Error creating keyword table: {e}")


def insert_keyword(connection, video_id, keyword):
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("""
            INSERT INTO video_keyword (video_id, keyword) VALUES (%s, %s)
        """, (video_id, keyword))
        connection.commit()
        print("Keyword inserted into keyword table successfully!")
    except mysql.connector.Error as e:
        print(f"Error inserting keyword: {e}")


def upload_s3():
    dir_list = os.listdir(clip_path)
    for path in dir_list:
        if path.endswith('.mp4'):
            try:
                # S3에 파일 업로드
                unique_id = generate_unique_id()
                video_path = f'./whisper/clip_video/{path}'
                image_path = f'./whisper/image/{unique_id}.jpg'
                bucket = 'yeouido-honeypot'
                video_url = f'videos/{unique_id}.mp4'
                image_url = f'images/{unique_id}.jpg'
                # thumnail 생성
                generate_thumbnail(video_path, f'{image_path}', 10)  # 10초 시점의 썸네일 생성

                # 영상 업로드
                video_upload_successful = upload_file_to_s3(video_path, bucket, video_url)
                # thumnail 업로드
                image_upload_successful = upload_file_to_s3(image_path, bucket, image_url)

                # if True:
                if video_upload_successful and image_upload_successful:
                    # MySQL 연결
                    connection = connect_to_mysql()
                    if connection:
                        # 테이블 생성
                        create_table(connection)

                        # 파일 메타데이터 삽입
                        insert_file_metadata(connection, path, AWS_CLOUD_FRONT + video_url, AWS_CLOUD_FRONT + image_url)

                        video_id = find_id_by_video_name(connection, path)

                        if video_id:
                            # keyword를 저장하는 테이블 생성
                            create_keyword_table(connection)
                            dir_list = os.listdir(script_path)
                            # 파일을 읽어서 문자열로 저장
                            with open(script_path + "[KEYWORD]" + path[:-4] + ".txt", "r",
                                      encoding="utf-8") as file:
                                file_contents = file.read()

                            keyword_list = eval(file_contents)
                            print(keyword_list)
                            for keyword in keyword_list:
                                # 키워드 저장
                                insert_keyword(connection, video_id, keyword)
                        # 연결 종료
                        connection.close()
                        print("MySQL connection closed.")
            except Exception as e:
                print(f"An error occurred: {e}")


if __name__ == "__main__":
    upload_s3()
    # unique_id = generate_unique_id()
    # generate_thumbnail(f'./whisper/clip_video/민생 공약과 선거 전략.mp4', f'./whisper/image/{unique_id}.jpg', 10)  # 10초 시점의 썸네일 생성
    #
    # image_upload_successful = upload_file_to_s3(f'./whisper/image/{unique_id}.jpg', 'yeouido-honeypot',
    #                                             f'images/{unique_id}.jpg')

    # generate_thumbnail("./whisper/clip_video/민생 공약과 선거 전략.mp4", generate_unique_id() + ".jpg", 10)  # 10초 시점의 썸네일 생성
