# https://www.youtube.com/watch?v=vj0NkOpgQKA&ab_channel=SSAFYLive4_2
from pytube import YouTube

video_url = 'https://www.youtube.com/watch?v=vj0NkOpgQKA&ab_channel=SSAFYLive4_2'
yt = YouTube(video_url)

print(yt)

try:
    yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download()
except Exception as e:
    print(e)
    print("No video: " + video_url)
