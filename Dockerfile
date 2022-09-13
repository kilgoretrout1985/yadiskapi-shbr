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

# For standart Docker for Linux, IP-address of the host will always be 172.17.0.1 
# The easiest way to get it is `ifconfig docker0`.
ENV DB_DSN postgresql+asyncpg://yadiskapi:pass@172.17.0.1/yadiskapi

CMD ["sh", "-c", "python /app/src/yadiskapi/main.py && uvicorn src.yadiskapi.main:app --host 0.0.0.0 --port 80 --loop=uvloop --proxy-headers"]

# docker build -t yadiskapiimage .
# docker run -d -p 8080:80 yadiskapiimage