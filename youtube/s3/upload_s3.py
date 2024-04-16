import os
import uuid
from datetime import datetime

import boto3
import cv2

from botocore.exceptions import ClientError  # boto3에서 발생하는 예외를 처리하기 위해 추가
from app.config.config import settings
from youtube.core.db import connect_to_mysql
from youtube.keyword_category.keyword_category_repository import find_category_id_by_category_name
from youtube.video.video_repository import create_video_table, insert_file_metadata, find_video_id_by_video_name
from youtube.video.video_service import get_video_created_at, format_video_created_at, get_video_time
from youtube.video_keyword.video_keyword_repository import create_keyword_table, insert_keyword

AWS_ACCESS_KEY_ID = settings.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = settings.AWS_SECRET_ACCESS_KEY
AWS_DEFAULT_REGION = settings.AWS_DEFAULT_REGION
AWS_CLOUD_FRONT = settings.AWS_CLOUD_FRONT

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


def generate_thumbnail(video_path, thumbnail_path, time_in_seconds):
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, time_in_seconds * 1000)
    success, image = cap.read()
    if success:
        cv2.imwrite(thumbnail_path, image)
        print("Thumbnail generated successfully.")
    else:
        print("Failed to generate thumbnail.")


def upload_s3():
    dir_list = os.listdir(clip_path)
    for path in dir_list:
        if path.endswith('.mp4'):
            try:
                # S3에 파일 업로드
                unique_id = generate_unique_id()
                video_path = f'../whisper/src/clip_video/{path}'
                image_path = f'../whisper/src/image/{unique_id}.jpg'
                bucket = 'yeouido-honeypot'
                video_url = f'videos/{unique_id}.mp4'
                image_url = f'images/{unique_id}.jpg'
                # thumnail 생성
                generate_thumbnail(video_path, f'{image_path}', 10)  # 10초 시점의 썸네일 생성

                video_time = get_video_time(video_path)

                # 영상 업로드
                video_upload_successful = upload_file_to_s3(video_path, bucket, video_url)
                # thumnail 업로드
                image_upload_successful = upload_file_to_s3(image_path, bucket, image_url)

                # if True:
                if video_upload_successful and image_upload_successful:
                    # MySQL 연결
                    connection = connect_to_mysql()
                    if connection:
                        # keyword를 저장하는 테이블 생성
                        create_keyword_table(connection)

                        # 테이블 생성
                        create_video_table(connection)

                        # KEYWORD 파일 열기
                        with open(script_path + "[KEYWORD]" + path[:-4] + ".txt", "r", encoding="utf-8") as file:
                            file_contents = file.read()

                        # 영상의 요약내용 추출
                        summary = file_contents.split("\n")[1]

                        # 비디오 생성시간
                        video_created_at = datetime.strptime(get_video_created_at(video_path), '%Y-%m-%dT%H:%M:%S.%fZ')
                        # video_created_at = format_video_created_at(video_created_at)
                        # print(video_created_at)
                        # 파일 메타데이터 삽입
                        insert_file_metadata(connection, path[:-4], summary, video_time, AWS_CLOUD_FRONT + video_url,
                                             AWS_CLOUD_FRONT + image_url, video_created_at)

                        video_id = find_video_id_by_video_name(connection, path[:-4])

                        if video_id:
                            # 키워드 속성 추출 : {}로 감싸진 부분 추출
                            start_index = file_contents.find('{')
                            end_index = file_contents.rfind('}')
                            extracted_part = file_contents[start_index:end_index + 1]
                            # dictionary 형식으로 변환
                            dictionary_data = eval(extracted_part)

                            # 키워드 저장
                            for key, value in dictionary_data.items():
                                category_id = find_category_id_by_category_name(connection, value)
                                # print(f'Key: {key}, Value: {value} for category: {category_id}')

                                # 카테고리 아이디가 존재하지 않는다면 기타로 분류
                                if not category_id:
                                    category_id = 1

                                # 키워드 카테고리 부여
                                insert_keyword(connection, video_id, key, category_id)

                        # 연결 종료
                        connection.close()
                        print("MySQL connection closed.")
            except Exception as e:
                print(e)
                print(f"An error occurred: {e}")


def keyword_fix(connection, video_id):
    # KEYWORD 파일 열기
    with open("whisper/script/[KEYWORD]한동훈 국민의힘 비상대책위원장 취임 한 달.txt", "r", encoding="utf-8") as file:
        file_contents = file.read()

    video_id = find_video_id_by_video_name(connection, "한동훈 국민의힘 비상대책위원장 취임 한 달")

    if video_id:
        # 키워드 속성 추출 : {}로 감싸진 부분 추출
        start_index = file_contents.find('{')
        end_index = file_contents.rfind('}')
        extracted_part = file_contents[start_index:end_index + 1]
        # dictionary 형식으로 변환
        try:
            dictionary_data = eval(extracted_part)
        except Exception as e:

            # JSON 파싱 실패 시, 문법 오류를 수정하여 JSON 파일로 변환
            fixed_content = file_contents.strip()[:-4] + ",\n" + file_contents.strip()[-3]
            # fixed_content = fixed_content.strip()[:-3] + ",\n" + fixed_content.strip()[-2]
            print(fixed_content)
            # 수정된 내용을 파일에 다시 쓰기
            with open("whisper/script/[KEYWORD]한동훈 국민의힘 비상대책위원장 취임 한 달.txt", 'w', encoding='utf-8') as file:
                file.write(fixed_content)
            print(f"파일이(가) 수정되었습니다.")

        # 키워드 저장
        # for key, value in dictionary_data.items():
        #     category_id = find_category_id_by_category_name(connection, value)
        #     insert_keyword(connection, video_id, key, category_id)
    # 연결 종료
    connection.close()
    print("MySQL connection closed.")


if __name__ == "__main__":
    # print(get_video_time("../youtube/whisper/clip_video/철도지화화 경쟁.mp4"))

    # 키워드 카테고리 테이블 초기화.
    # init_keyword_category_table()
    # upload_s3()
    # unique_id = generate_unique_id()
    # generate_thumbnail(f'./whisper/clip_video/민생 공약과 선거 전략.mp4', f'./whisper/image/{unique_id}.jpg', 10)  # 10초 시점의 썸네일 생성
    #
    # image_upload_successful = upload_file_to_s3(f'./whisper/image/{unique_id}.jpg', 'yeouido-honeypot',
    #                                             f'images/{unique_id}.jpg')

    keyword_fix()
    # generate_thumbnail("./whisper/clip_video/민생 공약과 선거 전략.mp4", generate_unique_id() + ".jpg", 10)  # 10초 시점의 썸네일 생성
