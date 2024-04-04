import json
import mysql.connector

from app.config.config import settings
from ai_video.s3 import connect_to_mysql


def find_bills():
    try:
        cursor = connection.cursor(buffered=True)
        cursor.execute("SELECT text_body, summary FROM bill WHERE summary IS NOT NULL")
        result = cursor.fetchall()
        if result:
            return result
        else:
            print("No record found with the given video name.")
            return None
    except mysql.connector.Error as e:
        print(f"Error finding id by video name: {e}")
        return None


def get_data():
    connection = connect_to_mysql()
    bill_list = find_bills()

    with open('train.jsonl', "a", encoding="utf-8") as file:
        for bill in bill_list:
            file.write('''{"messages":[{ "role": "system", "content": "시스템 프롬프트 입력" },{ "role": "user", "content":'''
                       + json.dumps(bill[0], indent=4, ensure_ascii=False)
                       + '''},{ "role": "assistant", "content": '''
                       + json.dumps(bill[1], indent=4, ensure_ascii=False)
                       + '''}] }''' + '\n')

    with open('train.jsonl', 'r', encoding='utf-8') as config_file:
        for line in config_file:
            print(line)


def fine_tuning():
    from openai import OpenAI
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    client.files.create(
        file=open("train.jsonl", "rb"),
        purpose="fine-tune"
    )


if __name__ == '__main__':
    # get_data()
    fine_tuning()
