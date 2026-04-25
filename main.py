from fastapi import FastAPI , HTTPException, Path , Query
import json

app = FastAPI();

# Utility function to load patient data from JSON file
def getData():
    with open('patients.json', 'r') as f:
        data = json.load(f)
    return data

# Root endpoint: Returns a simple hello world message
@app.get("/")
def hello():
    return {"message": "Hello World"};

# Endpoint to get details of a specific patient by patient_id
@app.get("/patients/{patient_id}")
def patients(patient_id: str = Path(..., description="The ID of the patient to retrieve")):
    data = getData();
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail="Patient not found")

# Endpoint to sort patients by a specified field and order
@app.get("/sort")
def sort_patients(
    sort_by: str = Query(..., description="The field to sort by (e.g., 'wieght', 'height' , 'bmi')"),
    order: str = Query('asc', description="The sort order (asc or desc)")
):
    valid_fields = ['wieght', 'height', 'bmi'];
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail=f"Invalid sort field. Valid fields are: {', '.join(valid_fields)}")
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail="Invalid sort order. Valid orders are: 'asc' or 'desc'")
    
    data = getData();
    sort_order = 1 if order == 'asc' else -1
    sorted_data = sorted(data.values(), key=lambda item: item.get(sort_by,0), reverse=(sort_order == -1))
    return sorted_data