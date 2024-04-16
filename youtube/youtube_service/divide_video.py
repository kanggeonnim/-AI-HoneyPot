import os
import re

import ffmpeg
from moviepy.video.io.VideoFileClip import VideoFileClip

from app.config.config import settings
from youtube.video.video_service import get_video_created_at
from youtube.youtube_service.summary_script import summary_script

video_path = settings.VIDEO_FILE_PATH
audio_path = settings.AUDIO_FILE_PATH
script_path = settings.SCRIPT_FILE_PATH
clip_path = settings.CLIP_FILE_PATH
image_path = settings.IMAGE_FILE_PATH


def time_formatter(only_second):
    try:
        idx = only_second.find('.')
        if idx == -1:
            raise ValueError("Invalid time format: missing '.'")
        second = only_second[:idx]
        minutes, seconds = divmod(int(second), 60)
        hours, minutes = divmod(minutes, 60)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    except ValueError as ve:
        print(f"ValueError: {ve}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def divide_video():
    dir_list = os.listdir(script_path)
    for path in dir_list:
        if not path.startswith("[KEYWORD]"):
            sum_result = summary_script(script_path + path[:-4] + ".txt")
            sum_list = sum_result.split("\n")

            video_created_at = get_video_created_at(video_path + path[:-4] + ".mp4")
            print(video_created_at)

            line1 = ""
            line2 = ""
            for (index, line) in enumerate(sum_list):
                sort_line = line.replace(" ", "")

                # 개행에 대한 처리
                if len(sort_line) == 0:
                    continue

                if sort_line[0].isdigit():
                    line1 = line + ""
                elif sort_line.startswith("-"):
                    line2 = line + ""

                    # 키워드 추출
                    keyword_start = line1.find('키워드:') + 5
                    keyword_end = line1[keyword_start:].find(')') + keyword_start
                    keyword_list = line1[keyword_start:keyword_end].split(', ')

                    # 시간 추출
                    time_start = line2.find('시작:')
                    time_end = line2.find('끝:')
                    start_time = time_formatter(line2[time_start + 4:time_end - 2])
                    end_time = time_formatter(line2[time_end + 3: -1])

                    sub_end = re.search(r'\d+\.', line1).end()
                    sub = line1[sub_end + 1:keyword_start - 7]

                    summary = line2[line2.find('-') + 2:time_start - 2]
                    # print(f'제목-{sub}')
                    # print(f'시작-{start_time}')
                    # print(f'끝-{end_time}')
                    # print(f'요약-{summary}')
                    # print(keyword_list)

                    try:
                        f = open(script_path + "[KEYWORD]" + sub + ".txt", "w", encoding="utf-8")
                        f.write(str(keyword_list) + '\n')
                        f.write(summary + '\n')
                        f.close()
                    except Exception as e:
                        print(e)
                        print("Fail to Create KEYWORD: " + path[:-4])

                    try:
                        clip_video_path = clip_path + sub + ".mp4"
                        clip_video = VideoFileClip(video_path + path[:-4] + ".mp4").subclip(start_time, end_time)
                        clip_video.write_videofile(clip_video_path, codec='libx264',
                                                   ffmpeg_params=['-metadata', 'creation_time=' + video_created_at])
                        print("clipvideo created successfully")
                        print("updated creation time: " + get_video_created_at(clip_video))
                    except Exception as e:
                        print(e)
                        print("Fail to Edit VIDEO: " + path[:-4] + ".mp4")


if __name__ == "__main__":
    divide_video()
