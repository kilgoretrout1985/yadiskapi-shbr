FROM python:3.10

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./src/yadiskapi /app/yadiskapi

# For standart Docker for Linux, IP-address of the host will always be 172.17.0.1 
# The easiest way to get it is `ifconfig docker0`.
ENV DB_DSN postgresql+asyncpg://yadiskapi:pass@172.17.0.1/yadiskapi

CMD ["sh", "-c", "uvicorn yadiskapi.main:app --host 0.0.0.0 --port 80 --loop=uvloop --proxy-headers"]

# docker build -t yadiskapiimage .
# docker run -d -p 8080:80 yadiskapiimage