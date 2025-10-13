from fastapi import FastAPI, Depends
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy import text
import database, models
from fastapi.middleware.cors import CORSMiddleware

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


models.Base.metadata.create_all(bind=database.engine) #Look at all the models, create if don't already exist

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
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
    

        
@app.get('/')
def read_root():
    return {'message': 'Hello From FastAPI and PostgreSQL'}