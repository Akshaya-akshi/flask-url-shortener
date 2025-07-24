# app/db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base

engine = create_engine("sqlite:///shortener.db")
SessionLocal = sessionmaker(bind=engine)

# Create the tables if they don't exist
Base.metadata.create_all(bind=engine)
