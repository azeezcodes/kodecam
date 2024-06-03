from datetime import date
from decimal import Decimal
from typing import Annotated, Optional
from fastapi import FastAPI, Path, Query
from pydantic import BaseModel

app = FastAPI()

userList = []

class Address(BaseModel):
    street: str
    city: str
    zip: str

class User(BaseModel):
    name: str
    email: str
    address: Address
    
class Report(BaseModel):
    title: str
    content: str

@app.get("/items/")
def basic_Query_Parameters(name: str, category: str, price: Decimal):
    return {
        "name" : name,
        "category" : category,
        "price" : price
    }

@app.get("/search/")
def query_Parameters_Default_values_Optional_field(query: Optional[str] = None, page:Optional[int] = 1 , size:Optional[int] = 10):
    return {f"https://example.com/{query}?page={page}"}


@app.post("/users/")
def request_body_nested_models(user: User):
    userList.append(user)
    return userList

@app.get("/validate/")
def combined_parameters_string_validations(username:Annotated[str,  Query(min_length=6, pattern="^[a-zA-Z0-9_]+$")]):
     return {f"{username} length is more than 6 and contain only text and number was well validated"}
     
     
@app.get("/reports/{report_id}")
def combined_parameters_validations(report: Report, report_id: str = Path(description = "include the report id to get more information"),                                     
                                    start_date: Optional[date] = Query(None, description="The start date of the report in YYYY-MM-DD format"),
                                    end_date: Optional[date] = Query(None, description="The end date of the report in YYYY-MM-DD format"), 
                                    ):
      return {
        "report_id": report_id,
        "start_date": start_date,
        "end_date": end_date,
        "report": report
    }    