FROM python:3.10

WORKDIR /app

COPY ./README.md /app/README.md
COPY ./requirements.txt /app/requirements.txt
# dev-file not used in image, just so setup.py do not fail 
COPY ./requirements.dev.txt /app/requirements.dev.txt
COPY ./setup.py /app/setup.py

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./src/yadiskapi /app/src/yadiskapi

RUN pip install -e /app --no-cache-dir

CMD ["sh", "-c", "python /app/src/yadiskapi/main.py && uvicorn src.yadiskapi.main:app --host 0.0.0.0 --port 80 --loop=uvloop --proxy-headers"]
