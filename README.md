# Run and test using virtualenv #

1)  ```
    git clone https://github.com/kilgoretrout1985/yadiskapi-shbr.git && \
    cd ./yadiskapi-shbr/ && \
    python3.10 -m venv .env && \
    source .env/bin/activate && \
    pip install -U pip && \
    pip install -e .[dev]
    ```

2)  Configure Postgres connect dsn by editing `src/yadiskapi/config.py`.

    If you can't or do not want to edit config.py (like storing secrets in 
    a file) - you can change config.py settings at runtime using environment 
    variables, e.g.:
    
    ```
    DB_DSN="postgresql+asyncpg://yadiskapi:pass@localhost/yadiskapi" uvicorn main:app --loop=uvloop
    ```

    This is a single bash line that sets env var `DB_DSN` specifically for 
    current uvicorn-run and than runs it. Same for running tests:

    ```
    DB_TEST_DSN="postgresql+asyncpg://yadiskapi:pass@localhost/yadiskapi_test" pytest
    ```

3)  Run `tox` or `pytest` to test your setup. Everything should be green at this point.
    You can also run `locust` for load testing.

4)  Run web-server with this command:
    ```
    cd src/yadiskapi && python main.py && uvicorn main:app --loop=uvloop
    ```

    `python main.py` is used to create initial db tables before first run. 
    
    Use `python main.py --drop-all` to drop (delete all!) and recreate db in case you need it.

5)  Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive docs.


# Run with docker-compose #

1)  Run:
    ```
    docker-compose up -d
    ```

2)  Open [http://0.0.0.0:80/docs](http://0.0.0.0:80/docs) for interactive docs.


# Run in a docker container using your Postgres #

1)  Build image:
    
    ```
    docker build -t yadiskapi-image .
    ```

2)  Find out your correct Postgres dsn, like:
    
    ```
    postgresql+asyncpg://yadiskapi:pass@172.17.0.1/yadiskapi
    ```

    For standart Docker for Linux, IP-address **of the host** most likely will 
    be 172.17.0.1. The easiest way to get it is `ifconfig docker0`.

2)  Run your image:
    
    ```
    docker run --name yadiskapi -d -p 80:80 \
        -e DB_DSN="postgresql+asyncpg://yadiskapi:pass@172.17.0.1/yadiskapi" \
        --restart unless-stopped yadiskapi-image
    ```

    In case of errors change `-p 80:80` to something like `-p 8080:80` if port 
    80 is already taken by another web-server on your machine.

4)  Open [http://0.0.0.0:80/docs](http://0.0.0.0:80/docs) for interactive docs.


# Run in a docker container using Postgres from docker container #

1)  Build your image:
    
    ```
    docker build -t yadiskapi-image .
    ```

2)  Create a separate docker volume where all Postgres data 
    will be actually stored. So this docker container is persistent between runs.

    ```
    docker volume create yadiskapi-pgdata
    ```

3)  Run standart docker image of Postgres:
    
    ```
    docker run --name yadiskapi-db -d -p 5432:5432 \
        -e POSTGRES_USER=yadiskapi -e POSTGRES_PASSWORD=pass -e POSTGRES_DB=yadiskapi \
        -e PGDATA=/var/lib/postgresql/data \
        -v yadiskapi-pgdata:/var/lib/postgresql/data \
        --restart unless-stopped postgres:14.5
    ```

    If port 5432 is already taken on your machine, change it to something like
    `-p 25432:5432` and supply connect-dsn with corrected port to yadiskapi container
    on the next step.

4)  Run your image:
    
    ```
    docker run --name yadiskapi -d -p 80:80 \
        -e DB_DSN="postgresql+asyncpg://yadiskapi:pass@172.17.0.1/yadiskapi" \
        --restart unless-stopped yadiskapi-image
    ```

    In case of errors change `-p 80:80` to something like `-p 8080:80` if port 
    80 is already taken by another web-server on your machine.

5)  Open [http://0.0.0.0:80/docs](http://0.0.0.0:80/docs) for interactive docs.
