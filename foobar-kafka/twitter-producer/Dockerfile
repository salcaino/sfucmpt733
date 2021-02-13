FROM python:3.8

WORKDIR /app

ADD ./requirements.txt ./
RUN pip install -r requirements.txt

ADD ./ ./
CMD ["python3", "-u","twitter_api.py"]