from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import text
import database, models
from database import db_manager
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

origins = [
    'http://localhost:5173' #The React Server
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods = ['*'],
    allow_headers = ['*'],
)


# models.Base.metadata.create_all(bind=database.engine) #Look at all the models.py, create if don't already exist

def get_db():
    try:
        yield from db_manager.get_db_session()
    except HTTPException as he:
        raise he
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        
        
@app.get('/users/{user_id}')
def get_user(user_id: int, db: Session = Depends(get_db)):
    result = db.execute(
        text('SELECT * FROM users WHERE id = :id'), {'id': user_id}
        #Following could cause SQL Injection attacks
        # f'SELECT * FROM user WHERE id={user_id}'
    )
    
    users = [dict(row._mapping) for row in result.fetchall()]
    
    if users:
        return users
    else:
        return {"error": "user not found"}
    
class Query(BaseModel):
    query: str
    
@app.post('/query')
def handle_query(data: Query, db: Session = Depends(get_db)):
    
    try:
        result = db.execute(text(data.query))
        
        results = [dict(row._mapping) for row in result.fetchall()]
        return {"query": str(data.query), "result": str(results)}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Query error: {str(e)}")
        
        
    
@app.get("/test-db")
def test_db(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "✅ Database connection successful!"}
    except Exception as e:
        return {"error": str(e)}
        
        

class Database(BaseModel):
    name: str | None
    url: str | None
    
@app.post('/database/connect')
def connect_database(data: Database):
    """
    Accept database connection data and store it for further use
    """
    global current_database_connection
    
    try:
        # Validate the database name
        valid_databases = ["PostgreSQL", "MySQL", "MongoDB"]
        if data.name not in valid_databases:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid database type. Must be one of: {', '.join(valid_databases)}"
            )
        
        if not data.url or data.url.strip() == "":
            raise HTTPException(status_code=400, detail="Database URL cannot be empty")
        
        
        # current_database_connection = data
        db_manager.connect(data.url, data.name)
        
        return {
            "status": "success",
            "message": f"Successfully connected to {data.name}",
            "data": {
                "name": data.name,
                "url": data.url
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Server error: {str(e)}")
    
@app.post('/database/disconnect')
def disconnect_database(data: Database):
    db_manager.disconnect()
    
    return {
        "status": "success",
        "message": f"Successfully disconnected from {data.name}",
        "data": {
                "name": data.name,
                "url": data.url
            }
    }
    
@app.get('/database')
def get_current_database():
    """
    Retrieve the current database connection info
    """
    if current_database_connection is None:
        raise HTTPException(status_code=404, detail="No database connection found")
    
    return {
        "status": "success",
        "data": {
            "name": current_database_connection.name,
            "url": current_database_connection.url
        }
    }
    

@app.get('/')
def read_root():
    print(current_database_connection)
    return {'message': 'Hello From FastAPI and PostgreSQL'}