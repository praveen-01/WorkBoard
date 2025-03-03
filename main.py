from fastapi import FastAPI,HTTPException,status,Depends
from fastapi.security import OAuth2PasswordBearer
from database import engine
from sqlalchemy import text
from models import Signuprequest,Jobpost
import bcrypt
import datetime
import jwt

SECRET_KEY = "samplesecretkey@12345678901"
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def valid_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithms=["HS256"])
        username = payload.get("sub")
        if not username:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
            )
        return username
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

@app.post("/signup")
def register_user(User: Signuprequest):
    user = User.username
    with engine.connect() as connection:
        user_present = connection.execute(text("SELECT * FROM users WHERE username = :user"),{"user":user})
        users = [dict(row) for row in user_present.mappings()]
        if users:
            raise HTTPException(status_code=400, detail="Username already exists.Try different username or try logging in!")
        else:
            hshd_password = bcrypt.hashpw(User.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            insert_user = connection.execute(text("INSERT INTO users (username,password) VALUES (:user,:pass)"),{"user":user,"pass":hshd_password})
            connection.commit()
            return {"message": "User registered successfully"}

@app.post("/login")
def login_user(User: Signuprequest):
    user = User.username
    password = User.password
    with engine.connect() as connection:
        check_auth = connection.execute(text("select * from users where username = :user"),{"user":user})
        users = [dict(row) for row in check_auth.mappings()]
        if not users:
            raise HTTPException(status_code=400, detail="No such user. Try signup!")
        else:
            if not bcrypt.checkpw(password.encode("utf-8"),users[0]["password"].encode("utf-8")):
                raise HTTPException(status_code=400, detail="Invalid password.")
            token_payload = {
                "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=1),
                "sub": user
            }
            token = jwt.encode(token_payload,SECRET_KEY,algorithm="HS256")
            return {"access_token": token, "token_type": "bearer"}
            
@app.post("/post-job")
def post_job(job_data: Jobpost,username: str = Depends(valid_token)):
    params = {
        "title": job_data.title,
        "company": job_data.company,
        "location": job_data.location,
        "type": job_data.type,
        "link": job_data.link,
        "description": job_data.description
        }
    with engine.connect() as connection:
        user_details = connection.execute(text("Select id from users where username = :user"),{"user": username}).fetchone()
        if not user_details:
            raise HTTPException(status_code = 400, detail="Invalid user!")
        params["user_id"]=user_details[0]
        db = connection.execute(text("INSERT INTO JOBS (title,company,location,type,link,description,user_id) VALUES (:title,:company,:location,:type,:link,:description,:user_id)"),params)
        connection.commit()
        return {"message": "job added successfully"}

@app.put("/jobs/{job_id}")
def update_job_record(job_id: int,job_data: Jobpost,username: str = Depends(valid_token)):
    params = {
        "title": job_data.title,
        "company": job_data.company,
        "location": job_data.location,
        "type": job_data.type,
        "link": job_data.link,
        "description": job_data.description
    }
    with engine.connect() as connection:
        user_details = connection.execute(text("Select id from users where username = :user"),{"user": username}).fetchone()
        if not user_details:
            raise HTTPException(status_code = 404, detail="No user found")
        job_user = connection.execute(text("select user_id from jobs where id=:job_id"),{"job_id":job_id}).fetchone()
        if not job_user:
            raise HTTPException(status_code = 404, detail="No job found")
        elif job_user[0]!=user_details[0]:
            raise HTTPException(status_code = 403, detail="Invalid operation. You can only edit jobs posted by you!!")
        params["id"]=job_id
        update_job = connection.execute(text("UPDATE jobs SET title=:title, company=:company, location=:location, type=:type, link=:link, description=:description  WHERE id=:id"),params)
        connection.commit()
        return {"message": "job updated successfully"}

@app.delete("/jobs/{job_id}")
def update_job_record(job_id: int,username: str = Depends(valid_token)):
    with engine.connect() as connection:
        user_details = connection.execute(text("Select id from users where username = :user"),{"user": username}).fetchone()
        if not user_details:
            raise HTTPException(status_code = 404, detail="No user found")
        job_user = connection.execute(text("select user_id from jobs where id=:job_id"),{"job_id":job_id}).fetchone()
        if not job_user:
            raise HTTPException(status_code = 404, detail="No job found")
        elif job_user[0]!=user_details[0]:
            raise HTTPException(status_code = 403, detail="Invalid operation. You can only edit jobs posted by you!!")
        params={"job_id":job_id}
        update_job = connection.execute(text("DELETE FROM jobs WHERE id=:job_id"),params)
        connection.commit()
        return {"message": "job deleted successfully"}

@app.get("/jobs")
def get_all_jobs(title: str | None = None,
                 location: str | None = None,
                 type: str | None=None,
                 limit: int = 10,
                 offset: int = 0):
    
    query_construct = []
    params = {}
    if title:
        query_construct.append("lower(title) like :title")
        title = title.strip('"')
        params["title"]=f"%{title.lower()}%"
    if location:
        query_construct.append("lower(location) like :location")
        location = location.strip('"')
        params["location"]=f"%{location.lower()}%"
    if type:
        query_construct.append("lower(type) like :type")
        type = type.strip('"')
        params["type"]=f"%{type.lower()}%"
    
    query = "SELECT * FROM jobs "
    if query_construct:
        query+="WHERE "+ " AND ".join(query_construct)
    
    query += " ORDER BY created_at,updated_at desc "
    query += " LIMIT :limit OFFSET :offset"
    params["limit"] = limit
    params["offset"] = offset
    
    with engine.connect() as connection:
        result = connection.execute(text(query),params)
        jobs = [dict(row) for row in result.mappings()]
        return jobs
    

@app.get("/jobs/{job_id}")
def get_job_by_id(job_id:int):
    with engine.connect() as connection:
        result = connection.execute(text("Select * from jobs where id= :job_id"),{"job_id": job_id})
        jobs = [dict(row) for row in result.mappings() ]
    if jobs:
        return jobs
    else:
        raise HTTPException(status_code=404, detail="Job not found")
