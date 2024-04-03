import datetime
import os
import cv2
import ffmpeg

from youtube import s3
from youtube.video.video_repository import find_videos_no_time, update_videos_time


def update_video_time(connection):
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


def delete_file(file):
    try:
        if os.path.isfile(file):
            os.remove(file)
            print(f"File '{file}' has been successfully deleted.")
        else:
            print(f"File '{file}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def get_video_time(video_path):
    # create video capture object
    data = cv2.VideoCapture(video_path)

    # count the number of frames
    frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
    fps = data.get(cv2.CAP_PROP_FPS)

    # calculate duration of the video
    seconds = round(frames / fps)
    video_time = datetime.timedelta(seconds=seconds)
    print(f"duration in seconds: {seconds}")
    print(f"video time: {video_time}")
    return video_time


def get_video_created_at(video_path):
    vid = ffmpeg.probe(video_path)
    return vid['streams'][0]['tags']['creation_time']


def format_video_created_at(video_created_at):
    return video_created_at.strftime('%Y-%m-%dT%H:%M:%S') + ('-%02d' % (video_created_at.microsecond / 10000))
