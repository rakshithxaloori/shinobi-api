# pull the official base image
FROM public.ecr.aws/g7q8g9j4/python_3.9:latest

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip3 install --upgrade pip
COPY requirements.txt /usr/src/app/
RUN pip3 install -r requirements.txt

# copy project
COPY . /usr/src/app/
# celery -A proeliumx worker -l INFO --uid=nobody --gid=nogroup -Q lol --concurrency 1
CMD ["celery", "-A", "proeliumx", "worker", "-l", "INFO", "--uid=nobody", "--gid=nogroup", "-Q", "lol", "--concurrency", "1"]
