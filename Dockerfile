FROM ubuntu:latest
LABEL authors="SSAFY"

ENTRYPOINT ["top", "-b"]

#
FROM python:3.10.14

#
WORKDIR /code

#
COPY ./requirements.txt /code/requirements.txt

#
RUN pip install --upgrade -r /code/requirements.txt

#
COPY ./app /code/app

#
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]