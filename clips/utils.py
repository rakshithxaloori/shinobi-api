import boto3


from django.conf import settings


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


default_mediaconvert_job_settings = {
    "Inputs": [
        {
            "TimecodeSource": "ZEROBASED",
            "VideoSelector": {},
            "AudioSelectors": {"Audio Selector 1": {"DefaultSelection": "DEFAULT"}},
        }
    ],
    "OutputGroups": [
        {
            "Name": "File Group",
            "OutputGroupSettings": {
                "Type": "FILE_GROUP_SETTINGS",
                "FileGroupSettings": {},
            },
            "Outputs": [
                {
                    "VideoDescription": {
                        "CodecSettings": {
                            "Codec": "H_264",
                            "H264Settings": {
                                "RateControlMode": "QVBR",
                                "SceneChangeDetect": "TRANSITION_DETECTION",
                                "MaxBitrate": 1000000,
                            },
                        }
                    },
                    "AudioDescriptions": [
                        {
                            "CodecSettings": {
                                "Codec": "AAC",
                                "AacSettings": {
                                    "Bitrate": 96000,
                                    "CodingMode": "CODING_MODE_2_0",
                                    "SampleRate": 48000,
                                },
                            }
                        }
                    ],
                    "ContainerSettings": {"Container": "MP4", "Mp4Settings": {}},
                    "NameModifier": "-compressed",
                }
            ],
        }
    ],
    "TimecodeConfig": {"Source": "ZEROBASED"},
}
