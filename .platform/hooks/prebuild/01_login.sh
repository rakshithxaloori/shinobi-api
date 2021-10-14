### 01login.sh
#!/bin/bash
ECR_USER=/opt/elasticbeanstalk/bin/get-config environment -k ECR_USER
ECR_PASSWD=/opt/elasticbeanstalk/bin/get-config environment -k ECR_PASSWD
docker login -u $ECR_USER -p $ECR_PASSWD
