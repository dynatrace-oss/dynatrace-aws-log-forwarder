FROM amazon/aws-sam-cli-build-image-python3.8

USER root

COPY . /var/task

RUN pip3 install -r /var/task/src/requirements.txt -r /var/task/src/requirements-dev.txt
