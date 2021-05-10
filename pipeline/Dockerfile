FROM public.ecr.aws/sam/build-python3.8

USER root

COPY . /var/task

RUN pip3 install -r /var/task/src/requirements.txt -r /var/task/src/requirements-dev.txt
