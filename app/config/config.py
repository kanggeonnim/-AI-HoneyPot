import os, json
from pathlib import Path


class Settings:
    BASE_DIR = Path(__file__).resolve().parent.parent
    CONFIG_SECRET_DIR = os.path.join(BASE_DIR, "env")
    CONFIG_SECRET_COMMON_FILE = os.path.join(CONFIG_SECRET_DIR, "setting_local.json")

    config_secret_common = json.loads(open(CONFIG_SECRET_COMMON_FILE, encoding='utf-8').read())

    OPENAI_API_KEY: str = config_secret_common["OPENAI_API_KEY"]
    YOUTUBE_API_KEY: str = config_secret_common["YOUTUBE_API_KEY"]
    GPT_PROMPT_BILL: str = config_secret_common["GPT_PROMPT_BILL"]
    GPT_PROMPT_ISSUE: str = config_secret_common["GPT_PROMPT_ISSUE"]
    GPT_PROMPT_KEYWORD: str = config_secret_common["GPT_PROMPT_KEYWORD"]
    VIDEO_FILE_PATH: str = config_secret_common["video_file_path"]
    AUDIO_FILE_PATH: str = config_secret_common["audio_file_path"]
    SCRIPT_FILE_PATH: str = config_secret_common["script_file_path"]
    CLIP_FILE_PATH: str = config_secret_common["clip_file_path"]
    IMAGE_FILE_PATH: str = config_secret_common["image_file_path"]
    AWS_ACCESS_KEY_ID: str = config_secret_common["AWS_ACCESS_KEY_ID"]
    AWS_SECRET_ACCESS_KEY: str = config_secret_common["AWS_SECRET_ACCESS_KEY"]
    AWS_DEFAULT_REGION: str = config_secret_common["AWS_DEFAULT_REGION"]
    DB_HOST: str = config_secret_common["DB_HOST"]
    DB_USER: str = config_secret_common["DB_USER"]
    DB_PASSWORD: str = config_secret_common["DB_PASSWORD"]
    DB_DATABASE: str = config_secret_common["DB_DATABASE"]
    AWS_CLOUD_FRONT: str = config_secret_common["AWS_CLOUD_FRONT"]
    DB_PORT: str = config_secret_common["DB_PORT"]
    CATEGORY_LIST: str = config_secret_common["CATEGORY_LIST"]


settings = Settings()
