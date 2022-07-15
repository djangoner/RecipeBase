FROM python:3.8-slim-buster
COPY requirements.txt app/
WORKDIR /app
#RUN apt-get update && apt-get install -y gcc ffmpeg
#RUN apt-get update && apt-get install -y git
RUN pip3 install --no-cache-dir -r requirements.txt
#CMD ["daphne", "-p 8080", "-b", "0.0.0.0", "FurnitureReport.asgi:application"]
#CMD ["gunicorn", "-w 4", "-b", "0.0.0.0:8080", "FurnitureReport.wsgi"]
CMD python3 manage.py runserver 0.0.0.0:8080
