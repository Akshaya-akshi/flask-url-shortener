from app.db import Base, engine
from app.models import URL

Base.metadata.create_all(bind=engine)
print("✅ Database and tables created successfully!")
