import uuid
import boto3
import mysql.connector
import cv2
from moviepy.editor import VideoFileClip

from botocore.exceptions import ClientError  # boto3에서 발생하는 예외를 처리하기 위해 추가
from ai.app.config.config import settings

AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION = settings.AWS_DEFAULT_REGION


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
            host='127.0.0.1',
            user='root',
            password='1234',
            database='db'
        )
        print("Connected to MySQL database!")
        return connection
    except mysql.connector.Error as e:
        print(f"Error connecting to MySQL database: {e}")
        return None


def create_table(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS s3_files (
                id INT AUTO_INCREMENT PRIMARY KEY,
                file_name VARCHAR(255) NOT NULL,
                s3_key VARCHAR(255) NOT NULL
            )
        """)
        connection.commit()
        print("Table 's3_files' created successfully!")
    except mysql.connector.Error as e:
        print(f"Error creating table: {e}")


def insert_file_metadata(connection, file_name, s3_key):
    try:
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO s3_files (file_name, s3_key) VALUES (%s, %s)
        """, (file_name, s3_key))
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

def main():
    try:
        # S3에 파일 업로드
        unique_id = generate_unique_id()
        file_name = './whisper/clip_video/이종섭 호주대사 임명과 관련된 논란.mp4'
        bucket = 'yeouido-honeypot'
        key = f'videos/{unique_id}이종섭 호주대사 임명과 관련된 논란.mp4'
        upload_successful = upload_file_to_s3(file_name, bucket, key)

        if upload_successful:
            # MySQL 연결
            connection = connect_to_mysql()
            if connection:
                # 테이블 생성
                create_table(connection)

                # 파일 메타데이터 삽입
                insert_file_metadata(connection, file_name, key)

                # 연결 종료
                connection.close()
                print("MySQL connection closed.")

        else:
            print("Failed to upload file to S3.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    # main()
    # 예시 사용법
    generate_thumbnail("./whisper/clip_video/선거운동 규정 변화와 이에 따른 영향.mp4", "./whisper/clip_video/선거운동영향.jpg",
                       10)  # 10초 시점의 썸네일 생성
