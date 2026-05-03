from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Optional, List, Literal, Annotated
import json
import pickle
import pandas as pd

app = FastAPI()


# Import the ML model
with open("model.pkl", "rb") as f:
    model = pickle.load(f)


tier_1_cities = ["Mumbai", "Delhi", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune"]
tier_2_cities = [
    "Jaipur",
    "Chandigarh",
    "Indore",
    "Lucknow",
    "Patna",
    "Ranchi",
    "Visakhapatnam",
    "Coimbatore",
    "Bhopal",
    "Nagpur",
    "Vadodara",
    "Surat",
    "Rajkot",
    "Jodhpur",
    "Raipur",
    "Amritsar",
    "Varanasi",
    "Agra",
    "Dehradun",
    "Mysore",
    "Jabalpur",
    "Guwahati",
    "Thiruvananthapuram",
    "Ludhiana",
    "Nashik",
    "Allahabad",
    "Udaipur",
    "Aurangabad",
    "Hubli",
    "Belgaum",
    "Salem",
    "Vijayawada",
    "Tiruchirappalli",
    "Bhavnagar",
    "Gwalior",
    "Dhanbad",
    "Bareilly",
    "Aligarh",
    "Gaya",
    "Kozhikode",
    "Warangal",
    "Kolhapur",
    "Bilaspur",
    "Jalandhar",
    "Noida",
    "Guntur",
    "Asansol",
    "Siliguri",
]


class UserInput(BaseModel):
    age: Annotated[int, Field(..., gt=0, lt=120, description="Age of the user")]
    weight: Annotated[float, Field(..., gt=0, description="Weight of the user")]
    height: Annotated[
        float, Field(..., gt=0, lt=2.5, description="Height of the user")
    ]
    income_lpa: Annotated[
        float, Field(..., gt=0, description="Annual salary of the user in lpa")
    ]
    smoker: Annotated[bool, Field(..., description="Is user a smoker")]
    city: Annotated[str, Field(..., description="The city that the user belongs to")]
    occupation: Annotated[
        Literal[
            "retired",
            "freelancer",
            "student",
            "government_job",
            "business_owner",
            "unemployed",
            "private_job",
        ],
        Field(..., description="Occupation of the user"),
    ]

    @computed_field
    @property
    def bmi(self) -> float:
        return self.weight / (self.height**2)

    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        if self.smoker and self.bmi > 30:
            return "high"
        elif self.smoker or self.bmi > 27:
            return "medium"
        else:
            return "low"

    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 25:
            return "young"
        elif self.age < 45:
            return "adult"
        elif self.age < 60:
            return "middle_aged"
        return "senior"

    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3


class Patient(BaseModel):
    id: Annotated[str, Field(..., description="The unique identifier of the patient")]
    name: Annotated[str, Field(..., description="The name of the patient")]
    city: Annotated[str, Field(..., description="The city where the patient resides")]
    age: Annotated[int, Field(..., gt=0, description="The age of the patient")]
    gender: Annotated[
        Literal["male", "female"], Field(..., description="The gender of the patient")
    ]
    weight: Annotated[
        float, Field(..., gt=0, description="The weight of the patient inkg")
    ]
    height: Annotated[
        float, Field(..., gt=0, description="The height of the patient in meters")
    ]

    @field_validator("id")
    @classmethod
    def validate_id(cls, value):
        if not value.startswith("P"):
            raise ValueError("Patient ID must start with 'P'")
        return value

    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height**2), 2)

    @computed_field
    @property
    def verdict(self) -> str:
        bmi_value = self.bmi
        if bmi_value < 18.5:
            return "Underweight"
        elif 18.5 <= bmi_value < 25:
            return "Normal weight"
        elif 25 <= bmi_value < 30:
            return "Overweight"
        else:
            return "Obese"


class UpdatePatient(BaseModel):
    name: Optional[str] = Field(None, description="The name of the patient")
    city: Optional[str] = Field(None, description="The city where the patient resides")
    age: Optional[int] = Field(None, gt=0, description="The age of the patient")
    gender: Optional[Literal["male", "female"]] = Field(
        None, description="The gender of the patient"
    )
    weight: Optional[float] = Field(
        None, gt=0, description="The weight of the patient in kg"
    )
    height: Optional[float] = Field(
        None, gt=0, description="The height of the patient in meters"
    )


# Utility function to load patient data from JSON file
def getData():
    with open("patients.json", "r") as f:
        data = json.load(f)
    return data



@app.post("/predict")
def predict_premium(data: UserInput):
    input_df = pd.DataFrame(
        [
            {
                "bmi": data.bmi,
                "age_group": data.age_group,
                "lifestyle_risk": data.lifestyle_risk,
                "city_tier": data.city_tier,
                "income_lpa": data.income_lpa,
                "occupation": data.occupation,
            }
        ]
    )

    prediction = model.predict(input_df)[0]

    return JSONResponse(status_code=200, content={"predicted_category": prediction})

# Root endpoint: Returns a simple hello world message
@app.get("/")
def hello():
    return JSONResponse(status_code=200, content={"message": "Hello World"})


# Endpoint to get details of a specific patient by patient_id
@app.get("/patients/{patient_id}")
def patients(
    patient_id: str = Path(..., description="The ID of the patient to retrieve")
):
    data = getData()
    if patient_id in data:
        return JSONResponse(status_code=200, content=data[patient_id])
    raise HTTPException(status_code=404, detail="Patient not found")


# Endpoint to sort patients by a specified field and order
@app.get("/sort")
def sort_patients(
    sort_by: str = Query(
        ..., description="The field to sort by (e.g., 'weight', 'height' , 'bmi')"
    ),
    order: str = Query("asc", description="The sort order (asc or desc)"),
):
    valid_fields = ["weight", "height", "bmi"]
    if sort_by not in valid_fields:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid sort field. Valid fields are: {', '.join(valid_fields)}",
        )

    if order not in ["asc", "desc"]:
        raise HTTPException(
            status_code=400,
            detail="Invalid sort order. Valid orders are: 'asc' or 'desc'",
        )

    data = getData()
    sort_order = 1 if order == "asc" else -1
    sorted_data = sorted(
        data.values(), key=lambda item: item.get(sort_by, 0), reverse=(sort_order == -1)
    )
    return JSONResponse(status_code=200, content=sorted_data)


@app.post("/create")
def add_patient(patient: Patient):
    data = getData()
    if patient.id in data:
        raise HTTPException(
            status_code=400, detail="Patient with this ID already exists"
        )

    data[patient.id] = patient.model_dump(
        exclude=["id"]
    )  # Convert the Patient model to a dictionary for JSON serialization

    with open("patients.json", "w") as f:
        json.dump(data, f, indent=4)

    return JSONResponse(
        status_code=201,
        content={
            "message": "Patient added successfully",
            "patient": patient.model_dump(),
        },
    )


@app.put("/update/{patient_id}")
def update_patient(patient_id: str, patient_update: UpdatePatient):
    data = getData()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    existing_patient = data[patient_id]

    # Update the existing patient data with the new values
    updated_patient = {
        **existing_patient,
        **patient_update.model_dump(exclude_unset=True),
    }
    updated_patient = Patient(id=patient_id, **updated_patient).model_dump(
        exclude=["id"]
    )

    data[patient_id] = updated_patient

    with open("patients.json", "w") as f:
        json.dump(data, f, indent=4)

    return JSONResponse(
        status_code=200,
        content={"message": "Patient updated successfully", "patient": updated_patient},
    )


@app.delete("/delete/{patient_id}")
def delete_patient(patient_id: str):
    data = getData()
    if patient_id not in data:
        raise HTTPException(status_code=404, detail="Patient not found")

    del data[patient_id]

    with open("patients.json", "w") as f:
        json.dump(data, f, indent=4)

    return JSONResponse(
        status_code=200, content={"message": "Patient deleted successfully"}
    )
