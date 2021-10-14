### 01login.sh
#!/bin/bash
USER=/opt/elasticbeanstalk/bin/get-config environment -k ECR_USER
PASSWD=/opt/elasticbeanstalk/bin/get-config environment -k ECR_PASSWD
docker login -u $ECR_USER -p $ECR_PASSWD
