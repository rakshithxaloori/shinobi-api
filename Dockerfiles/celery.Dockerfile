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
ARG AWS_S3_ACCESS_KEY_ID
ENV AWS_S3_ACCESS_KEY_ID "$AWS_S3_ACCESS_KEY_ID"
ARG AWS_S3_SECRET_ACCESS_KEY
ENV AWS_S3_SECRET_ACCESS_KEY "$AWS_S3_SECRET_ACCESS_KEY"
ARG AWS_STORAGE_BUCKET_NAME
ENV AWS_STORAGE_BUCKET_NAME "$AWS_STORAGE_BUCKET_NAME"
ARG AWS_SNS_ACCESS_KEY_ID
ENV AWS_SNS_ACCESS_KEY_ID "$AWS_SNS_ACCESS_KEY_ID"
ARG AWS_SNS_SECRET_ACCESS_KEY
ENV AWS_SNS_SECRET_ACCESS_KEY "$AWS_SNS_SECRET_ACCESS_KEY"
ARG AWS_SNS_TOPIC_ARN
ENV AWS_SNS_TOPIC_ARN "$AWS_SNS_TOPIC_ARN"
ARG ADMIN_URL
ENV ADMIN_URL "$ADMIN_URL"
ARG AWS_MEDIACONVERT_ACCESS_KEY_ID
ENV AWS_MEDIACONVERT_ACCESS_KEY_ID "$AWS_MEDIACONVERT_ACCESS_KEY_ID"
ARG AWS_MEDIACONVERT_SECRET_ACCESS_KEY
ENV AWS_MEDIACONVERT_SECRET_ACCESS_KEY "$AWS_MEDIACONVERT_SECRET_ACCESS_KEY"
ARG AWS_MEDIACONVERT_JOB_ROLE
ENV AWS_MEDIACONVERT_JOB_ROLE "$AWS_MEDIACONVERT_JOB_ROLE"
ARG GOOGLE_RECAPTCHA_SECRET_KEY
ENV GOOGLE_RECAPTCHA_SECRET_KEY "$GOOGLE_RECAPTCHA_SECRET_KEY"

ARG RDS_DB_NAME
ENV RDS_DB_NAME "$RDS_DB_NAME"
ARG RDS_PORT
ENV RDS_PORT "$RDS_PORT"
ARG CI_CD_STAGE
ENV CI_CD_STAGE "$CI_CD_STAGE"
ARG REDIS_URL
ENV REDIS_URL "$REDIS_URL"
ARG OAUTH_REDIRECT_URI
ENV OAUTH_REDIRECT_URI "$OAUTH_REDIRECT_URI"
ARG AWS_S3_REGION_NAME
ENV AWS_S3_REGION_NAME "$AWS_S3_REGION_NAME"
ARG AWS_SNS_REGION_NAME
ENV AWS_SNS_REGION_NAME "$AWS_SNS_REGION_NAME"
ARG AWS_MEDIACONVERT_REGION_NAME
ENV AWS_MEDIACONVERT_REGION_NAME "$AWS_MEDIACONVERT_REGION_NAME"
ARG AWS_S3_CUSTOM_DOMAIN
ENV AWS_S3_CUSTOM_DOMAIN "$AWS_S3_CUSTOM_DOMAIN"


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install dependencies
RUN pip3 install --upgrade pip
COPY requirements.txt /usr/src/app/
RUN pip3 install -r requirements.txt

# copy project
COPY . /usr/src/app/
# celery -A shinobi worker -l INFO --uid=nobody --gid=nogroup -Q celery
CMD ["celery", "-A", "shinobi", "worker", "-l", "INFO", "--uid=nobody", "--gid=nogroup", "-Q", "celery"]
