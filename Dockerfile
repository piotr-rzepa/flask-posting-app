ARG VERSION=3.11.1

FROM python:${VERSION}-slim-buster

WORKDIR /app

ENV FLASK_APP=app.py

ENV FLASK_RUN_HOST=0.0.0.0

EXPOSE 5000

COPY src/ .

COPY requirements.txt .

RUN pip install -r requirements.txt

RUN rm -f requirements*.txt

ENTRYPOINT ["flask", "run"]
