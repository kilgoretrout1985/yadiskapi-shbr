```
python3 -m venv .env && \
source .env/bin/activate && \
pip install -U pip && \
pip install -e .[dev]
```

Run `tox` command to check your project setup. Everything should be green at this 
point.

```
cd src/yadiskapi && uvicorn main:app --reload
```
