import os
import boto3
import uuid
import json

from django.conf import settings


VIDEO_MAX_SIZE_IN_BYTES = 500 * 1000 * 1000  # 500 MB
VIDEO_FILE_ARGS = [4, 3, 2, 1]
VIDEO_DIMENSIONS = [1080, 720, 480, 360]

AWS_UPLOADS_BUCKET_NAME = settings.AWS_UPLOADS_BUCKET_NAME
AWS_STORAGE_BUCKET_NAME = settings.AWS_STORAGE_BUCKET_NAME


class UPLOAD_TYPE:
    CLIP = "c"
    THUMBNAIL = "t"


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

if settings.CI_CD_STAGE == "testing" or settings.CI_CD_STAGE == "production":
    mediaconvert_client = boto3.client(
        service_name="mediaconvert",
        aws_access_key_id=settings.AWS_MEDIACONVERT_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_MEDIACONVERT_SECRET_ACCESS_KEY,
        region_name=settings.AWS_MEDIACONVERT_REGION_NAME,
    )
    endpoints = mediaconvert_client.describe_endpoints()

    mediaconvert_client = boto3.client(
        service_name="mediaconvert",
        aws_access_key_id=settings.AWS_MEDIACONVERT_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_MEDIACONVERT_SECRET_ACCESS_KEY,
        region_name=settings.AWS_MEDIACONVERT_REGION_NAME,
        endpoint_url=endpoints["Endpoints"][0]["Url"],
        verify=False,
    )
else:
    mediaconvert_client = None


def create_presigned_s3_url(file_size, file_path, upload_type):
    # Toggle bucket based on clip or thumbnail
    if upload_type == UPLOAD_TYPE.CLIP:
        bucket = AWS_UPLOADS_BUCKET_NAME
    elif upload_type == UPLOAD_TYPE.THUMBNAIL:
        bucket = AWS_STORAGE_BUCKET_NAME
    else:
        return None

    fields = {
        "Content-Type": "multipart/form-data",
    }

    conditions = [
        ["content-length-range", file_size - 10, file_size + 10],
        {"content-type": "multipart/form-data"},
    ]
    expires_in = 3600

    url = s3_client.generate_presigned_post(
        Bucket=bucket,
        Key=file_path,
        Fields=fields,
        Conditions=conditions,
        ExpiresIn=expires_in,
    )
    return url


def create_job(file_path, height, width):
    sourceS3 = "s3://" + AWS_UPLOADS_BUCKET_NAME + "/" + file_path
    destinationS3 = (
        "s3://" + AWS_STORAGE_BUCKET_NAME + "/" + settings.S3_FILE_CONVERT_PATH_PREFIX
    )
    jobs = []

    jobMetadata = {}
    jobMetadata["assetID"] = str(uuid.uuid4())
    jobMetadata["application"] = "VOD"
    jobMetadata["input"] = sourceS3
    try:
        # Build a list of jobs to run against the input.  Use the settings files in WatchFolder/jobs
        # if any exist.  Otherwise, use the default job.
        jobInput = {}

        # Use Default job settings in the lambda zip file in the current working directory
        if not jobs:

            with open(os.path.join("clips", "job.json")) as json_data:
                jobInput["filename"] = "Default"
                jobInput["settings"] = json.load(json_data)
                jobs.append(jobInput)

        for j in jobs:
            jobSettings = j["settings"]
            jobFilename = j["filename"]

            # Save the name of the settings file in the job userMetadata
            jobMetadata["settings"] = jobFilename

            # Update the job settings with the source video from the S3 event
            jobSettings["Inputs"][0]["FileInput"] = sourceS3

            # Update the job settings with the destination paths for converted videos.  We want to replace the
            # destination bucket of the output paths in the job settings, but keep the rest of the
            # path
            fileDestination = (
                destinationS3 + "/" + os.path.splitext(os.path.basename(file_path))[0]
            )

            for outputGroup in jobSettings["OutputGroups"]:
                if outputGroup["OutputGroupSettings"]["Type"] == "FILE_GROUP_SETTINGS":
                    outputGroup["OutputGroupSettings"]["FileGroupSettings"][
                        "Destination"
                    ] = fileDestination

                for output, dimension_size in zip(
                    outputGroup["Outputs"], VIDEO_DIMENSIONS
                ):
                    if width > height or width == 0 or height == 0:
                        output["VideoDescription"]["Height"] = dimension_size
                    else:
                        output["VideoDescription"]["Width"] = dimension_size

            # Convert the video using AWS Elemental MediaConvert
            job = mediaconvert_client.create_job(
                Role=settings.AWS_MEDIACONVERT_JOB_ROLE,
                UserMetadata=jobMetadata,
                Settings=jobSettings,
            )
            print(job)

    except Exception as e:
        print(e)


print("\n----------------------\n")
print("s3_client", s3_client is not None)
print("sns_client", sns_client is not None)
print("mediaconvert_client", mediaconvert_client is not None)
print("\n----------------------\n")
