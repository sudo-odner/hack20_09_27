FROM python:3.11

WORKDIR /opt/web/

COPY . /opt/web/

ENV DOCKER_CONTAINER=1

COPY requirements.txt ./

RUN  pip install --upgrade pip \
    && pip install -r requirements.txt

CMD ["python", "main.py"]