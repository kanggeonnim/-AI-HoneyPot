import sched
from apscheduler.schedulers.background import BackgroundScheduler

sched = BackgroundScheduler(timezone='Asia/Seoul')


# 매일 새벽 1시 30분에 스케줄러가 작동, YouTube 영상을 업로드 한다.
@sched.scheduled_job('cron', seconds=5, id='update_youtube_videos')
def job():
    print("Job scheduled")
    raise Exception


def start_image_scheduler():
    sched.start()
