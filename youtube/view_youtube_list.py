from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime, timedelta
import os
from ai.app.config.config import settings
# YouTube Data API의 API key를 입력합니다.

from videoInfo import videoInfo

youtube_api_key = settings.YOUTUBE_API_KEY


def get_youtube_list():
    # 가져올 채널의 ID를 입력합니다.
    channel_id = 'UCL-WOj1FxKR8Hlzg5tvnWKg'
    #   국회방송NATV

    # YouTube Data API 클라이언트를 빌드합니다.
    youtube = build('youtube', 'v3', developerKey=youtube_api_key)

    beforeVideos = []

    try:
        # 동영상 목록을 가져옵니다.
        request = youtube.search().list(
            part='id,snippet',
            channelId=channel_id,
            order='date',
            type='video',
            maxResults=20
        )
        response = request.execute()
        # print(response)

        videos = list()
        # 동영상 제목과 ID를 출력합니다.
        for item in response['items']:
            video_title = item['snippet']['title']
            published_at = item['snippet']['publishTime'][0:10]
            today = (datetime.today() - timedelta(days=1)).strftime("%Y-%m-%d")
            live_broadcast = item['snippet']['liveBroadcastContent']
            tumblr_url = item['snippet']['thumbnails']['high']
            video_id = item['id']['videoId']

            if (today == published_at and live_broadcast == "none"):
                # if (today != published_at and live_broadcast == "none"):
                videos.append(video_id)
                # print(live_broadcast)
                # print(f'{video_title}\n{video_id}\n{tumblr_url}')
                # print(published_at)
                # print("==============================")
        print(videos)

        if len(videos) == 0:
            raise Exception("No videos found")

        return videos
        # beforeVideos.append(video_title)

        # print(beforeVideos)

    except HttpError as e:
        print(f'An HTTP error {e.resp.status} occurred:\n{e.content}')
