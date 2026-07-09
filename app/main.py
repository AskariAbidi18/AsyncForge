from app.database import Base, engine

# Import all models
from app.models.task import Task

def init_db():
    print("[DB] Creating tables...")
    Base.metadata.create_all(bind=engine)
    print("[DB] Ready.")
