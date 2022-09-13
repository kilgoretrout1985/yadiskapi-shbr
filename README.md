# Using virtualenv #

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

4)  Run web-server with this command:
    ```
    cd src/yadiskapi && python main.py && uvicorn main:app --loop=uvloop
    ```

    `python main.py` is used to create initial db tables before first run. 
    
    Use `python main.py --drop-all` to drop (delete all!) and recreate db in case you need it.

5)  Open [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) for interactive docs.

# In a docker container using your local Postgres #

1) Edit `Dockerfile` for correct Postgres dsn like:

    ```
    ENV DB_DSN postgresql+asyncpg://yadiskapi:pass@172.17.0.1/yadiskapi
    ```

2)  ```
    docker build -t yadiskapiimage .
    docker run -d -p 8080:80 yadiskapiimage
    ```

4) Open [http://0.0.0.0:8080/docs](http://0.0.0.0:8080/docs) for interactive docs.
