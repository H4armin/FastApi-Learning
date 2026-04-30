from pydantic import BaseModel, Field, EmailStr, AnyUrl, ValidationError ,field_validator , model_validator , computed_field
from typing import List, Optional , Literal

class Employee(BaseModel):
    empId: int = Field(gt=0, lt=100)
    empName: str = Field(min_length=3, max_length=50)
    empPortfolio: AnyUrl
    empEmail: EmailStr
    empAge: int
    empSkills: List[str]
    empMarried: Optional[bool] = None
    empRole:Literal['Frontend Dev', 'Backend Dev']
    empTotalLeave: float 
    empAppliedLeave: int

    @field_validator('empAge' , mode='before')
    @classmethod
    def validate_emp_age(cls, value):
        if value < 18 or value > 65:
            raise ValueError("empAge must be between 18 and 65")
        return value
    
    @field_validator('empEmail' , mode='after')
    @classmethod
    def validate_emp_email(cls, value):
        validDomain = ['oracle.com', 'ibm.com']
        domainName = value.split('@')[-1]
        if domainName not in validDomain:
            raise ValueError("empEmail domain must be one of the following: oracle.com, ibm.com")
        return value
    
    @model_validator(mode='after')
    def validate_emp_skills(model):
        frontendSkill = {'React', 'Angular'}
        backendSkill = {'Python', 'FastAPI'}

        if model.empRole == 'Frontend Dev' and not frontendSkill.intersection(model.empSkills):
            raise ValueError("Frontend Dev must include at least one of: React, Angular")

        if model.empRole == 'Backend Dev' and not backendSkill.intersection(model.empSkills):
            raise ValueError("Backend Dev must include at least one of: Python, FastAPI")

        return model
    
    @computed_field
    @property
    def empLeaveBalance(self) -> float:
        return self.empTotalLeave - self.empAppliedLeave


def createEmpProfile(employee: Employee):
    if not isinstance(employee, Employee):
        raise TypeError("employee must be an Employee instance")
    return employee.model_dump()


class EmpAddress(BaseModel):
    street: str = Field(min_length=3, max_length=100)
    city: str = Field(min_length=2, max_length=50)
    state: str = Field(min_length=2, max_length=50)
    pincode: str = Field(pattern=r"^\d{6}$")


class EmployeeWithAddress(BaseModel):
    empId: int = Field(gt=0, lt=100)
    empName: str = Field(min_length=3, max_length=50)
    empEmail: EmailStr
    empAddress: EmpAddress


def createEmpAddressProfile(employee: EmployeeWithAddress):
    if not isinstance(employee, EmployeeWithAddress):
        raise TypeError("employee must be an EmployeeWithAddress instance")
    return employee.model_dump()


try:
    emp = Employee(
        empId=1,
        empName="Harsh",
        empPortfolio="https://example.com",
        empEmail="harsh@oracle.com",
        empAge=25,
        empSkills=["Python", "FastAPI"],
        empMarried=False,
        empRole="Backend Dev",
        empTotalLeave=20,
        empAppliedLeave=5
    )
    print(createEmpProfile(emp))
except ValidationError as error:
    print("Validation error while creating employee profile:")
    for err in error.errors():
        print(f"- {err['loc'][0]}: {err['msg']}")
except TypeError as error:
    print(f"Type error: {error}")

try:
    empWithAddress = EmployeeWithAddress(
        empId=2,
        empName="Ravi",
        empEmail="ravi@ibm.com",
        empAddress=EmpAddress(
            street="MG Road",
            city="Bengaluru",
            state="Karnataka",
            pincode="560001"
        )
    )
    print(createEmpAddressProfile(empWithAddress))
except ValidationError as error:
    print("Validation error while creating employee address profile:")
    for err in error.errors():
        print(f"- {err['loc'][0]}: {err['msg']}")
except TypeError as error:
    print(f"Type error: {error}")
