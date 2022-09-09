from pydantic import BaseSettings


class Settings(BaseSettings):
    app_title: str = "Yet Another Disk Open API"
    app_description: str = "Вступительное задание в Осеннюю Школу Бэкенд Разработки Яндекса 2022"

    # postgresql+asyncpg://user:[password]@host_or_ip[:port]/database_name
    db_dsn: str = "postgresql+asyncpg://yadiskapi:pass@localhost/yadiskapi"
    db_test_dsn: str = db_dsn + "_test"  # separate db to run tests is `yadiskapi_test` (same user, pass as ^^^)
    db_echo_flag: bool = True  # set True to see generated SQL queries in the console


settings = Settings()
