```
python3 -m venv .env && \
source .env/bin/activate && \
pip install -U pip && \
pip install -e .[dev]
```

Run `tox` command to check your project setup. Everything should be green at this 
point.

```
cd src/yadiskapi && python main.py && uvicorn main:app --reload
```

`python main.py` is used to create initial db tables before first run. 

Use `python main.py --drop-all` to drop (delete all!) and recreate db in case you need it.