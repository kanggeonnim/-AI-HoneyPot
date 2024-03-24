class videoInfo(object):
    def __init__(self, video_title, video_id, tumblr_url):
        self.video_title = video_title
        self.video_id = video_id
        self.tumblr_url = tumblr_url

    def __str__(self):
        return f"{self.video_title} {self.video_id} {self.tumblr_url}"
