import json
import mysql.connector

from youtube.s3 import connect_to_mysql


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


if __name__ == '__main__':
    connection = connect_to_mysql()
    bill_list = find_bills()
    for bill in bill_list:
        with open('train.jsonl', "a", encoding="utf-8") as file:
            data = '{"prompt": "' + bill[0] + '", "completion": "' + bill[1] + '"}\n'
            json.dump(data, file, indent=4, ensure_ascii=False)
