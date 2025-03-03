from pydantic import BaseModel,constr


class Signuprequest(BaseModel):
    username: constr(min_length=3, max_length=50) 
    password: constr(min_length=8)

class Jobpost(BaseModel):
    title: str
    company: str
    location: str
    type: str
    link: str
    description: str