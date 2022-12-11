FROM python:3.8-alpine
WORKDIR /app
COPY mqtt_listener .
RUN pip install -r requirements.txt

CMD ["python", "main.py"]