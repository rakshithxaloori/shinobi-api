import boto3


from django.conf import settings


VIDEO_MAX_SIZE_IN_BYTES = 500 * 1000 * 1000  # 500 MB


if settings.CI_CD_STAGE == "testing" or settings.CI_CD_STAGE == "production":
    s3_client = boto3.client(
        service_name="s3",
        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME,
    )
else:
    s3_client = None

if settings.CI_CD_STAGE == "testing" or settings.CI_CD_STAGE == "production":
    sns_client = boto3.client(
        service_name="sns",
        aws_access_key_id=settings.AWS_SNS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SNS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_SNS_REGION_NAME,
    )
else:
    sns_client = None
