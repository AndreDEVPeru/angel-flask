from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

username = "postgres"
password = "SfoAX6AWPuqXzDxFYPp3"
host = "database-1.cwhnlj9dcl1p.us-east-1.rds.amazonaws.com"
port = "5432"
database = "postgres"  # Replace with your actual database name

DATABASE_URL = f"postgresql://{username}:{password}@{host}:{port}/{database}"

engine = create_engine(
    DATABASE_URL, connect_args={'check_same_thread': True}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
