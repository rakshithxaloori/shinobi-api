# pull the official base image
FROM public.ecr.aws/g7q8g9j4/python_3.9:latest

# set work directory
WORKDIR /usr/src/app

###########################
# set environment variables
ARG SECRET_KEY
ENV SECRET_KEY "$SECRET_KEY"
ARG RDS_USERNAME
ENV RDS_USERNAME "$RDS_USERNAME"
ARG RDS_PASSWORD
ENV RDS_PASSWORD "$RDS_PASSWORD"
ARG RDS_HOSTNAME
ENV RDS_HOSTNAME "$RDS_HOSTNAME"
ARG INSTAGRAM_CLIENT_ID
ENV INSTAGRAM_CLIENT_ID "$INSTAGRAM_CLIENT_ID"
ARG INSTAGRAM_CLIENT_SECRET
ENV INSTAGRAM_CLIENT_SECRET "$INSTAGRAM_CLIENT_SECRET"
ARG TWITCH_CLIENT_ID
ENV TWITCH_CLIENT_ID "$TWITCH_CLIENT_ID"
ARG TWITCH_CLIENT_SECRET
ENV TWITCH_CLIENT_SECRET "$TWITCH_CLIENT_SECRET"
ARG GOOGLE_EXPO_GO_APP_CLIENT_ID
ENV GOOGLE_EXPO_GO_APP_CLIENT_ID "$GOOGLE_EXPO_GO_APP_CLIENT_ID"
ARG GOOGLE_ANDROID_APP_CLIENT_ID
ENV GOOGLE_ANDROID_APP_CLIENT_ID "$GOOGLE_ANDROID_APP_CLIENT_ID"
ARG ROLLBAR_ACCESS_TOKEN
ENV ROLLBAR_ACCESS_TOKEN "$ROLLBAR_ACCESS_TOKEN"
ARG RIOT_API_KEY
ENV RIOT_API_KEY "$RIOT_API_KEY"

ARG RDS_DB_NAME
ENV RDS_DB_NAME "$RDS_DB_NAME"
ARG RDS_PORT
ENV RDS_PORT "$RDS_PORT"
ARG RIOT_LOL_RATE_LIMIT_1
ENV RIOT_LOL_RATE_LIMIT_1 "$RIOT_LOL_RATE_LIMIT_1"
ARG RIOT_LOL_RATE_PERIOD_1
ENV RIOT_LOL_RATE_PERIOD_1 "$RIOT_LOL_RATE_PERIOD_1"
ARG RIOT_LOL_RATE_LIMIT_2
ENV RIOT_LOL_RATE_LIMIT_2 "$RIOT_LOL_RATE_LIMIT_2"
ARG RIOT_LOL_RATE_PERIOD_2
ENV RIOT_LOL_RATE_PERIOD_2 "$RIOT_LOL_RATE_PERIOD_2"
ARG CI_CD_STAGE
ENV CI_CD_STAGE "$CI_CD_STAGE"
ARG REDIS_URL
ENV REDIS_URL "$REDIS_URL"
ARG OAUTH_REDIRECT_URI
ENV OAUTH_REDIRECT_URI "$OAUTH_REDIRECT_URI"


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip3 install --upgrade pip
COPY requirements.txt /usr/src/app/
RUN pip3 install -r requirements.txt

# copy project
COPY . /usr/src/app/
# celery -A proeliumx worker -l INFO --uid=nobody --gid=nogroup -Q celery
CMD ["celery", "-A", "proeliumx", "worker", "-l", "INFO", "--uid=nobody", "--gid=nogroup", "-Q", "celery"]
