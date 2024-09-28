FROM python:3.11

WORKDIR /opt/model/

COPY . /opt/model/

COPY requirements.txt ./

RUN  pip install --upgrade pip \
    && pip install -r requirements.txt

CMD ["python", "main.py"]