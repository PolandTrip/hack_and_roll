ToasterChan's Backend

1. Install packages

```
pip install -r requirements.txt
```

2. Activate virtual environment
```
.\venv\Scripts\activate
```

3. Run the backend
```
uvicorn main:app --host 127.0.0.1 --port 8080 --reload
```