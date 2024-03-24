import view_youtube_list
import os
import whisperx

from moviepy.video.io.VideoFileClip import VideoFileClip
from pytube import YouTube
from app.config.config import settings

os.environ['PATH'] += os.pathsep + 'C:\Program Files\\ffmpeg-6.1.1-full_build-shared\\bin'

video_path = settings.VIDEO_FILE_PATH
audio_path = settings.AUDIO_FILE_PATH
script_path = settings.SCRIPT_FILE_PATH


def download_list():
    youtube_list = view_youtube_list.get_youtube_list()
    for l in youtube_list:
        download_video(l)
    print(youtube_list)


def download_video(path):
    video_url = 'https://www.youtube.com/watch?v=' + path
    yt = YouTube(video_url)
    try:
        t = (yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()
             .download(video_path))

    except Exception as e:
        print(e)
        print("No video: " + video_url)


def video_to_audio():
    dir_list = os.listdir(video_path)
    for path in dir_list:
        if path.endswith('.mp4'):
            # 특수문자제거
            # save_path = re.sub(r"[^.\uAC00-\uD7A30-9a-zA-Z\s]", "", path)
            video = VideoFileClip(video_path + path)
            video.audio.write_audiofile(audio_path + path[:-4] + ".mp3")


def audio_to_text_model():
    dir_list = os.listdir(audio_path)
    for path in dir_list:
        print(path)
        device = "cuda"
        audio_file = "./whisper/audio/육아휴직 중 해외 여행 부정 수급일까 shorts.mp3"  # audio_path + path
        # audio_file = audio_path + path
        batch_size = 16  # reduce if low on GPU mem
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
        break


if __name__ == '__main__':
    # download_list()
    # video_to_audio()
    audio_to_text_model()
