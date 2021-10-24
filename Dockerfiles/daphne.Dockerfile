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
RUN python manage.py migrate --noinput &&
RUN python manage.py collectstatic --noinput &&
# daphne -b 0.0.0.0 -p 8000 proeliumx.asgi:application
EXPOSE 8000
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "proeliumx.asgi:application"]
# CMD ["python", "manage.py", "migrate", "--noinput", "&&", "python", "manage.py", "collectstatic", "--noinput", "&&", "daphne", "-b", "0.0.0.0", "-p", "8000", "proeliumx.asgi:application"]
