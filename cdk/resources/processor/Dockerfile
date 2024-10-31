FROM --platform=linux/amd64 python:3.9

ENV PYTHONUNBUFFERED=1

ADD requirements.txt .
ADD *.py .

COPY container/ /container/
COPY indexes/ /indexes/

RUN pip install -r requirements.txt

CMD ["python","./main.py"]
