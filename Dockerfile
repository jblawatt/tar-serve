FROM python:3.7-alpine

RUN apk update && pip install gunicorn
ADD app.py .
ADD bottle.py .
ADD views .

EXPOSE 8080

ENTRYPOINT ["gunicorn", "-b", "0.00.0:8080", "app:app"]