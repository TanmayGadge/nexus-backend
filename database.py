# database.py

from sqlalchemy import create_engine, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from fastapi import HTTPException
import os
from dotenv import load_dotenv


Base = declarative_base()

class DatabaseManager:
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self.current_url = None
        self.current_name = None
        
        
        # load_dotenv()
        # initial_url = os.getenv('SQLALCHEMY_DATABASE_URL')
        # if initial_url:
        #     print(f"Found initial database URL, attempting connection...")
        #     try:
        #         # Pass 'models' to register them before create_all
        #         import models 
        #         self.connect(initial_url, "Initial ENV Connection")
        #         print("✅ Successfully connected to initial database.")
        #     except Exception as e:
        #         print(f"⚠️ Failed to connect to initial database from .env: {e}")

    def connect(self, url: str, name: str = "default"):
        """
        Disconnects any existing engine and creates a new one
        with the provided URL.
        """
        # If we are already connected, dispose of the old engine
        if self.engine:
            self.engine.dispose()
            
        try:
            self.engine = create_engine(url)
            self.SessionLocal = sessionmaker(autoflush=False, autocommit=False, bind=self.engine)
            
            with self.SessionLocal() as db:
                db.execute(text("SELECT 1"))
            
            
            self.current_url = url
            self.current_name = name
            print(f"Successfully connected to: {name}")
            
        except Exception as e:
            # If connection fails, reset everything
            self.engine = None
            self.SessionLocal = None
            self.current_url = None
            self.current_name = None
            print(f"Failed to connect: {e}")
            # Re-raise the error so the API endpoint can catch it
            raise e


    def discoonect(self, name: str = "default"):
        """
        Disconnects the current engine and resets the connection details.
        """
        self.engine.dispose()
        self.engine = None
        self.SessionLocal = None
        self.current_url = None
        self.current_name = None

    def get_db_session(self):
        """
        A generator function to be used as a FastAPI dependency.
        """
        if not self.SessionLocal:
            raise HTTPException(
                status_code=503, # Service Unavailable
                detail="Database is not connected. Please configure via the /database endpoint."
            )
        
        db = self.SessionLocal()
        try:
            yield db
        finally:
            db.close()

# Create a single, global instance of the manager
# This is what your app will import and use
db_manager = DatabaseManager()