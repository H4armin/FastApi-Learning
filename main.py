from fastapi import FastAPI
import json

app = FastAPI();

def getData():
    with open('patients.json', 'r') as f:
        data = json.load(f)
    return data

@app.get("/")
def hello():
    return {"message": "Hello World"};

@app.get("/patients")
def patients():
    data = getData();
    return data;