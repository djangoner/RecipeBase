FROM python:3.11-slim-buster
WORKDIR /app
COPY Pipfile .
COPY Pipfile.lock .
#RUN apt-get update && apt-get install -y gcc ffmpeg
#RUN apt-get update && apt-get install -y git
RUN pip install --no-cache-dir pipenv
RUN pipenv install --system
#CMD ["daphne", "-p 8080", "-b", "0.0.0.0", "FurnitureReport.asgi:application"]
#CMD ["gunicorn", "-w 4", "-b", "0.0.0.0:8080", "FurnitureReport.wsgi"]
CMD python3 manage.py runserver 0.0.0.0:8080
