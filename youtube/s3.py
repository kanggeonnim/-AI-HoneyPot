import boto3

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
    except Exception as e:
        print(e)
    else:
        print("s3 bucket connected!")
        return s3


s3 = s3_connection()

file_name = './whisper/audio/개혁신당의 내부 갈등과 정치적 실험.mp4'  # 업로드할 파일 이름
bucket = 'yeouido-honeypot'  # 버켓 주소
key = '/videos/개혁신당의 내부 갈등과 정치적 실험.mp4'  # s3 파일 이미지

result = s3.upload_file(file_name, bucket, key)  # 파일 저장
print(result)


# result = s3.download_file(bucket, key, file_name)
# print(result)
