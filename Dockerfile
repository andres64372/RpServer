# pull official base image
FROM python:3.9.7-slim-buster

EXPOSE 8000

# set work directory
WORKDIR /usr/src/app

COPY . .

# install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc g++ musl-dev libpq-dev

# install python dependencies
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements/requirements.txt 

#CMD ["gunicorn","--bind","0.0.0.0:8000","main:app"]
CMD ["python","main.py"]
