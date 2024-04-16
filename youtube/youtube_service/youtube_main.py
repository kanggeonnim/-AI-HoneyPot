import os
import re
from datetime import datetime

import whisperx
from moviepy.editor import VideoFileClip
from openai import OpenAI
from pytube import YouTube

from app.config.config import settings
from view_youtube_list import get_youtube_list_playlist, get_youtube_list_lastest
from youtube.s3.upload_s3 import upload_s3
from youtube.video.video_service import delete_file
from youtube.youtube_service.divide_video import divide_video

os.environ['PATH'] += os.pathsep + 'C:/Program Files/ffmpeg-6.1.1-full_build-shared/bin'

video_path = settings.VIDEO_FILE_PATH
audio_path = settings.AUDIO_FILE_PATH
script_path = settings.SCRIPT_FILE_PATH
clip_path = settings.CLIP_FILE_PATH
image_path = settings.IMAGE_FILE_PATH


def download_list():
    # youtube_list = get_youtube_list_playlist()
    youtube_list = get_youtube_list_lastest()
    for link in youtube_list:
        download_video(link)
    print(youtube_list)


def download_video(path):
    video_url = 'https://www.youtube.com/watch?v=' + path
    yt = YouTube(video_url)

    # 쇼츠는 제외
    if yt.length <= 150 or yt.length > 2400:
        return
    print(yt)

    try:
        yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(
            video_path)
    except Exception as e:
        print(e)
        print("No video: " + video_url)


def video_to_audio():
    dir_list = os.listdir(video_path)
    for path in dir_list:
        if path.endswith('.mp4'):
            # 특수문자제거
            # save_path = re.sub(r"[^.\uAC00-\uD7A30-9a-zA-Z\s]", "", path)
            try:
                video = VideoFileClip(video_path + path)
                video.audio.write_audiofile(audio_path + path[:-4] + ".mp3")
            except Exception as e:
                print(f'Could not convert {path} to audio file \n{e}')


def audio_to_text_model():
    dir_list = os.listdir(audio_path)
    for path in dir_list:
        print(path)
        device = "cuda"
        # audio_file = "./whisper/audio/육아휴직 중 해외 여행 부정 수급일까 shorts.mp3"  # audio_path + path
        audio_file = audio_path + path
        batch_size = 4  # reduce if low on GPU mem
        compute_type = "int8"  # change to "int8" if low on GPU mem (may reduce accuracy)

        # 1. Transcribe with original whisper (batched)
        model = whisperx.load_model("large-v2", device, compute_type=compute_type, language="ko",
                                    download_root="./whisper/model")

        # save model to local path (optional)
        # model_dir = "/path/"
        # model = whisperx.load_model("large-v2", device, compute_type=compute_type, download_root=model_dir)
        audio = whisperx.load_audio(audio_file)
        result = model.transcribe(audio, batch_size=batch_size)

        print(result["segments"])  # before alignment
        print(result)

        # save scripts
        f = open(script_path + path[:-4] + ".txt", "w", encoding="utf-8")
        f.write(str(result))
        f.close()

        # delete audio
        # delete_file(audio_file)


def get_keyword_category(keyword_list):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # 모델 - GPT 3.5 Turbo 선택
    model = "gpt-3.5-turbo-0125"

    pre_prompt = settings.GPT_PROMPT_KEYWORD
    # 메시지 설정
    messages = [{
        "role": "user",
        "content": pre_prompt + str(keyword_list),
    }]

    # ChatGPT API 호출
    response = client.chat.completions.create(
        model=model,
        messages=messages
    )
    openai_result = response.choices[0].message.content

    return openai_result


def get_keyword_category_list():
    dir_list = os.listdir(script_path)
    for path in dir_list:
        if path.startswith("[KEYWORD]"):
            with open(script_path + path, "r", encoding="utf-8") as file:
                file_contents = file.read()

            content = file_contents[:file_contents.find(']') + 1]

            # 카테고리 추출
            keyword_list = eval(content)

            with open(script_path + path, "a", encoding="utf-8") as file:
                file.write('\n' + get_keyword_category(keyword_list) + '\n')


def delete_all_files_in_directory(directory):
    dir_list = os.listdir(directory)
    for path in dir_list:
        delete_file(os.path.join(directory, path))


def delete_all_files():
    delete_all_files_in_directory(audio_path)
    delete_all_files_in_directory(script_path)
    delete_all_files_in_directory(clip_path)
    delete_all_files_in_directory(image_path)
    delete_all_files_in_directory(video_path)


def parse_video():
    print(f'YouTube video Edit START AT: {datetime.today()}\n')
    # download_list()
    # video_to_audio()
    # audio_to_text_model()
    # divide_video()
    # get_keyword_category_list()
    # upload_s3()
    # delete_all_files()


if __name__ == '__main__':
    # download_list()
    # video_to_audio()
    # audio_to_text_model()
    # divide_video()
    # get_keyword_category_list()
    # upload_s3()
    delete_all_files()
    #
    # # schedule.every(5).seconds.do(parse_video)
    # schedule.every().day.at("00:30").do(parse_video)  # 매일 10:30에
    #
    # while True:
    #     schedule.run_pending()
    #     time.sleep(1)

    # download_video("https://www.youtube.com/watch?v=xrQ1vxS7bRo&ab_channel=NATV%EA%B5%AD%ED%9A%8C%EB%B0%A9%EC%86%A1")
    # summary_script("./whisper/script/민주당 조수진 사퇴 강북을에 한민수 대변인 전략공천! (24322)  인명진 전 자유한국당 비대위원장  정치한수  국회라이브1.txt")
